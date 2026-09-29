---
name: regression-proof
description: Establish whether a bug fix is protected by a test or bounded reproduction that detects the original failure. Use for bug fixes, regression-test requests, and review of claims that a defect cannot recur. Distinguish pre-fix failure evidence from a test that only passes after the fix; never require destructive checkout or automatic reversal of user work.
---

# Regression Proof

Identify the original symptom, violated contract, owning boundary, relevant input
and affected state. Read the project's test conventions and current worktree.
A passing compile or a newly added test alone is not regression detection proof.

## Evidence path

1. Locate or create a focused scenario for the original behavior, within the
   authorized implementation scope. During read-only review, inspect existing
   tests/evidence and propose missing coverage without editing.
2. When safe and authorized, establish failure on the pre-fix implementation in an
   isolated disposable copy/worktree. Prefer existing applicable failure evidence
   when available. Never reset, clean, stash, checkout over, or revert the user's
   working tree to manufacture a red/green result.
3. Confirm that failure detects the intended defect, not missing dependencies,
   a syntax error, an unrelated exception or different fixture input. If a new test
   is applied to the old implementation, explain any setup adjustment and its limits.
4. Run the same relevant scenario against the fixed implementation and inspect its
   assertions/output. Check adjacent positive, negative and boundary behavior as
   appropriate. Do not weaken assertions or mock away the defect to make it pass.
5. Compare the actual tested states and inputs. Refresh affected checks after later
   edits; keep environmental or concurrent-change uncertainty visible.

## Report the strength of the evidence

- `STRONG`: the relevant pre-fix failure and post-fix pass were actually observed,
  the failure reason matches the defect, and relevant adjacent checks passed.
- `PARTIAL`: targeted coverage and/or a bounded post-fix scenario passed, but a safe
  pre-fix reproduction, comparable environment or adjacent validation is missing.
- `NONE`: no behavior-level regression evidence, such as compile-only verification.

Report execution status separately with `ACTUAL_PASS`, `ACTUAL_FAIL`, `STATIC`,
`NOT_RUN`, or `BLOCKED`. Include the scenario/test identifier, observed pre/post
results, state compared, adjacent checks and any limitation. A post-fix failure
means the repair is not verified, regardless of how good the pre-fix evidence is.

No test guarantees that every future regression is impossible. Do not force TDD,
unsafe historical reproduction, production access, dependency installation, or a
particular agent sequence. OMO Slim owns orchestration; project rules and host
permissions still govern execution. This Skill supplies evidence criteria only.
