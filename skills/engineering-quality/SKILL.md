---
name: engineering-quality
description: Review a code change against its requested scope, assess cross-boundary impact and architecture consistency, or verify completion with claim-specific evidence. Use for code review, meaningful multi-module or public-contract changes, and before reporting an implementation complete. Select only the relevant reference; this is not an orchestration or mandatory full-review workflow.
---

# Engineering Quality

Establish the requested outcome, applicable project instructions, relevant diff,
and the current source of truth. Preserve pre-existing user changes. Treat a
review request as read-only unless implementation is separately authorized.

## Select the smallest relevant reference

| Need | Read |
| --- | --- |
| Review a proposed or completed change | [Change review](references/change-review.md) |
| Cross-module, API, DB, event, configuration or generated-contract change | [Change impact](references/change-impact.md) |
| Changed dependency direction, ownership, state or architectural boundary | [Architecture consistency](references/architecture-consistency.md) |
| Claim that implementation, verification or a repair is complete | [Completion verification](references/completion-verification.md) |

For a small local correction, use completion verification without automatically
loading the other references. For a bug fix, use `regression-proof` if available
and permitted. For a changed trust boundary, use `security-review` if available
and permitted. Do not read denied Skills directly, install missing Skills, or
claim a specialist review occurred when it did not.

## Shared contract

- Apply repository-specific policy before generic recommendations. Investigate
  policy/source conflicts; do not silently redefine architecture from current code.
- Detect affected but out-of-scope consumers without automatically changing them.
- Judge root-cause ownership and requested behavior, not stylistic preference or
  the number of tests. Do not invent findings to fill a report.
- Separate `ACTUAL_PASS`, `ACTUAL_FAIL`, `STATIC`, `NOT_RUN`, and `BLOCKED`.
  Tie each statement to the actual diff, command, observation or contract it covers.
- Scale reporting to the work. No fixed review count, new agent roles, mandatory
  delegation sequence, task database, or automatic commits/PRs/deployments.

OpenCode owns host permissions; OMO Slim owns orchestration. Veyrix supplies this
opt-in guidance, not runtime enforcement. Global and project `AGENTS.md` remain
user/project-owned. Catalog presence or a successful copy is not a Skill-load or
model-quality result.
