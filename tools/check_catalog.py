#!/usr/bin/env python3
"""Offline integrity/selection checks. Does not certify upstream code or host use."""
from __future__ import annotations
import hashlib, json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from veyrix.common import HASH, ID, SHA, Error, digest, encoded, load_json, load_yaml, require, safe_rel

def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def check(root: Path) -> dict:
    catalog=load_json((root/"catalog/skills.json").read_bytes()); entries=dict(catalog["skills"])
    migration=load_json((root/"catalog/migration.json").read_bytes())
    additions_path=root/"catalog/additions.json"
    additions=load_json(additions_path.read_bytes()) if additions_path.exists() else {"schema":1,"skills":{}}
    require(catalog["schema"]==migration["schema"]==additions["schema"]==1,"SCHEMA","Unsupported catalog schema")
    require(len(migration["decisions"])==95,"MIGRATION","Migration inventory must cover the reviewed 95 IDs")
    require(isinstance(additions.get("skills"),dict),"MIGRATION","Invalid additions catalog")
    for name,entry in additions["skills"].items():
        require(name not in entries and ID.fullmatch(name) is not None,"MIGRATION","Invalid/duplicate addition")
        require(entry.get("path")=="skills/"+name and entry.get("status") in ("available","conditional"),
                "MIGRATION","Invalid addition metadata")
        require(SHA.fullmatch(entry.get("origin",{}).get("commit","")) is not None,"ORIGIN",name)
        blobs=entry.get("files_git_blob")
        require(isinstance(blobs,dict) and "SKILL.md" in blobs,"INVENTORY",name)
        folder=root/entry["path"]
        actual={p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()}
        require(actual==set(blobs),"INVENTORY",name)
        require(any(Path(p).name.lower().startswith("license") for p in actual),"LICENSE",name)
        for rel,expected in blobs.items():
            safe_rel(rel); data=(folder/rel).read_bytes()
            require(git_blob(data)==expected,"HASH",name+"/"+rel)
        front=load_yaml((folder/"SKILL.md").read_text().split("---",2)[1])
        require(front.get("name")==name and isinstance(front.get("description"),str),"FRONTMATTER",name)
        entries[name]=entry
    roots={p.name for p in (root/"skills").iterdir()}
    require(roots==set(entries),"CATALOG","Catalog and source directories differ")
    count=size=0
    for name,entry in catalog["skills"].items():
        require(bool(ID.fullmatch(name)) and entry["path"]=="skills/"+name,"PATH",name)
        folder=root/entry["path"]; paths=list(folder.rglob("*"))
        require(not any(p.is_symlink() for p in paths),"SYMLINK",name)
        actual={p.relative_to(folder).as_posix() for p in paths if p.is_file()}
        require(actual==set(entry["files"]),"INVENTORY",name)
        require(set(entry["files"])==set(entry["original_files"])|set(entry["supplements"]),"ORIGIN",name)
        adapted=entry.get("adapted_files",{})
        require(isinstance(adapted,dict) and set(adapted)<=set(entry["original_files"]),"ORIGIN",name)
        for rel,expected in entry["original_files"].items():
            require(HASH.fullmatch(expected) is not None,"ORIGIN",name+"/"+rel)
        if adapted:
            sources=entry.get("adaptation_sources")
            require(isinstance(sources,list) and bool(sources),"ORIGIN",name)
            for source in sources:
                require(isinstance(source,dict) and SHA.fullmatch(source.get("commit","")) is not None and
                        isinstance(source.get("repository"),str) and bool(source["repository"]) and
                        isinstance(source.get("path"),str) and bool(safe_rel(source["path"])) and
                        isinstance(source.get("scope"),str) and bool(source["scope"].strip()),"ORIGIN",name)
            for rel,expected in adapted.items():
                require(HASH.fullmatch(expected) is not None and expected!=entry["original_files"][rel],
                        "ORIGIN",name+"/"+rel)
        else:
            require("adaptation_sources" not in entry,"ORIGIN",name)
        require(any(Path(p).name.lower().startswith("license") for p in actual),"LICENSE",name)
        require(SHA.fullmatch(entry["origin"]["commit"]) is not None,"ORIGIN",name)
        for rel,expected in entry["files"].items():
            safe_rel(rel); data=(folder/rel).read_bytes(); actual_digest=digest(data)
            require(HASH.fullmatch(expected) is not None and actual_digest==expected,
                    "HASH",name+"/"+rel+" expected="+str(expected)+" actual="+actual_digest)
            source_expected=adapted.get(rel,entry["original_files"].get(rel,entry["supplements"].get(rel,{}).get("sha256")))
            require(expected==source_expected,"ORIGIN",name+"/"+rel)
            count+=1; size+=len(data)
        front=load_yaml((folder/"SKILL.md").read_text().split("---",2)[1])
        require(front["name"]==name and isinstance(front["description"],str),"FRONTMATTER",name)
        require(entry["status"] in ("available","conditional") and entry["host_runtime"]=="NOT_RUN","EVIDENCE",name)
    reachable=set()
    for folder in ("profiles","addons"):
        for path in sorted((root/folder).glob("*.json")):
            spec=load_json(path.read_bytes()); require(spec["schema"]==1 and isinstance(spec["roles"],dict),"PROFILE",path.name)
            for role,names in spec["roles"].items():
                require(role in ("fixer","designer","oracle","librarian"),"ROLE",role)
                require(names==sorted(set(names)) and set(names)<=set(entries),"PROFILE",path.name)
                if folder=="profiles":
                    require(all(entries[n]["status"]=="available" for n in names),"PROFILE","Conditional IDs must remain opt-in")
                reachable.update(names)
    require(reachable==set(entries),"PROFILE","Unreachable catalog entries")
    kept={n for n,e in migration["decisions"].items() if e["decision"]=="KEEP"}
    require(kept|{"emil-design-eng"}|set(additions["skills"])==set(entries),"MIGRATION","Historical KEEP plus additions differ from catalog")
    require(not set(additions["skills"])&set(migration["decisions"]),"MIGRATION","Addition overlaps historical decision")
    require(all(e["decision"] in ("KEEP","EXCLUDE","DEFER") and e.get("reason") for e in migration["decisions"].values()),
            "MIGRATION","Every decision needs a reason")
    for name in ("setup","sync","audit"):
        text=(root/"commands"/f"veyrix-{name}.md").read_text()
        require(text.startswith("---\n") and "$ARGUMENTS" in text,"COMMAND",name)
    require(not (root/".apm").exists(),"SCOPE","No APM mirrors in Veyrix")
    return {"result":"PASS","skills":len(entries),"files":count+sum(len(e["files_git_blob"]) for e in additions["skills"].values()),
            "bytes":size,"profiles":len(list((root/"profiles").glob("*.json"))),
            "addons":len(list((root/"addons").glob("*.json"))),
            "conditional":[n for n,e in entries.items() if e["status"]=="conditional"],
            "origins":dict(Counter(e.get("upstream",{}).get("sourceType","local-derived") for e in entries.values())),
            "migration":dict(Counter(e["decision"] for e in migration["decisions"].values())),
            "host_runtime":"NOT_RUN"}

if __name__=="__main__":
    try: print(encoded(check(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1])).decode(),end="")
    except (Error,KeyError,ValueError,OSError,TypeError) as exc:
        print(json.dumps({"result":"FAIL","message":str(exc)})); raise SystemExit(1)
