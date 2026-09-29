"""Git is an object transport, never a working checkout or executable source."""
from __future__ import annotations

import contextlib
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

from .common import Error, SHA, digest, guarded, require, safe_rel


def repository(value: str, allow_local: bool = False) -> str:
    require(isinstance(value, str) and value and not any(c.isspace() for c in value),
            "SOURCE", "Repository must be a URL without whitespace")
    if re.fullmatch(r"git@[A-Za-z0-9.-]+:[A-Za-z0-9._/-]+", value):
        require(".." not in value.split(":", 1)[1].split("/"), "SOURCE", "Unsafe remote path")
        return value
    parsed = urlsplit(value)
    if allow_local and parsed.scheme == "file":
        require(not parsed.netloc and Path(parsed.path).is_absolute(), "SOURCE", "Use an absolute file URL")
        return value
    require(parsed.scheme in ("https", "ssh") and bool(parsed.hostname) and
            not parsed.password and not parsed.query and not parsed.fragment and
            (parsed.scheme == "ssh" or parsed.username is None) and
            parsed.path not in ("", "/"), "SOURCE", "Use credential-free HTTPS or SSH Git URL")
    return value


@contextlib.contextmanager
def mutex(path: Path):
    require(not path.is_symlink(), "SYMLINK", f"Lock is a symlink: {path}")
    try:
        path.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise Error("BUSY", f"Operation lock exists: {path}; inspect abandoned locks manually") from exc
    try:
        yield
    finally:
        path.rmdir()


class Cache:
    def __init__(self, root: Path, repo: str, offline: bool = False, allow_local: bool = False):
        self.repo = repository(repo, allow_local)
        self.root = root.expanduser().absolute()
        self.offline = offline
        self.allow_local = allow_local
        self.path = self.root / "repositories" / (digest(self.repo.encode()) + ".git")
        require(not self.root.is_symlink() and not self.path.is_symlink(), "SYMLINK", "Unsafe cache path")

    def git(self, *args: str, check: bool = True) -> bytes:
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_CONFIG") and
               k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
                         "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR")}
        env["GIT_TERMINAL_PROMPT"] = "0"
        command = ["git", "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false",
                   "-c", "protocol.file.allow=" + ("always" if self.allow_local else "never"),
                   "-c", "protocol.ext.allow=never", "-c", "maintenance.auto=false",
                   "--git-dir", str(self.path), *args]
        try:
            result = subprocess.run(command, env=env, capture_output=True, timeout=90, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise Error("GIT", "Git unavailable or operation timed out; check Git/SSH access") from exc
        if result.returncode and check:
            # Git diagnostics can repeat credential helper output or private URLs.
            raise Error("GIT", f"Git {args[0]} failed (exit {result.returncode}); check source/pin/access")
        return result.stdout if result.returncode == 0 else b""

    def prepare(self) -> None:
        guarded(self.root, "repositories/" + self.path.name)
        if not self.path.exists():
            require(not self.offline, "OFFLINE_MISS", "Pinned source is not cached")
            self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            self.path.mkdir(mode=0o700)
            self.git("init", "--bare", "--quiet", str(self.path))
        require(self.git("rev-parse", "--is-bare-repository").strip() == b"true", "CACHE", "Cache must be bare")

    def resolve(self, ref: str) -> str:
        require(isinstance(ref, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", ref)
                and ".." not in ref and "@{" not in ref, "REF", "Invalid source ref")
        self.prepare()
        with mutex(self.path.parent / (self.path.name + ".lock")):
            if SHA.fullmatch(ref):
                existing = self.git("rev-parse", "--verify", ref + "^{commit}", check=False).decode().strip()
                if existing == ref:
                    return ref
            require(not self.offline, "OFFLINE_MISS", "Exact commit unavailable offline")
            self.git("fetch", "--no-tags", "--no-recurse-submodules", "--depth=1", self.repo, ref)
            commit = self.git("rev-parse", "--verify", "FETCH_HEAD^{commit}").decode().strip()
            require(bool(SHA.fullmatch(commit)), "SOURCE", "Source did not resolve to a commit")
            require(not SHA.fullmatch(ref) or commit == ref, "SOURCE", "Fetched commit differs from pin")
            self.git("update-ref", "refs/veyrix/pins/" + commit, commit)
            return commit


class Snapshot:
    def __init__(self, cache: Cache, commit: str):
        require(bool(SHA.fullmatch(commit)), "PIN", "A full 40-character commit is required")
        self.cache = cache
        self.commit = commit
        self.files: dict[str, tuple[str, str, str]] = {}
        for row in filter(None, cache.git("ls-tree", "-rz", "--full-tree", commit).split(b"\0")):
            meta, raw = row.split(b"\t", 1)
            mode, kind, sha = meta.decode().split()
            self.files[raw.decode()] = (mode, kind, sha)

    def read(self, name: str) -> bytes:
        safe_rel(name)
        require(name in self.files, "SOURCE_MISSING", f"Source file missing: {name}")
        mode, kind, sha = self.files[name]
        require(mode == "100644" and kind == "blob", "SOURCE_TYPE", f"Unsupported source type: {name}")
        size = int(self.cache.git("cat-file", "-s", sha))
        require(size <= 4 * 1024 * 1024, "SIZE_LIMIT", f"Source file too large: {name}")
        data = self.cache.git("cat-file", "blob", sha)
        require(not data.startswith(b"version https://git-lfs.github.com/spec/"),
                "LFS", f"Unresolved LFS pointer: {name}")
        return data
