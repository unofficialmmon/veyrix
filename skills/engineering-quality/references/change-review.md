# Change review

Review the current change without fixing findings or rewriting user work.

1. Establish the requested outcome and acceptance conditions. Identify the diff
   base or working-tree scope, including relevant untracked files. Separate prior
   user work where evidence permits; report uncertain attribution.
2. Read the nearest applicable project instructions, contracts, source and tests.
   Inspect enough surrounding control/data flow to substantiate each finding.
3. Prioritize missing behavior, wrong-layer or symptom-only repairs, invalid-state
   masking, broken API/DB/auth contracts, ownership violations, unnecessary scope,
   and tests that do not exercise the claim. Inspect maintainability only where it
   creates a concrete change cost or defect risk; do not impose a new style.
4. Check that reported verification applies after the last relevant change.
   A successful formatter, compile, fixture or unrelated test is not proof of the
   requested behavior. Do not weaken a failing test to remove a finding.
5. Report significant findings with severity (`HIGH`, `MEDIUM`, `LOW`), exact
   file/symbol or verified line range, evidence, consequence and smallest correction
   direction. Separate a confirmed defect from an unverified concern.

Conclude with scope match (`PASS`, `PARTIAL`, `FAIL`, `UNVERIFIED`), claim-specific
verification evidence, and important areas actually inspected without findings.
If the original request is unavailable, scope is `UNVERIFIED`, not inferred from
the implementation. A lack of findings is scoped to the reviewed material, not a
claim of universal correctness or security.

Read-only review does not authorize installing dependencies, running side-effecting
scripts, modifying tests, or applying remediation. Follow existing authorization
for any execution needed to substantiate a finding.
