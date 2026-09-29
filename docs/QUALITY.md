# Common quality layer

`engineering-quality` is an explicit add-on, not a workflow engine. It makes
exactly three Skills available to fixer and oracle through owned `skills_add`
contributions. No base profile selects them automatically.

| Scope | Reference |
| --- | --- |
| Code review | engineering-quality / change-review |
| Change impact | engineering-quality / change-impact |
| Architecture consistency | engineering-quality / architecture-consistency |
| Completion verification | engineering-quality / completion-verification |
| Regression evidence | regression-proof |
| Changed trust boundaries | security-review |

Choose only relevant references. A small local correction does not trigger a
mandatory full audit. Read-only review does not authorize fixing, installing,
probing production, or changing permissions. Impact discovery does not expand
approved scope. Architecture checks use actual project authority rather than
mandating a particular layering pattern.

## Ownership

OpenCode owns host loading and permissions; OMO Slim owns agent roles and
orchestration. Project `AGENTS.md` and repository contracts define local policy;
Veyrix supplies reusable technical/quality guidance. Global and project AGENTS
remain user/project-owned. Optional templates in `docs/agents/` are documents,
not CLI-managed outputs.

Do not access a denied Skill by reading its files through another tool. Missing
Skills/tools and unknown runtime state remain explicit limitations, not reasons
to install companions or bypass host rules.

## Evidence

Use `ACTUAL_PASS`, `ACTUAL_FAIL`, `STATIC`, `NOT_RUN` and `BLOCKED` per
material claim. Regression evidence is strong only when the original failure and
fixed pass were observed for the intended defect and adjacent checks passed.
Never reset or revert a user's working tree to manufacture red/green evidence.
Security review is likewise scoped evidence, not blanket certification.

## Adoption and removal

New projects select `--addon engineering-quality` during init. Existing projects
first preview/apply an explicit reviewed source update containing the add-on, then
add it to `veyrix.yml`, preview `sync --dry-run`, and sync. Removing it removes
only Veyrix-owned contributions; user edits still block unsafe removal, and manual
OMO settings remain user-owned.

No additional OpenCode command, custom agent, global installation or model eval is
introduced. The three management wrappers remain setup/sync/audit. Comparative
model-output evaluation is intentionally deferred.

## Derivation and limits

The new content is a bounded rewrite inspired by
`unofficialmmon/agent-reference@2053b47cd291db5d00d7c9df9932764aca7b3859`:
`global/ENGINEERING.md`, `prompts/CHANGE_AUDIT.md`, evidence concepts from
`verification-before-completion`, and trust-boundary questions from
`security-and-hardening`. These are conceptual inputs, not reactivated workflow
bundles. The historical migration decisions remain unchanged.

Deterministic tests cover configuration, deployment, protection and metadata.
Actual OpenCode/OMO loads, delegation and comparative model output remain NOT_RUN.
