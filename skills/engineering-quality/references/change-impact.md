# Change impact

Map the plausible impact before expanding a consequential change. This is a
bounded investigation, not permission to modify every affected component.

Start from changed symbols, data structures and configuration. Follow direct
callers and consumers, then only the relevant boundaries:

- public API, serialized data, DB schema, events and messages;
- module/process ownership, transactions, authentication and authorization;
- generated clients/mappers and their source schemas or generator configuration;
- tests, fixtures and supported user journeys covering those consumers;
- compatibility, configuration defaults, migrations and deployment assumptions.

Use source and authoritative contracts to verify search/index results. Record
whether a relationship was directly observed or inferred, and explain limits for
reflection, dynamic discovery, unavailable downstream repositories or runtime-only
consumers. An empty search result does not establish that no consumers exist.

Return a compact map: changed surface -> affected consumer/contract -> evidence ->
needed verification. Label impacts inside the approved scope separately from
`AFFECTED_OUT_OF_SCOPE`; do not automatically edit the latter. Report unresolved
compatibility decisions before an irreversible change, while continuing work that
is independent and already authorized.

Do not run migrations, deploy, rewrite schemas or install tools just to complete
this map. Do not turn observations into new project-wide policy.
