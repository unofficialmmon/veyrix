# Catalog acceptance

`catalog/skills.json` owns exact files, upstream/transfer provenance, preserved
licenses, status and limitations. `catalog/migration.json` owns all 95 decisions.
Nothing in this catalog is a blanket claim of correctness or model-output uplift.

The recovered seed contains 44 Skills: 21 external, 14 previously adapted, three
local-derived and six official-document-derived. It is 298 files / 1,381,907 bytes,
not counting catalog metadata or CLI code. No `.apm` distribution mirrors remain.
Each selection copies one complete Skill directory; references are not discarded
to make it look smaller. Root licenses are supplemented separately without editing
upstream files. The origin of those supplements is recorded.

The three existing local-derived references are api-contract, generated-code and
java-style. They were explicitly retained from the previous selection plan.
`java-style` now has a recorded Veyrix-local adaptation: its preserved transferred
`original_files` hash remains tied to agent-reference, while `adapted_files`
records the deployed bytes after selectively folding in framework-neutral naming,
immutability, Optional, generics/type-safety, null-handling and code-smell guidance
from the excluded `java-coding-standards` source at the same reviewed
agent-reference commit. Spring/Quarkus architecture examples, project-layout
templates and mandatory TDD/coverage guidance remain excluded. Framework-specific
guidance must respect the actual project version, formatter and maintained contracts.

## Known limits and conditional acceptance

Four entries are conditional: nestjs-best-practices, python-testing-patterns,
react-testing and swift-testing-expert. None appears in a base profile. Selecting
a matching add-on requires its ID in `accept_limitations` or the init argument
`--accept-limitations <id>`. Read the complete catalog limitations first. This is
not an instruction to excuse errors, override tests or use a failing recipe.

The imported Python testing snapshot retains a failing toy email-validator case
and a strict-mode async-fixture compatibility issue. Swift Testing retains an
invalid seconds-based time-limit example. React's JSDOM/axe result is not a color
contrast pass, and optional ECC companions are not bundled. These are the prior
agent-reference intake observations, NOT newly executed Veyrix language tests.
Python type-safety's Result example cannot represent a successful None result.
Keep existing project tools/styles instead of mechanically applying example
line lengths, new dependencies, type-checker migrations or TDD coverage targets.

Three existing problematic snapshots are deferred entirely: Kotlin coroutine
platform advice, Swift task-group cancellation guidance and Flutter's unkeyed
user cache architecture example. There is no silent substitute. Swift/iOS
currently offers design guidance and an optional testing Skill, not a complete
Swift concurrency implementation profile. Kotlin and Flutter coverage also has
explicit gaps. Supporting a language does not mean every language workflow is
covered or runtime-tested.

## Frontend craft

`frontend-craft` makes six references available to designer. Select by task;
it is not a command to load every body for every UI change:

| Task | Main reference |
| --- | --- |
| Landing/marketing/portfolio art direction | design-taste-frontend |
| Approved redesign of an existing UI | redesign-existing-projects |
| Component/interaction craft | emil-design-eng |
| Requested motion implementation | animate |
| Motion critique | review-animations |
| Web semantics/forms/accessibility quality review | web-design-guidelines |

Motion opportunity discovery and mobile-web polish are separate optional add-ons.
Emil is not a full dashboard information-architecture specification. Taste's
marketing scope must not be applied indiscriminately to complex product screens.
Existing project tokens, behavior and user constraints take precedence over
stylistic preferences. Missing companion Skills/tools remain missing; no implicit
installer or delegation framework is bundled to satisfy them.

The large Taste entrypoint is intentionally preserved. Catalog size and loaded
context are different; cost and result quality need matched host trials. CLI tests
cannot certify a better design. Impeccable remains external, with its own intended
owner and task boundaries; do not install duplicate same-ID copies.
