"""Read profile/add-on metadata from one explicit immutable source snapshot."""
from __future__ import annotations
from .common import ID, digest, load_json, require
from .resolve import load_catalog, profile
from .source import Snapshot

def describe(snapshot: Snapshot, group: str, name: str | None = None) -> dict:
    require(group in ("profiles", "addons"), "PROFILE", "Unknown definition group")
    catalog, catalog_digest = load_catalog(snapshot)
    if name is not None:
        require(isinstance(name, str) and ID.fullmatch(name) is not None, "PROFILE",
                "Use a profile ID returned by veyrix profiles")
        paths = [f"{group}/{name}.json"]
    else:
        paths = sorted(p for p in snapshot.files
                       if p.startswith(group + "/") and p.count("/") == 1 and p.endswith(".json"))
    entries = []
    for path in paths:
        identifier = path.split("/", 1)[1][:-5]
        require(ID.fullmatch(identifier) is not None, "PROFILE", "Invalid definition filename")
        roles = profile(snapshot, path)
        skills = sorted({skill for values in roles.values() for skill in values})
        limitations, statuses = {}, {}
        for skill in skills:
            entry = catalog["skills"].get(skill)
            require(isinstance(entry, dict) and entry.get("status") in ("available", "conditional"),
                    "CATALOG", f"Missing/unavailable Skill metadata: {skill}")
            statuses[skill] = entry["status"]
            if entry.get("limitations"):
                limitations[skill] = entry["limitations"]
        entries.append({"id": identifier, "roles": roles, "skills": skills,
                        "skill_status": statuses, "limitations": limitations})
    output = {"result": "PROFILE" if name is not None else group.upper(),
              "repository": snapshot.cache.repo, "commit": snapshot.commit,
              "catalog_sha256": catalog_digest, "evidence": "STATIC_METADATA",
              "host_runtime": "NOT_RUN"}
    output["profile" if name is not None else group] = entries[0] if name is not None else entries
    return output
