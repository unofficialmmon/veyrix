"""Explicit init/sync/update/audit; ordinary sync never selects a newer revision."""
from __future__ import annotations
import argparse, os, sys
from pathlib import Path
from . import __version__
from .common import Error, SHA, digest, encoded, guarded, read_regular, require
from .deploy import MANIFEST, apply, plan, read_state, roots_for
from .discovery import describe
from .feedback import failure
from .provenance import installed_pin, installed_source
from .resolve import manifest, resolve
from .source import Cache, Snapshot

DEFAULT_REPOSITORY = "https://github.com/unofficialmmon/veyrix.git"

def parser() -> argparse.ArgumentParser:
    result=argparse.ArgumentParser(prog="veyrix",description=__doc__)
    result.add_argument("--version",action="version",version=__version__)
    result.add_argument("--project",type=Path,default=Path.cwd())
    result.add_argument("--cache-dir",type=Path,default=Path(os.environ.get("XDG_CACHE_HOME",str(Path.home()/".cache")))/"veyrix")
    result.add_argument("--offline",action="store_true",help="Use cached exact commits only")
    result.add_argument("--allow-local-source",action="store_true",help="Explicit development/test-only file:// source permission")
    result.add_argument("--extra-skill-root",type=Path,action="append",default=[],help="Additional disk discovery root to check for collisions")
    commands=result.add_subparsers(dest="command",required=True)
    init=commands.add_parser("init",help="Create a manifest, lock and explicit profile deployment")
    init.add_argument("--profile",required=True); init.add_argument("--repository",default=DEFAULT_REPOSITORY)
    init.add_argument("--ref",help="Default: installed Git commit for this repository; named refs are preview-only")
    init.add_argument("--addon",action="append",default=[]); init.add_argument("--accept-limitations",action="append",default=[],metavar="SKILL_ID")
    init.add_argument("--dry-run",action="store_true")
    sync=commands.add_parser("sync",help="Reconcile manifest at the existing immutable pin"); sync.add_argument("--dry-run",action="store_true")
    update=commands.add_parser("update",help="Preview a new ref; only --apply updates project state")
    update.add_argument("--ref",required=True); update.add_argument("--apply",action="store_true")
    commands.add_parser("audit",help="Check frozen desired state without project writes")
    commands.add_parser("info",help="Print this project's selected IDs and limitations")
    commands.add_parser("doctor",help="Diagnose local state using cached source only; never repair or fetch")
    profiles=commands.add_parser("profiles",help="List profiles at the project or installed source pin")
    addons=commands.add_parser("addons",help="List add-ons and their limitations at the same pin")
    show=commands.add_parser("profile",help="Inspect a profile definition"); subs=show.add_subparsers(dest="profile_command",required=True)
    detail=subs.add_parser("show",help="Show selected Skills, roles and limitations"); detail.add_argument("id")
    for command in (profiles,addons,detail):
        command.add_argument("--repository",help="Explicit catalog repository override")
        command.add_argument("--ref",help="Explicit source ref override; no automatic latest lookup")
    return result

def browse(args: argparse.Namespace, project: Path) -> tuple[dict,int]:
    old,_=read_state(project); raw=read_regular(guarded(project,MANIFEST))
    require((old is None)==(raw is None),"NOT_INITIALIZED","Incomplete project state; review before source selection")
    spec=manifest(raw,args.allow_local_source) if raw is not None else None
    if old is not None: require(spec["repository"]==old["repository"],"SOURCE_CHANGED","Manifest and pinned source differ")
    repo=args.repository or (spec["repository"] if spec else DEFAULT_REPOSITORY)
    if args.ref is not None: ref=args.ref
    elif old is not None and repo==old["repository"]: ref=old["commit"]
    else: ref=installed_pin(repo,args.allow_local_source)
    cache=Cache(args.cache_dir,repo,args.offline,args.allow_local_source); source=Snapshot(cache,cache.resolve(ref))
    if old is not None and repo==old["repository"] and source.commit==old["commit"]:
        require(resolve(source,spec)[0]["catalog_sha256"]==old.get("catalog_sha256"),"LOCK_MODIFIED","Locked catalog digest differs from pinned source")
    group="addons" if args.command=="addons" else "profiles"
    return describe(source,group,args.id if args.command=="profile" else None),0

