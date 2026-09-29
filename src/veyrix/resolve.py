"""Resolve explicit profiles and verify complete source inventories."""
from __future__ import annotations
from typing import Any
from .common import HASH, ID, digest, ids, load_json, load_yaml, require, safe_rel
from .source import Snapshot

def load_catalog(snapshot: Snapshot) -> tuple[dict, str]:
    base_bytes = snapshot.read("catalog/skills.json")
    catalog = load_json(base_bytes)
    require(catalog.get("schema") == 1 and isinstance(catalog.get("skills"), dict), "CATALOG", "Invalid catalog")
    if "catalog/additions.json" not in snapshot.files:
        return catalog, digest(base_bytes)
    extra_bytes = snapshot.read("catalog/additions.json")
    extra = load_json(extra_bytes)
    require(isinstance(extra, dict) and extra.get("schema") == 1 and isinstance(extra.get("skills"), dict),
            "CATALOG", "Invalid additions catalog")
    for name, entry in extra["skills"].items():
        require(name not in catalog["skills"], "CATALOG", f"Duplicate catalog Skill: {name}")
        require(isinstance(entry, dict) and isinstance(entry.get("files_git_blob"), dict),
                "CATALOG", f"Invalid addition: {name}")
        normalized = dict(entry)
        normalized["files"] = {}
        prefix = safe_rel(entry["path"]) + "/"
        actual = {p[len(prefix):] for p in snapshot.files if p.startswith(prefix)}
        require(actual == set(entry["files_git_blob"]) and "SKILL.md" in actual,
                "INVENTORY", f"Incomplete added Skill inventory: {name}")
        for rel, blob in entry["files_git_blob"].items():
            safe_rel(rel)
            path = prefix + rel
            require(snapshot.files[path][2] == blob, "HASH", f"Added Skill Git blob differs: {name}/{rel}")
            normalized["files"][rel] = digest(snapshot.read(path))
        catalog["skills"][name] = normalized
    return catalog, digest(base_bytes + b"\0" + extra_bytes)

MANIFEST_KEYS = {"schema", "repository", "profile", "addons", "accept_limitations"}

def manifest(data: bytes, allow_local: bool = False) -> dict:
    from .source import repository
    obj = load_yaml(data)
    require(isinstance(obj, dict) and obj.get("schema") == 1 and not set(obj) - MANIFEST_KEYS,
            "MANIFEST", "Invalid veyrix.yml schema/keys")
    require(isinstance(obj.get("profile"), str) and ID.fullmatch(obj["profile"]) is not None,
            "MANIFEST", "An explicit profile is required")
    repository(obj.get("repository", ""), allow_local)
    for key in ("addons", "accept_limitations"):
        obj[key] = sorted(ids(obj.get(key, []), key))
    return obj

def profile(snapshot: Snapshot, path: str) -> dict[str, list[str]]:
    obj = load_json(snapshot.read(path))
    require(isinstance(obj, dict) and set(obj) == {"schema", "roles"} and obj["schema"] == 1,
            "PROFILE", f"Invalid profile: {path}")
    roles = obj["roles"]
    require(isinstance(roles, dict) and set(roles) <= {"fixer", "designer", "oracle", "librarian"},
            "PROFILE", f"Unsupported roles in {path}")
    return {name: ids(values, path + ":" + name) for name, values in roles.items()}

def resolve(snapshot: Snapshot, spec: dict) -> tuple[dict, dict[str, bytes]]:
    catalog, catalog_digest = load_catalog(snapshot)
    routes: dict[str, set[str]] = {}
    selected = ["profiles/" + spec["profile"] + ".json"] + ["addons/" + x + ".json" for x in spec["addons"]]
    definition_hashes = {}
    for path in selected:
        definition_hashes[path] = digest(snapshot.read(path))
        for role, values in profile(snapshot, path).items():
            routes.setdefault(role, set()).update(values)
    skill_ids = sorted(set().union(*routes.values())) if routes else []
    require(bool(skill_ids), "PROFILE", "Profile resolves to no Skills")
    result: dict[str, bytes] = {}
    warnings: dict[str, Any] = {}
    require(set(spec["accept_limitations"]) <= set(skill_ids), "LIMITATIONS", "Acceptance contains unselected IDs")
    for name in skill_ids:
        require(name in catalog["skills"], "CATALOG", f"Unknown Skill: {name}")
        entry = catalog["skills"][name]
        require(entry.get("status") in ("available", "conditional"), "HELD", f"Skill unavailable: {name}")
        if entry["status"] == "conditional":
            require(name in spec["accept_limitations"], "LIMITATIONS",
                    f"Read catalog limitations and explicitly accept {name} before deployment")
        prefix = safe_rel(entry["path"]) + "/"
        require(prefix == "skills/" + name + "/", "CATALOG", f"Noncanonical source path: {name}")
        hashes = entry["files"]
        actual = {p[len(prefix):] for p in snapshot.files if p.startswith(prefix)}
        require(isinstance(hashes, dict) and actual == set(hashes) and "SKILL.md" in hashes,
                "INVENTORY", f"Incomplete Skill inventory: {name}")
        for rel, expected in hashes.items():
            safe_rel(rel)
            require(isinstance(expected, str) and HASH.fullmatch(expected) is not None,
                    "CATALOG", f"Invalid digest: {name}/{rel}")
            content = snapshot.read(prefix + rel)
            require(digest(content) == expected, "HASH", f"Source hash differs: {name}/{rel}")
            result[".agents/skills/" + name + "/" + rel] = content
        entrypoint = result[".agents/skills/" + name + "/SKILL.md"].decode()
        require(entrypoint.startswith("---\n") and "\n---" in entrypoint[4:], "SKILL", f"Bad frontmatter: {name}")
        front = load_yaml(entrypoint.split("---", 2)[1])
        require(isinstance(front, dict) and front.get("name") == name and
                isinstance(front.get("description"), str) and bool(front["description"].strip()),
                "SKILL", f"Invalid Skill identity: {name}")
        if entry.get("limitations"):
            warnings[name] = entry["limitations"]
    for command in ("setup", "sync", "audit"):
        path = "commands/veyrix-" + command + ".md"
        result[".opencode/commands/veyrix-" + command + ".md"] = snapshot.read(path)
    require(sum(map(len, result.values())) <= 32 * 1024 * 1024, "SIZE_LIMIT", "Selection exceeds size limit")
    lock = {"schema":1,"repository":spec["repository"],"commit":snapshot.commit,
            "manifest":spec,"catalog_sha256":catalog_digest,"definitions":definition_hashes,
            "skills":skill_ids,"routes":{k:sorted(v) for k,v in sorted(routes.items())},
            "files":{p:digest(b) for p,b in sorted(result.items())},"limitations":warnings}
    return lock, result
