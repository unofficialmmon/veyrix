---
description: Reconcile the explicit Veyrix manifest at its existing pinned revision.
---
Run the installed `veyrix --project <current-project-root> sync --dry-run` first.
Inspect the exact targets, existing ownership and preserved user changes. Then
run `sync` without `--dry-run` for this explicitly requested reconciliation.
Do not upgrade the source revision, invoke `update`, rewrite user AGENTS or use
raw copy/delete as a fallback. Stop on managed-file modifications, duplicate
Skill owners, a legacy OMO JSON config or unsupported state. Report partial
writes/recovery if the CLI fails. No Git commits, global changes, plugin or MCP
installation are authorized here. CLI success is not live Skill activation.
User scope: $ARGUMENTS
