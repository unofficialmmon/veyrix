---
name: mybatis-dynamic-sql
description: MyBatis Dynamic SQL DSL, generated support classes, rendering strategies, mapper mixins, selective inserts/updates, joins, aliases, and custom statement integration. Use when `org.mybatis.dynamic-sql` APIs or generated DynamicSqlSupport classes are present.
license: MIT
metadata:
  author: pi-dev-kit
  source-type: official-doc-derived
  reviewed: "2026-08-21"
---

# MyBatis Dynamic SQL

Use this Skill only when the repository uses the MyBatis Dynamic SQL library or generator runtime. Do not confuse it with MyBatis XML `<if>`/`<where>` dynamic SQL.

## Official references

- https://mybatis.org/mybatis-dynamic-sql/docs/introduction.html
- https://mybatis.org/mybatis-dynamic-sql/docs/select.html
- https://mybatis.org/mybatis-dynamic-sql/docs/insert.html
- https://mybatis.org/mybatis-dynamic-sql/docs/update.html
- https://mybatis.org/mybatis-dynamic-sql/docs/mybatis3.html

This is an original pi-dev-kit summary derived from official MyBatis Dynamic SQL documentation.

## Generated support boundary

- Generated `*DynamicSqlSupport` classes define tables and columns; generated mapper interfaces provide common operations. Treat both as generator-owned unless the repository explicitly says otherwise.
- Put domain-specific query composition in human-owned services, repositories, or custom mapper methods rather than editing generated files.
- Static imports improve DSL readability but can hide cross-domain persistence access. Preserve domain ownership rules.

## Rendering and execution

- Use the rendering strategy required by the integration, commonly `RenderingStrategies.MYBATIS3`.
- Build statements first, render once, and pass the provider object expected by the mapper annotation or XML statement.
- Keep table aliases consistent across joins, selected columns, order clauses, and qualified subqueries.
- Confirm the library version for DSL features; generated code and runtime library must be compatible.

## Inserts and updates

- Choose among full, selective, multi-row, and batch insert based on null/default semantics and driver/database limits.
- Selective mapping omits null properties; it is not equivalent to explicitly writing SQL `NULL`.
- In updates, construct the `where` clause deliberately. Never make a missing predicate silently mean whole-table update.
- For compare-and-set or optimistic updates, include the expected current value/version in the predicate and verify affected rows.

## Selects, joins, and pagination

- Select only required columns and define deterministic ordering before pagination.
- Qualify ambiguous columns in joins. Use explicit result mappings for joined/nested results when automatic mapping cannot express the shape.
- Preserve database-specific pagination and locking semantics; the DSL does not make SQL portable automatically.

## Extension points

- Prefer documented custom mapper methods and statement providers over forking generated common methods.
- Reusable conditions or rendering helpers should remain local until repeated use demonstrates a shared abstraction.
- XML result maps may be paired with Dynamic SQL statements for complex result shapes; keep statement and result-map ownership clear.

## Review checklist

1. Confirm Dynamic SQL and generated-code versions.
2. Identify generated versus human-owned files.
3. Check rendering strategy and mapper method contract.
4. Verify null/default, affected-row, ordering, and locking semantics.
5. Test rendered SQL against the actual target database.
