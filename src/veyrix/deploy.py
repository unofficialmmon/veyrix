"""Bounded file ownership, native Skill collision inventory and safe apply."""
from __future__ import annotations

import os
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from . import jsonc
from .common import Error, HASH, ID, config_home, digest, encoded, guarded, ids, load_json, load_yaml, read_regular, require, safe_rel
from .source import mutex

OMO = ".opencode/oh-my-opencode-slim.jsonc"
LEGACY_OMO = ".opencode/oh-my-opencode-slim.json"
STATE_DIR = ".agents/veyrix"\nRECEIPT = STATE_DIR + "/managed.json"
LOCK = "veyrix.lock.json"
MANIFEST = "veyrix.yml"


def managed_path(path: str) -> bool:
    safe_rel(path)
    parts = path.split("/")
    return (len(parts) >= 4 and parts[:2] == [".agents", "skills"] and ID.fullmatch(parts[2]) is not None
            or path in {f".opencode/commands/veyrix-{x}.md" for x in ("setup", "sync", "audit")})


def read_state(root: Path) -> tuple[dict | None, dict | None]:
    lock_raw = read_regular(guarded(root, LOCK))
    raw = read_regular(guarded(root, RECEIPT))
    require((raw is None) == (lock_raw is None), "STATE", "Lock and ownership receipt must both exist")
    if raw is None:
        return None, None
    receipt = load_json(raw)
    lock = load_json(lock_raw)
    require(isinstance(receipt, dict) and receipt.get("schema") == 1 and
            set(receipt) == {"schema", "lock_sha256", "files", "routes"}, "STATE", "Invalid ownership receipt")
    require(receipt["lock_sha256"] == digest(lock_raw), "LOCK_MODIFIED", "Lock changed outside Veyrix; use update")
    require(isinstance(lock, dict) and lock.get("schema") == 1, "STATE", "Invalid lock")
    require(isinstance(receipt["files"], dict) and isinstance(receipt["routes"], dict), "STATE", "Invalid receipt maps")
    for path, value in receipt["files"].items():
        require(managed_path(path) and isinstance(value, str) and HASH.fullmatch(value) is not None,
                "STATE", "Receipt contains an invalid managed path or digest")
    require(receipt["files"] == lock.get("files"), "STATE", "Receipt/lock file set mismatch")
    for role, values in receipt["routes"].items():
        require(role in {"fixer", "designer", "oracle", "librarian"}, "STATE", "Unknown owned role")
        ids(values, role)
        require(set(values) <= set(lock.get("routes", {}).get(role, [])), "STATE", "Invalid owned grants")
    return lock, receipt


def roots_for(project: Path, extra: list[Path]) -> list[Path]:
    roots = [project / p / "skills" for p in (".agents", ".opencode", ".claude")]
    roots += [config_home() / "skills", Path.home() / ".agents/skills", Path.home() / ".claude/skills"]
    roots += extra
    return list(dict.fromkeys(p.expanduser().absolute() for p in roots))


def check_collisions(project: Path, names: list[str], previous: dict, extra: list[Path]) -> list[str]:
    own = {str((project / p).resolve()) for p in previous if p.endswith("/SKILL.md")}
    selected = set(names)
    seen = set()
    for root in roots_for(project, extra):
        if not root.exists():
            require(not root.is_symlink(), "DISCOVERY", f"Dangling Skill root: {root}")
            continue
        require(root.is_dir(), "DISCOVERY", f"Skill root is not a directory: {root}")
        actual_root = root.resolve()
        if str(actual_root) in seen:
            continue
        seen.add(str(actual_root))
        for directory, dirs, files in os.walk(actual_root, followlinks=False):
            for name in dirs:
                candidate = Path(directory) / name
                require(not candidate.is_symlink(), "DISCOVERY", f"Symlink subtree requires explicit ownership review: {candidate}")
            candidates = ["SKILL.md"] if "SKILL.md" in files else []
            if Path(directory) == actual_root:
                candidates += [n for n in files if n.endswith(".md") and n != "SKILL.md"]
            for name in candidates:
                path = Path(directory) / name
                require(not path.is_symlink(), "DISCOVERY", f"Symlink entrypoint requires review: {path}")
                data = read_regular(path)
                assert data is not None
                try:
                    text = data.decode()
                    front = load_yaml(text.split("---", 2)[1]) if text.startswith("---\n") else {}
                except (Error, UnicodeError, IndexError):
                    continue
                skill = front.get("name") if isinstance(front, dict) else None
                # Root markdown uses its filename as ID on supported v2 hosts.
                candidate_id = skill if name == "SKILL.md" else path.stem
                if candidate_id in selected and str(path.resolve()) not in own:
                    raise Error("SKILL_COLLISION", f"Selected ID {candidate_id} already exists at {path}; no automatic removal/adoption")
    typo = project / ".agent/skills"
    if typo.exists():
        require(not any((typo / name).exists() for name in names), "WRONG_SKILL_ROOT", "Found selected Skill in .agent/skills; expected .agents/skills")
    return ["Disk inventory only; plugin registrations, remote catalogs, runtime permissions and actual Skill loads are NOT_RUN."]


