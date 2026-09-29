# Architecture consistency

Check the project's architecture; do not substitute a preferred architecture.

Find applicable `AGENTS.md`, maintained design/ADR documents, dependency rules,
build constraints, contract ownership and representative neighboring source.
Distinguish explicit policy from observed implementation. When they disagree,
identify the conflict rather than declaring the implementation authoritative.

Trace only the boundaries touched by the change: permitted dependency direction,
module responsibility, state/transaction ownership, public interfaces and generated
or vendored ownership. Check reverse/circular dependencies, hidden shared state,
wrong-layer fixes and abstractions without a demonstrated variation or isolation
need. Preserve intentional project exceptions instead of normalizing them away.

Do not infer human architecture from generated output. Inspect the schema,
generator configuration or maintained contract for the portion the generator owns.
Do not prescribe Controller/Service/Repository, clean architecture, dependency
injection or a new module hierarchy merely because the stack can support it.

Report `CONSISTENT`, `VIOLATION`, or `UNVERIFIED` with the boundary, authority and
specific evidence. `CONSISTENT` means consistent with the identified constraints
within the inspected scope, not a full-system architecture certification. With no
reliable authority or conflicting patterns, report observations and uncertainty;
never manufacture a rule to obtain a passing result.