def run(args: argparse.Namespace) -> tuple[dict,int]:
    project=args.project.expanduser().absolute()
    require(not project.is_symlink() and project.is_dir(),"PROJECT","Use an existing real project directory")
    discovery=args.command in ("profiles","profile","addons")
    project_scope=not discovery or any((project/p).exists() or (project/p).is_symlink() for p in (".git",MANIFEST,"veyrix.lock.json",".veyrix"))
    cache_path=args.cache_dir.expanduser().absolute()
    require(not project_scope or not cache_path.resolve().is_relative_to(project.resolve()),"CACHE_SCOPE","Cache must be outside the project")
    require(not any(cache_path.resolve().is_relative_to(p.resolve()) for p in roots_for(project,args.extra_skill_root)),
            "CACHE_SCOPE","Cache must be outside active disk Skill roots")
    if discovery: return browse(args,project)
    if args.command=="doctor":
        probe=argparse.Namespace(**vars(args)); probe.command,probe.offline="audit",True
        result,status=run(probe); result["result"]="HEALTHY" if status==0 else "DRIFT"
        if status: result["next_action"]="Review veyrix sync --dry-run before applying any repair. Doctor made no project changes."
        return result,status
    require((project/".git").exists(),"PROJECT","Run at a Git project root (.git directory or worktree file)")
    old,receipt=read_state(project); current_manifest=read_regular(guarded(project,MANIFEST)); new_manifest=None
    if args.command=="init":
        require(old is None and current_manifest is None,"EXISTS","Project already has Veyrix state; use sync")
        new_manifest=encoded({"schema":1,"repository":args.repository,"profile":args.profile,
                              "addons":args.addon,"accept_limitations":args.accept_limitations})
        spec=manifest(new_manifest,args.allow_local_source); new_manifest=encoded(spec)
        ref=args.ref if args.ref is not None else installed_pin(spec["repository"],args.allow_local_source)
    else:
        require(old is not None and current_manifest is not None,"NOT_INITIALIZED","No complete Veyrix state; run init")
        spec=manifest(current_manifest,args.allow_local_source)
        require(spec["repository"]==old["repository"],"SOURCE_CHANGED","Repository migration is not an ordinary sync/update")
        ref=args.ref if args.command=="update" else old["commit"]
    if (args.command=="init" and not args.dry_run) or (args.command=="update" and args.apply):
        require(SHA.fullmatch(ref) is not None,"PIN_REQUIRED","Apply requires a full commit SHA; preview named refs first")
    cache=Cache(args.cache_dir,spec["repository"],args.offline,args.allow_local_source)
    commit=cache.resolve(ref); source=Snapshot(cache,commit); locked,content=resolve(source,spec)
    if old is not None and commit==old["commit"]:
        require(locked["catalog_sha256"]==old.get("catalog_sha256"),"LOCK_MODIFIED","Locked catalog digest differs from pinned source")
    if args.command=="info":
        return {"result":"INFO","commit":commit,"profile":spec["profile"],"skills":locked["skills"],
                "limitations":locked["limitations"],"host_runtime":"NOT_RUN"},0
    change=plan(project,locked,content,old,receipt,args.extra_skill_root,new_manifest)
    dry=args.command=="audit" or getattr(args,"dry_run",False) or args.command=="update" and not args.apply
    result=change.summary() if dry else apply(change,cache.root)
    result.update({"commit":commit,"previous_commit":old["commit"] if old else None,"profile":spec["profile"],
                   "skills":locked["skills"],"routes":locked["routes"],"limitations":list(locked["limitations"]),"preview":dry})
    if args.command=="audit":
        result["result"]="DRIFT" if change.after else "STATIC_MATCH"; return result,1 if change.after else 0
    return result,0

def main(argv: list[str] | None=None) -> int:
    args=parser().parse_args(argv)
    try: result,status=run(args)
    except Error as exc: result,status=failure(exc),2
    except (OSError,UnicodeError,KeyError,TypeError,ValueError,RecursionError) as exc:
        result,status=failure(Error("INVALID_STATE",str(exc))),2
    if args.command=="doctor":
        try: provenance=installed_source(args.allow_local_source)
        except Error: provenance={"evidence":"UNAVAILABLE","note":"Explicit project pins remain usable; new init needs --ref."}
        result.update({"installation":{"version":__version__,"source":provenance},
                       "diagnostic_scope":"STATIC_CONFIGURATION_AND_DISK_INVENTORY","source_access":"CACHE_ONLY","host_runtime":"NOT_RUN"})
    print(encoded(result).decode(),end=""); return status

if __name__=="__main__": sys.exit(main())
