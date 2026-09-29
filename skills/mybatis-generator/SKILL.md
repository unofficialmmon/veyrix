---
name: mybatis-generator
description: MyBatis Generator configuration, target runtimes, introspection, generated model/client/support output, plugins, regeneration ownership, and MyBatis Dynamic SQL integration. Use when MBG XML/Java configuration or generated mapper/model/support sources are present.
license: MIT
metadata:
  author: pi-dev-kit
  source-type: official-doc-derived
  reviewed: "2026-08-21"
---

# MyBatis Generator

Treat generator configuration and schema metadata as the source of truth for generated artifacts. Do not repair generator-owned output by hand when the owning configuration can produce the correction.

## Official references

- https://mybatis.org/generator/
- https://mybatis.org/generator/configreference/xmlconfig.html
- https://mybatis.org/generator/configreference/context.html
- https://mybatis.org/generator/generatedobjects/dynamicSqlV2.html
- https://mybatis.org/generator/reference/plugins.html
- https://mybatis.org/generator/running/runningWithMaven.html

This is an original pi-dev-kit summary derived from official MyBatis Generator documentation.

## Configuration flow

Map the complete path before changing output:

```text
build profile/plugin execution
  → generator configuration file
  → properties and JDBC connection
  → database metadata introspection
  → context targetRuntime/plugins
  → model/client/support generators
  → targetProject and targetPackage
  → compile/source-control treatment
```

A generated-source directory seen in build output is not the source of truth if configuration writes elsewhere.

## Context and runtime

- Confirm `targetRuntime`. `MyBatis3DynamicSql` generates a different artifact shape from legacy XML mapper runtimes.
- Check `defaultModelType`, delimiters, beginning/ending delimiters, catalog/schema, and `nullCatalogMeansCurrent` against the actual database.
- Keep the MBG core/plugin version aligned with the generated runtime APIs.

## Introspection

- Each `<table>` mapping controls identity, domain object naming, ignored columns, generated keys, type overrides, and runtime catalog/schema behavior.
- Database remarks, nullability, keys, and JDBC metadata affect generated output. Regeneration against the wrong schema can create a large but internally consistent wrong diff.
- Use an explicit table filter only when the execution and configuration support it; verify what was actually regenerated.

## Output ownership

- `targetProject` determines whether generated files land in a committed source tree or a generated build directory.
- If output is under `src/main/java`, normal compilation usually sees it without build-helper registration. If output is under `target/generated-sources`, confirm the build registers that source root.
- Generated files may be committed when the repository requires reproducible builds without database access. Follow repository rules for formatting exclusions and review.
- Never mix human SQL or domain behavior into files that regeneration overwrites. Use custom mappers, extension interfaces, XML, or services according to the chosen runtime.

## Plugins

- Plugins can add annotations, interfaces, nullness metadata, rename artifacts, or change generated methods. Read plugin ordering and version compatibility before removing apparently redundant output.
- Distinguish built-in plugins from project-local plugin classes and inspect their source when output cannot be explained by XML alone.

## Safe regeneration

1. Record the current Git status and protect unrelated user changes.
2. Confirm the exact database/schema and credentials source without printing secrets.
3. Run the repository's documented generator execution.
4. Review the complete generated diff for unexpected table or type changes.
5. Run compile/tests that consume the generated API.
6. Do not commit credentials, `.env`, generated logs, or temporary database artifacts.

## Common traps

- Running a direct plugin goal instead of the configured execution ID.
- Assuming Maven property placeholders are resolved without the profile/plugin that loads them.
- Regenerating every table when only one configured context was intended.
- Editing generated mapper methods instead of fixing configuration or adding a custom extension.
- Registering a generated source root that is already inside `src/main/java`.
