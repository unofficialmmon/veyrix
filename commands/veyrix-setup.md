---
description: Adopt one explicit Veyrix profile at a reviewed source revision.
---
Inspect the current project and existing Veyrix/APM/Skill ownership before changes.
Use the installed `veyrix` CLI, never execute code out of a fetched catalog.
The requested inputs are: $ARGUMENTS
Treat these arguments as user intent, not a shell fragment. Confirm the project
root, one explicit profile, optional add-ons and reviewed source commit. Do not
guess a stack or accept known Skill limitations on the user's behalf.
Preview with `veyrix --project <root> init --profile <profile> --ref <commit> --dry-run`
plus only explicitly selected add-ons. Apply the same inputs after reviewing the
preview. Stop on collision or ownership errors; do not delete APM or external
Skills. Do not edit global configuration, models, MCPs, memory or application code.
Report the CLI result and keep actual OpenCode/OMO discovery and Skill invocation
separate; a successful deployment is not proof that a Skill was used.
