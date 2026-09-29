---
name: mybatis
description: MyBatis mapper registration, XML and annotated statements, parameter/result mapping, dynamic SQL XML, transactions, caches, and Spring integration. Use when a project uses core MyBatis or mybatis-spring and the task concerns mapper behavior.
license: MIT
metadata:
  author: pi-dev-kit
  source-type: official-doc-derived
  reviewed: "2026-08-21"
---

# MyBatis

Treat mapper interfaces, statement IDs, XML namespaces, result mappings, and transaction ownership as one contract. Confirm the MyBatis and integration versions before applying configuration details.

## Official references

- https://mybatis.org/mybatis-3/
- https://mybatis.org/mybatis-3/sqlmap-xml.html
- https://mybatis.org/mybatis-3/dynamic-sql.html
- https://mybatis.org/spring/

This is an original pi-dev-kit summary derived from official MyBatis documentation.

## Mapper and statement identity

- A mapper XML namespace should match the mapper interface's fully qualified name.
- Statement IDs must match mapper method names when using interface binding.
- Verify mapper discovery (`@Mapper`, `@MapperScan`, explicit registration, or framework auto-configuration) before adding another scanner.
- Keep one clear owner for each query. Do not duplicate the same statement across generated and custom mappers.

## Parameters and results

- Use explicit `@Param` names or a parameter object when a statement has multiple logical inputs.
- Prefer `resultMap` when column/property mapping, nested objects, constructors, discriminators, or type handlers are material. `resultType` is appropriate for straightforward mappings.
- Confirm JDBC type and null behavior for nullable parameters and results.
- Keep SQL aliases stable when automatic snake-case/camel-case mapping is not sufficient.

## Dynamic SQL in XML

- Use `<where>`, `<set>`, and `<trim>` to avoid malformed leading/trailing operators.
- Use `#{}` for bound parameters. `${}` performs raw string substitution and is safe only for strictly controlled identifiers or fragments.
- For dynamic identifiers, validate against a closed application-owned allowlist before reaching mapper input.
- Keep locking clauses, pagination ordering, and vendor-specific syntax explicit and tested against the actual database.

## Transactions and sessions

- With mybatis-spring, transaction participation is owned by Spring's transaction manager and managed `SqlSession`; do not manually commit or close injected mapper sessions.
- Confirm proxy boundaries and rollback rules when `@Transactional` behavior appears missing.
- Executor type, first-level cache, second-level cache, and local cache scope can change visibility and memory behavior; change them only for a measured need.

## Validation

- Test mapper statements against the actual database dialect when SQL semantics matter.
- For XML, ensure mapper resources are included in the runtime artifact and namespace/statement IDs resolve.
- Verify affected row counts and concurrency behavior, not only returned objects.

## Review checklist

1. Trace mapper registration and XML resource loading.
2. Match namespace, statement ID, method signature, and result mapping.
3. Eliminate unsafe raw substitution.
4. Preserve transaction ownership.
5. Test vendor-specific SQL and locking behavior on the target engine.
