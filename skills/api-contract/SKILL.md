---
name: api-contract
description: HTTP/OpenAPI contract design, change, validation, and compatibility guidance. Use when adding, changing, reviewing, or removing an HTTP API; editing an authoritative OpenAPI document; checking request/response wire shape; or assessing whether an API change is breaking.
license: MIT
compatibility: opencode
metadata:
  source: "OMP API-CONTRACT and CODEGEN safe-evolution principles"
  ownership: "agent-reference"
---

# API Contract

Use repository authority first. This Skill does not introduce OpenAPI into a repository that does not already treat it as an authoritative contract.

## Find the contract owner

Before implementing an HTTP API change:

1. Read project `AGENTS.md` and relevant maintained API/architecture docs.
2. Identify the repository-declared authoritative API contract, if one exists.
3. Find the existing operation and implementation boundary it maps to.
4. If candidate contracts conflict, report the conflict instead of choosing silently.
5. If no authoritative OpenAPI exists, follow the repository's established API documentation practice rather than introducing one solely because this Skill exists.

## Model the actual wire contract

Treat client-visible behavior as the contract:

- path and method;
- path/query/header parameters;
- request body and required/optional/nullability semantics;
- response body and established response envelope;
- success and error status codes;
- relevant headers;
- enum/type/required semantics.

Do not document only an inner payload when the real response wraps it.

## Contract-first repositories

When the repository declares a machine-readable contract as source of truth, prefer:

```text
request
→ inspect accepted contract and implementation
→ update proposed contract
→ assess compatibility and impact
→ regenerate owned artifacts when applicable
→ implement human-owned behavior
→ project validation
→ contract validation/compatibility check
```

Do not force this sequence on repositories whose source of truth is different.

## Compatibility baseline

For a tracked contract in Git, the accepted baseline is normally the tracked `HEAD` version and the candidate is the working-tree version.

Prefer the repository's existing validator. When `oasdiff` is already part of the workflow or explicitly chosen, typical checks are:

```bash
oasdiff validate --fail-on ERR <candidate>
oasdiff breaking --fail-on ERR <baseline> <candidate>
```

A new/untracked contract or repository without a meaningful baseline may be validated, but backward compatibility is **not established** and must not be reported as PASS.

## Breaking changes

Treat confirmed wire incompatibility as a product/API decision, including:

- removing endpoint/method/path;
- adding required input;
- removing response fields;
- incompatible type changes;
- required/nullability semantic changes;
- enum narrowing;
- removing accepted success responses;
- changing the established response-envelope shape.

Do not silently ship a confirmed breaking public contract.

## Generated API artifacts

If DTO/controller/client/service-contract files are generator-owned, do not patch the generated output merely to match the contract. Load the `generated-code` Skill and change the owning contract/schema/configuration when that is the supported repository path.

A generator may own mechanical API shapes while business rules, authorization, orchestration, and repository-specific integration remain human-owned. Generation completion is not feature completion.

Removing an API operation may retire generated artifacts, but it does not automatically authorize deletion of unrelated human implementation. Check remaining callers and ownership.

## Verification layers

Keep evidence separate:

1. contract syntax/schema validity;
2. backward-compatibility comparison;
3. generated-source consistency;
4. compile/typecheck;
5. focused application tests;
6. integration/runtime behavior.

A PASS at one layer does not prove the others.

Report what was actually run, what was only reviewed statically, and what was not run or blocked.
