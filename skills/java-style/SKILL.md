---
name: java-style
description: Java/Spring formatting, linting, import ordering, member ordering, DTO/record style, Lombok constructor safety, conditions, streams, logging, and MyBatis Generator formatting boundaries. Use when creating or cleaning up handwritten Java/Spring source, reviewing Java style consistency, fixing formatter/linter findings, or deciding how to format a changed Java file without broad refactoring.
license: MIT
compatibility: opencode
metadata:
  source: "user Development Formatting and Linting Guide"
  ownership: "agent-reference"
---

# Java Style

Follow repository rules before this Skill. The project's formatter, linter, `AGENTS.md`, maintained local conventions, generated-code ownership, and explicit user instructions take precedence.

## Formatting is not refactoring

Formatting or lint cleanup must preserve behavior and contracts.

Unless explicitly in scope, do not:

- rename classes, methods, fields, parameters, or locals;
- move classes/packages;
- change API paths, signatures, DTO meaning, serialized names, exception flow, or logging semantics;
- convert loops to streams or streams to loops merely for style;
- introduce helpers or abstractions solely to satisfy formatting preferences;
- extract a simple helper used once when keeping the logic inline is clearer;
- convert an existing DTO class to a record;
- reorder a large established class only for cosmetic consistency;
- format unrelated files;
- modify generated source.

Keep the diff local and reviewable.

## JavaDoc for handwritten source

For handwritten Java/Spring source, use the repository's established language
for concise JavaDoc focused on business and wire semantics. Document meaningful
parameters with `@param`, non-void public methods with `@return`, and
contract-significant exceptions with `@throws`.

- DTO records explain business meaning, wire meaning, and relevant nullability.
- Controllers explain endpoint purpose, authentication/context requirements,
  and request parameters.
- Services explain the business action and meaningful actor or state rules.
- Avoid comments that merely restate obvious code.
- Do not modify or add application-level JavaDoc to generated/tool-owned source.

## Line wrapping

Treat line length as a readability boundary, not a target.

When the repository has no stricter configured rule, approximately 180 characters is a practical upper boundary for a simple Java declaration or invocation.

- Keep a short, structurally simple declaration or call on one line when easy to scan.
- Wrap earlier for complex nested types, annotations, lambdas, conditions, or multiple logical stages.
- When wrapping a method declaration, put one parameter per continuation line and keep its annotations with it.
- When wrapping fluent code, prefer one meaningful chain step per line.
- Do not create temporary variables solely to avoid wrapping; introduce one when it names a real business concept, supports reuse/debugging, or separates processing stages.

## Imports

Use the project's configured import order when one exists. Otherwise use:

1. static imports;
2. `java.*`;
3. `jakarta.*`;
4. third-party libraries;
5. project packages.

Use one blank line between groups and alphabetical order inside each group.

- No wildcard imports.
- Remove unused imports in changed handwritten source.
- Keep project packages distinct from external packages.
- Do not reorganize generated imports manually.

## Member ordering

When consistent with the repository, prefer:

1. `static final` constants;
2. other static fields;
3. dependency fields;
4. other instance fields;
5. constructors;
6. public methods;
7. protected/package-private methods;
8. private helpers;
9. nested classes, records, or enums.

Preserve established interface order or business-flow order when that is clearer. Do not create a broad diff solely to reorder members.

### Controllers

Prefer dependency fields, constructor/Lombok constructor annotation, endpoint methods, then private helpers. Keep controllers focused on transport/orchestration according to the repository's architecture.

### Services

Prefer constants, dependencies, constructor, primary public entry points, supporting public methods, then private validation/lookup/mapping helpers. Preserve an established business-flow order over mechanical sorting.

## Annotations

Keep project annotation order. A reasonable fallback for classes is:

1. framework stereotype;
2. Lombok annotation;
3. mapping/configuration annotation;
4. documentation/security/custom annotations.

Do not add, remove, or semantically change annotations as formatting-only work.

## JavaDoc

For handwritten Java/Spring source where the repository or project language requires documentation:

- Begin the JavaDoc with a concise summary in the repository or project's language; use Korean only when that language or its conventions call for it.
- Document meaningful parameters with `@param`, non-void public methods with `@return`, and contract-significant exceptions with `@throws`.
- Document DTO records in terms of business meaning, wire representation, and nullability; controllers in terms of endpoint, authentication, and request meaning; and services in terms of business action, actor, and state semantics.
- Explain business or wire contracts rather than restating obvious code. Exclude generated and other tool-owned source.

## Constructor and Lombok safety

Prefer Lombok `@RequiredArgsConstructor` with required `final` dependencies for straightforward dependency injection. Replace an explicit constructor with it only when the constructor merely assigns those dependencies and generated-constructor behavior is equivalent.

Keep an explicit constructor when it contains or depends on:

- `@Qualifier`, `@Lazy`, or custom injection annotations;
- multiple same-typed beans requiring explicit selection;
- argument transformation or validation;
- collection-to-map/registry construction;
- any behavior beyond direct assignment.

Do not assume constructor-parameter annotations are copied by Lombok unless project configuration guarantees it.

Avoid nullable compatibility constructors unless an actual caller contract requires them.

Avoid broad class-level Lombok mutability such as `@Data` or `@Setter` unless that mutability is intentionally part of the design.

## DTOs and records

For new immutable request/response DTOs, records are a reasonable default only when framework compatibility and repository convention support them and the type does not require inheritance, mutable setters, or JavaBean-specific behavior.

Do not convert an existing DTO class to a record during formatting-only work. Such conversion can alter serialization, validation placement, reflection, getter conventions, fixtures, inheritance, and framework binding.

## Enums

When repository convention does not say otherwise, order enum content as:

1. constants;
2. fields;
3. constructor/Lombok constructor annotation;
4. methods.

Do not reorder constants when order has semantic, serialization, test, or external-contract meaning.

For simple string/DB-code enums, prefer a `code` field with `getCode()` and `fromCode(String)`;

## Conditions

- Always use braces.
- Keep simple guard clauses compact.
- For multiline complex conditions, keep operator placement consistent with the project; when no rule exists, leading continuation operators are preferred for scanability.
- Avoid nested ternaries.
- Do not rewrite conditions merely to make them shorter during formatting cleanup.

## Streams and lambdas

A short obvious pipeline may remain on one line. Use one operation per line when there are several stages or a lambda body.

Do not convert loops and streams into each other as formatting-only work.

## Logging and exceptions

- Prefer parameterized logging over string concatenation.
- Do not leave `System.out`, `System.err`, or `printStackTrace` in production code unless explicitly intentional.
- No empty catch blocks or silently swallowed exceptions.
- Avoid broad exception catches/declarations unless the boundary genuinely requires them.
- If an exception is intentionally ignored, document why and keep the ignored scope narrow.
- Do not change exception type or error payload merely for cleanup.

## MyBatis Generator boundary

Do not manually modify MyBatis Generator output unless explicitly requested with overwrite risk understood.

Typical generated areas include generated `model`, `mapper`, `support`, and files marked `@Generated`. Apply handwritten formatting rules to domain/service/controller/adapter/DTO code instead.

Use the `generated-code` Skill when generation ownership or regeneration is part of the task.

## Validation

Use the repository's actual formatter/linter commands first.

For formatting/import-only changes, run the formatter/linter and compile when appropriate. For source-level changes such as constructor conversion, run compilation and the closest relevant tests. DTO/framework-boundary changes require focused serialization/controller/injection/contract validation rather than being treated as formatting-only.

Report exactly what ran. A formatter PASS does not prove behavior, and failed/not-run/blocked validation must remain visible.
