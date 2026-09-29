# Implementation decisions and recovery

## Recovered basis

Main began at `ab7bc60394a6d9154bbb7770492f745095e97ed4` (README only).
`feat/v0.1.0` preserved seed `8a262981fd4f3a746c428e1669d504de4a03ecf7`, whose
independently reconstructed tree was `356d38a4b0e4722882aa00e2a3e565cacc13fe7f`.
It had 44 complete Skill directories and provenance, but no recoverable CLI/tests.
The earlier reported 50-test pass is not reused as evidence for this delivery.

## v0.1 decisions

| Decision | Reason |
| --- | --- |
| Python 3.11+ CLI, PyYAML pinned | Small cross-language configurator, no daemon or native build toolchain. |
| Bare Git cache, exact SHA apply | No developer checkout/pull management; independent project pins. |
| Explicit profiles/add-ons | Same declared selection yields the same managed IDs, without model stack guessing. |
| Three installed wrapper prompts | Bounded lifecycle entry points, not inherited 12-command orchestration. |
| Skills copied in full | Keep licenses/resources and per-project revision isolation; no moving symlink targets. |
| OMO skills_add contributions | Preserve global/user capability rather than overwrite an effective allowlist. |
| Existing .json OMO blocks | Avoid creating a .jsonc that silently shadows user config. |
| Existing AGENTS never generated/rewritten | Project facts need repository-specific authoring, not generic guesses. |
| No APM owner adoption in this release | Copying over APM files would create two deployment owners. |
| Conditional entries opt-in | Preserve original defects/limits honestly without making them defaults. |
| No new local coding guidelines | Carry only previously selected originals, with local/adapted provenance retained. |

The initial design mentioned ~30 Skills and later reports mentioned 42. The
recoverable pinned seed contains **44**; this delivery preserves that concrete
reviewable inventory rather than inventing a lost subset. Of 95 old entries,
43 are kept, 49 excluded and 3 deferred; Emil design-engineering is the 44th.

## Completion boundaries

The implemented surface is init/sync/update/audit/info, explicit selection,
complete source verification, managed-file protection, surgical JSONC additions,
collision checks, private recovery and focused regression tests. No user project,
agent-reference repository, repository visibility or global environment is changed
by this repository delivery. Actual target-host activation stays NOT RUN.

Durable implementation and CI results are attached to the recovery pull request;
[VALIDATION.md](VALIDATION.md) describes their scope and remaining limitations.
