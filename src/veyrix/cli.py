"""Explicit init/sync/update/audit; ordinary sync never selects a newer revision."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import __version__
from .common import Error, SHA, encoded, guarded, read_regular, require
from .deploy import MANIFEST, apply, plan, read_state, roots_for
from .resolve import manifest, resolve
from .source import Cache, Snapshot

DEFAULT_REPOSITORY = "https://github.com/unofficialmmon/veyrix.git"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="veyrix", description=__doc__)
    result.add_argument("--version", action="version", version=__version__)
    result.add_argument("--project", type=Path, default=Path.cwd())
    result.add_argument("--cache-dir", type=Path, default=Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "veyrix")
    result.add_argument("--offline", action="store_true", help="Use cached exact commits only")
    result.add_argument("--allow-local-source", action="store_true", help="Explicit development/test-only file:// source permission")
    result.add_argument("--extra-skill-root", type=Path, action="append", default=[], help="Additional disk discovery root to check for collisions")
    commands = result.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Create a manifest, lock and explicit profile deployment")
    init.add_argument("--profile", required=True)
    init.add_argument("--repository", default=DEFAULT_REPOSITORY)
    init.add_argument("--ref", required=True, help="Reviewed full commit preferred; a named ref is resolved once")
    init.add_argument("--addon", action="append", default=[])
    init.add_argument("--accept-limitations", action="append", default=[], metavar="SKILL_ID")
    init.add_argument("--dry-run", action="store_true")
    sync = commands.add_parser("sync", help="Reconcile manifest at the existing immutable pin")
    sync.add_argument("--dry-run", action="store_true")
    update = commands.add_parser("update", help="Preview a new ref; only --apply updates project state")
    update.add_argument("--ref", required=True)
    update.add_argument("--apply", action="store_true")
    commands.add_parser("audit", help="Check frozen desired state without project writes")
    commands.add_parser("info", help="Print this project's selected IDs and limitations")
    return result


def run(args: argparse.Namespace) -> tuple[dict, int]:
    project = args.project.expanduser().absolute()
    require(not project.is_symlink() and project.is_dir(), "PROJECT", "Use an existing real project directory")
    # Initial v0.1 intentionally supports explicit Git project roots, not nested
    # automatic workspace detection or accidental parent-repository mutation.
    require((project / ".git").exists(), "PROJECT", "Run at a Git project root (.git directory or worktree file)")
    cache_path = args.cache_dir.expanduser().absolute()
    require(not cache_path.resolve().is_relative_to(project.resolve()), "CACHE_SCOPE", "Cache must be outside the project")
    require(not any(cache_path.resolve().is_relative_to(p.resolve()) for p in roots_for(project, args.extra_skill_root)),
            "CACHE_SCOPE", "Cache must be outside active disk Skill roots")
    old, receipt = read_state(project)
    current_manifest = read_regular(guarded(project, MANIFEST))
    new_manifest = None
    if args.command == "init":
        require(old is None and current_manifest is None, "EXISTS", "Project already has Veyrix state; use sync")
        new_manifest = encoded({"schema": 1, "repository": args.repository, "profile": args.profile,
                                "addons": args.addon, "accept_limitations": args.accept_limitations})
        spec = manifest(new_manifest, args.allow_local_source)
        new_manifest = encoded(spec)  # JSON is an unambiguous YAML subset.
        ref = args.ref
    else:
        require(old is not None and current_manifest is not None, "NOT_INITIALIZED", "No complete Veyrix state; run init")
        assert old is not None and current_manifest is not None
        spec = manifest(current_manifest, args.allow_local_source)
        require(spec["repository"] == old["repository"], "SOURCE_CHANGED", "Repository migration is not an ordinary sync/update")
        ref = args.ref if args.command == "update" else old["commit"]
    if args.command == "init" and not args.dry_run or args.command == "update" and args.apply:
        require(SHA.fullmatch(ref) is not None, "PIN_REQUIRED", "Apply requires a full commit SHA; preview named refs first")
    cache = Cache(args.cache_dir, spec["repository"], args.offline, args.allow_local_source)
    commit = cache.resolve(ref)
    source = Snapshot(cache, commit)
    locked, content = resolve(source, spec)
    if old is not None and commit == old["commit"]:
        require(locked["catalog_sha256"] == old.get("catalog_sha256"), "LOCK_MODIFIED", "Locked catalog digest differs from pinned source")
    if args.command == "info":
        return {"result": "INFO", "commit": commit, "profile": spec["profile"],
                "skills": locked["skills"], "limitations": locked["limitations"], "host_runtime": "NOT_RUN"}, 0
    change = plan(project, locked, content, old, receipt, args.extra_skill_root, new_manifest)
    dry = args.command == "audit" or getattr(args, "dry_run", False) or args.command == "update" and not args.apply
    result = change.summary() if dry else apply(change, cache.root)
    result.update({"commit": commit, "previous_commit": old["commit"] if old else None,
                   "profile": spec["profile"], "skills": locked["skills"], "routes": locked["routes"],
                   "limitations": list(locked["limitations"]), "preview": dry})
    if args.command == "audit":
        result["result"] = "DRIFT" if change.after else "STATIC_MATCH"
        return result, 1 if change.after else 0
    return result, 0


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result, status = run(args)
    except Error as exc:
        result, status = {"result": "BLOCKED", "code": exc.code, "message": str(exc), "host_runtime": "NOT_RUN"}, 2
    except (OSError, UnicodeError, KeyError, TypeError, ValueError, RecursionError) as exc:
        result, status = {"result": "BLOCKED", "code": "INVALID_STATE", "message": str(exc), "host_runtime": "NOT_RUN"}, 2
    print(encoded(result).decode(), end="")
    return status


if __name__ == "__main__":
    sys.exit(main())