@dataclass
class Plan:
    root: Path
    after: dict[str, bytes | None] = field(default_factory=dict)
    before: dict[str, bytes | None] = field(default_factory=dict)
    modes: dict[str, int] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def watch(self, path: str) -> bytes | None:
        if path not in self.before:
            target = guarded(self.root, path)
            self.before[path] = read_regular(target)
            if target.exists():
                self.modes[path] = target.stat().st_mode & 0o777
        return self.before[path]

    def put(self, path: str, data: bytes | None) -> None:
        if self.watch(path) != data:
            self.after[path] = data

    def summary(self) -> dict:
        return {"result": "CHANGES_PLANNED" if self.after else "NOOP",
                "changes": [{"path": p, "action": "DELETE" if b is None else
                             "CREATE" if self.before[p] is None else "UPDATE"}
                            for p, b in sorted(self.after.items())],
                "notes": self.notes, "host_runtime": "NOT_RUN"}


def plan(root: Path, lock: dict, content: dict[str, bytes], old: dict | None,
         receipt: dict | None, extra: list[Path], init_manifest: bytes | None = None) -> Plan:
    require(not (root / LEGACY_OMO).exists() and not (root / LEGACY_OMO).is_symlink(),
            "LEGACY_OMO_CONFIG", "Existing .json OMO config requires explicit migration; will not shadow it with .jsonc")
    result = Plan(root)
    for watched in (MANIFEST, LOCK, RECEIPT, OMO, LEGACY_OMO):
        result.watch(watched)
    previous = receipt["files"] if receipt else {}
    # Existing owned bytes must remain unchanged. A missing file may be restored.
    for path, expected in previous.items():
        data = result.watch(path)
        require(data is None or digest(data) == expected, "MANAGED_MODIFIED", f"Managed file modified: {path}")
    for path in content:
        data = result.watch(path)
        require(path in previous or data is None, "UNOWNED", f"Existing file has another owner: {path}")
    all_ids = set(lock["skills"]) | set(old.get("skills", []) if old else [])
    for name in all_ids:
        folder = guarded(root, ".agents/skills/" + name)
        if folder.exists():
            for directory, dirs, files in os.walk(folder, followlinks=False):
                for child in dirs:
                    require(not (Path(directory) / child).is_symlink(), "SYMLINK", f"Symlink in managed Skill: {name}")
                for child in files:
                    rel = (Path(directory) / child).relative_to(root).as_posix()
                    require(rel in previous, "UNOWNED", f"Unowned file in managed Skill directory: {rel}")
    result.notes += check_collisions(root, lock["skills"], previous, extra)
    original_omo = result.before[OMO]
    text = original_omo.decode() if original_omo is not None else "{\n}\n"
    new_text, routes = jsonc.reconcile(text, lock["routes"], receipt["routes"] if receipt else {})
    if original_omo is None:
        new_text = encoded({"agents": {role: {"skills_add": values} for role, values in lock["routes"].items()}}).decode()
    result.put(OMO, new_text.encode())
    for path in sorted(set(previous) | set(content)):
        result.put(path, content.get(path))
    lock_bytes = encoded(lock)
    result.put(LOCK, lock_bytes)
    result.put(RECEIPT, encoded({"schema": 1, "lock_sha256": digest(lock_bytes),
                               "files": lock["files"], "routes": routes}))
    if init_manifest is not None:
        require(result.before[MANIFEST] is None, "EXISTS", "veyrix.yml already exists")
        result.put(MANIFEST, init_manifest)
    if lock["limitations"]:
        result.notes.append("Selected Skills retain upstream limitations; read veyrix.lock.json limitations.")
    return result


def _replace(path: Path, data: bytes | None, mode: int) -> None:
    if data is None:
        if path.exists():
            path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.parent / (".veyrix-" + uuid.uuid4().hex + ".tmp")
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
            os.fchmod(handle.fileno(), mode)
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def apply(change: Plan, cache_root: Path) -> dict:
    if not change.after:
        return change.summary()
    root = change.root
    state = guarded(root, STATE_DIR)
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    with mutex(state / "write.lock"):
        for path, before in change.before.items():
            require(read_regular(guarded(root, path)) == before, "CONCURRENT_CHANGE", f"Target changed after planning: {path}")
        # Backups have opaque names, never SKILL.md, and are not in a Skill root.
        backup = cache_root / "recovery" / uuid.uuid4().hex
        backup.mkdir(parents=True, mode=0o700)
        os.chmod(backup, 0o700)
        record = {"project": str(root), "files": {}}
        for index, path in enumerate(sorted(change.after)):
            data = change.before[path]
            key = f"{index:05d}.backup"
            if data is not None:
                (backup / key).write_bytes(data)
                os.chmod(backup / key, 0o600)
            record["files"][path] = {"backup": key if data is not None else None,
                                      "sha256": digest(data) if data is not None else None,
                                      "mode": change.modes.get(path, 0o644)}
        (backup / "recovery.json").write_bytes(encoded(record))
        os.chmod(backup / "recovery.json", 0o600)
        written = []
        try:
            # Receipt last; it never certifies a partially applied file set.
            paths = sorted(change.after, key=lambda p: (p == RECEIPT, p == LOCK, p))
            for path in paths:
                target = guarded(root, path)
                require(read_regular(target) == change.before[path], "CONCURRENT_CHANGE", f"Concurrent target change: {path}")
                _replace(target, change.after[path], change.modes.get(path, 0o644))
                written.append(path)
        except Exception as exc:
            conflicts = []
            for path in reversed(written):
                target = guarded(root, path)
                if read_regular(target) == change.after[path]:
                    _replace(target, change.before[path], change.modes.get(path, 0o644))
                else:
                    conflicts.append(path)
            raise Error("APPLY_FAILED", f"Apply stopped; recovery at {backup}; rollback conflicts: {conflicts}") from exc
    result = change.summary()
    result["result"] = "UPDATED"
    result["recovery"] = str(backup)
    return result
