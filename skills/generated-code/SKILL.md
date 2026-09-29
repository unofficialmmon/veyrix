---
name: generated-code
description: Generated and tool-managed source ownership guidance. Use when a repository contains MyBatis Generator output, OpenAPI-generated clients or DTOs, schema-generated models, protocol bindings, generated SDKs, or any source whose supported change path is through a contract, schema, configuration, or generator rather than direct editing.
license: MIT
compatibility: opencode
metadata:
  source: "CODEGEN ownership and safe-regeneration principles"
  ownership: "agent-reference"
---

# Generated Code

Treat generated/tool-managed source as an ownership boundary, not merely a formatting convention.

## Prove ownership

Before deciding a file is generated or managed, look for repository evidence:

- generator configuration;
- generated annotations or headers;
- build plugin/task;
- documented managed directories;
- contract/schema source of truth;
- established regeneration command.

Do not label ordinary human source as generated because it looks repetitive.

## Change the owner, not the output

When a generated file needs to change, prefer:

```text
contract / schema / generator configuration
→ generation
→ generated diff review
→ required human implementation changes
→ compile/test
```

Do not patch output that regeneration will overwrite unless the user explicitly requests an exceptional workaround and the risk is understood.

## Scope of authority

Generated source is strong evidence for what the generator owns, such as:

- schema fields and generated types;
- generated mapper/query capability;
- generated API/client shapes;
- generator naming/configuration.

It is not automatically authority for:

- product scope;
- service/controller architecture;
- domain ownership;
- business semantics;
- human package conventions.

## Prefer existing generated capability

Use an existing generated capability before creating a handwritten parallel path when it already satisfies the need.

Examples:

- generated MyBatis Mapper / Dynamic SQL before a CustomMapper/XML query when sufficient;
- generated client/transport types before duplicate handwritten transport models when the repository contract makes them authoritative.

Create handwritten custom behavior for demonstrated gaps, not preemptively.

## Human work remains explicit

After generation, identify remaining human-owned work such as:

- business rules;
- authorization;
- transactions and state transitions;
- domain mapping;
- integration behavior;
- cleanup of genuinely retired human code.

Never report a feature complete merely because generation succeeded.

## Safe regeneration

Before running a generator:

1. inspect working-tree changes in generated and human-owned areas;
2. identify the configured generation target and owner;
3. prefer a narrow target when the repository supports it;
4. run the repository's official generation command;
5. inspect generated diff separately from human diff;
6. verify unrelated user changes were not overwritten.

If regeneration would overwrite uncommitted user work, stop and surface the conflict rather than discarding it.

When tooling offers preview/dry-run, treat the preview as evidence for that repository state. Re-preview after material contract/config/source changes.

## Deletion

Generated-file retirement and human-source deletion are separate decisions. Removing a schema/operation may remove generated artifacts, but human code must be checked for remaining ownership/callers before deletion.

## Verification layers

Report separately:

- generator command actually run;
- generated diff reviewed;
- generated consistency checks;
- compile/typecheck;
- focused application tests;
- runtime/integration verification;
- not-run or blocked checks.

Generated consistency does not prove application correctness.
