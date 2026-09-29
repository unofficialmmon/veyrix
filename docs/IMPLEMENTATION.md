# Veyrix v0.1.0 implementation checkpoint

## Recovered basis

- Main: `ab7bc60394a6d9154bbb7770492f745095e97ed4` (bootstrap README).
- Preserved seed: `8a262981fd4f3a746c428e1669d504de4a03ecf7`.
- Independently reconstructed seed tree: `356d38a4b0e4722882aa00e2a3e565cacc13fe7f`.
- 44 complete selected Skill directories with origin hashes and license supplements.
- The previous report of 50 passing tests is NOT reused: the corresponding CLI/test files were not recovered.

## Delivery scope

Implement an explicitly invoked project configurator, not an agent runtime:

1. Bare Git object cache; exact-commit source reads, no user working checkout and no executing cached scripts.
2. Explicit versioned profiles/add-ons; stable selected IDs and role-specific OMO `skills_add`.
3. `.agents/skills` copies with a pin/lock and ownership ledger; preview, changed-file protection, bounded removal, rollback evidence and repeated-sync NOOP.
4. Surgical JSONC changes preserving user models, MCPs, permissions, comments and unrelated grants. Do not silently shadow an existing `.json` with a generated `.jsonc`.
5. Source integrity/license validation, all 95 agent-reference migration decisions with reasons, and focused tests.
6. PR and merge only after tests/CI and final-tree verification. No edits to agent-reference or user projects; no repository visibility changes.

## Evidence boundaries

CLI fixtures are not OpenCode/OMO runtime tests. Installing/discovering a Skill is not evidence that a model invoked it or produced a better result. Preserved upstream limitations remain visible and conditional Skills require explicit acceptance. Authenticated private-Git, native macOS host use and runtime discovery will remain NOT RUN unless actually exercised.

Status: recovery checkpoint. Completion results will replace this status before release.
