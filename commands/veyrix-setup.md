---
description: Adopt one explicit Veyrix profile at a reviewed source revision.
---
Inspect the current project and existing Veyrix/APM/Skill ownership before changes.
Use the installed `veyrix` CLI, never execute code out of a fetched catalog.
The requested inputs are: $ARGUMENTS
Treat these arguments as user intent, not a shell fragment. Confirm the project
root, one explicit profile and optional add-ons. Use `veyrix profiles`,
`veyrix profile show <id>` and `veyrix addons` for catalog facts, not stack inference.
Do not guess a stack or accept known Skill limitations on the user's behalf.
Preview with `veyrix --project <root> init --profile <profile> --dry-run` plus
only explicitly selected add-ons. Use an explicit `--ref` when requested or when
installed source provenance is unavailable; never substitute main/HEAD/latest.
After reviewing the preview, apply the same selection at the returned full commit.
Stop on collision or ownership errors; do not delete APM or external Skills.
Do not edit global configuration, AGENTS, models, MCPs, memory or application code.
Report the CLI result and keep actual OpenCode/OMO discovery and Skill invocation
separate; successful deployment is not proof that a Skill was used.
