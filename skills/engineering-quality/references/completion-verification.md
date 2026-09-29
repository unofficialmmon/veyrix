# Completion verification

Separate implementation status from verification status. Use the project's
required checks and add only checks proportional to the changed contracts and risk.

Before making a success claim:

1. Reconcile requested outcomes with the final integrated change. Account for
   unresolved findings and affected out-of-scope consumers.
2. Identify what observation or command would actually demonstrate each important
   claim. Confirm test selection exercised relevant cases rather than zero tests,
   skipped work, mocked-away behavior or an unrelated successful target.
3. Inspect script prerequisites and side effects. Execute within existing approval;
   do not install, regenerate, deploy or mutate production data merely to obtain a
   green report. Preserve user changes and existing protection rules.
4. Read the exit result and relevant output. Check resulting state independently
   when a consequential write is part of the requested task.
5. Reuse evidence only while its target, inputs and relevant state remain applicable.
   After a relevant edit, rerun the affected check or disclose stale evidence. A new
   chat message alone does not invalidate an otherwise unchanged verified state.

Report each material claim using:

| Status | Meaning |
| --- | --- |
| `ACTUAL_PASS` | The stated command/scenario ran and succeeded for its stated scope. |
| `ACTUAL_FAIL` | It ran and failed; include the relevant failure and remaining impact. |
| `STATIC` | Source/configuration/documentation was inspected, without execution proof. |
| `NOT_RUN` | Relevant execution was not performed; state why and what remains unknown. |
| `BLOCKED` | A prerequisite, permission or conflict prevented the needed check/work. |

Connect evidence to command/method, working directory or target, and result.
Compilation is not a test run; tests are not compatibility/deployment proof unless
they exercise those properties. A scanner's clean output is not full security
assurance. Installed files and static grants are not actual host Skill activation.

Do not claim verified completion when required checks failed or remain unexecuted.
Report the implemented portion and exact unverified boundary instead. Do not
create an elaborate report or persistent tracking files for a trivial change.
