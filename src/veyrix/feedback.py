"""Actionable recovery guidance without weakening existing errors."""
from __future__ import annotations
from .common import Error

ACTIONS = {
 "PIN_REQUIRED":"Supply --ref <FULL_COMMIT_SHA> for the selected source. Named refs are preview-only; never substitute latest/main implicitly.",
 "PROFILE":"Run veyrix profiles and veyrix profile show <ID> against the same source pin; select an explicit valid profile.",
 "SOURCE_MISSING":"Run veyrix profiles or veyrix addons against the same repository and pin; do not substitute a newer revision.",
 "NOT_INITIALIZED":"Choose a profile with veyrix profiles, then run veyrix init --profile <ID>. Preserve partial state for review.",
 "EXISTS":"Use veyrix sync --dry-run to inspect existing managed state; do not initialize over it.",
 "PROJECT":"Use veyrix --project <EXISTING_GIT_ROOT> with a real project directory.",
 "OFFLINE_MISS":"Populate the reviewed exact pin with an online preview, then retry offline. Doctor never fetches or repairs.",
 "MANAGED_MODIFIED":"Inspect and back up the local change. Reconcile ownership before retrying; Veyrix will not overwrite it.",
 "UNOWNED":"Identify the existing file owner and resolve the collision explicitly; identical bytes do not authorize adoption.",
 "SKILL_COLLISION":"Review the duplicate Skill ID and both owners. Do not automatically delete or adopt either copy.",
 "ROUTING_DENIED":"Review existing OMO exclusions and the selected Skills. Do not bypass the denial.",
 "INVALID_JSONC":"Correct only the JSONC syntax problem while preserving comments and unrelated user settings.",
 "LIMITATIONS":"Read the selected Skill limitations and explicitly accept only the relevant IDs; never accept automatically.",
 "SOURCE_CHANGED":"Restore the intended repository or plan an explicit migration; ordinary sync/update cannot migrate repositories.",
 "LOCK_MODIFIED":"Compare lock and receipt with trusted history; do not hand-edit hashes to bypass the mismatch.",
 "BUSY":"Check whether the owning operation is still running. Review abandoned locks manually.",
 "CONCURRENT_CHANGE":"Re-read current files and retry the preview after coordinating concurrent writers.",
 "APPLY_FAILED":"Inspect the recovery directory and rollback conflicts before retrying; do not overwrite concurrent changes.",
 "SYMLINK":"Inspect the symlink and owner. Use an explicitly approved real path; do not follow or replace it automatically."
}
def failure(exc: Error) -> dict:
    return {"result":"BLOCKED","code":exc.code,"message":str(exc),
            "next_action":ACTIONS.get(exc.code,
              "Inspect the reported source/configuration problem and its owner, then retry the same intended operation without bypassing checks."),
            "host_runtime":"NOT_RUN"}
