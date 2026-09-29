---
name: maven-build
description: Maven lifecycle, effective model, dependency management, plugin execution, profiles, reactor builds, wrappers, and reproducible validation. Use when diagnosing or changing Maven-specific build behavior.
license: MIT
metadata:
  author: pi-dev-kit
  source-type: official-doc-derived
  reviewed: "2026-08-21"
---

# Maven Build

Start from the effective Maven model, not only the visible `pom.xml`. Parent POMs, imported BOMs, active profiles, plugin management, user settings, and command-line properties can all own the observed behavior.

## Official references

- https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html
- https://maven.apache.org/pom.html
- https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html
- https://maven.apache.org/guides/introduction/introduction-to-profiles.html
- https://maven.apache.org/wrapper/

This is an original pi-dev-kit summary derived from official Apache Maven documentation.

## Model and dependency resolution

- Identify parent inheritance and imported BOMs before adding versions locally.
- `dependencyManagement` supplies defaults; it does not add a dependency. `pluginManagement` configures defaults; it does not necessarily execute a plugin.
- Use `mvn help:effective-pom`, `help:active-profiles`, and `dependency:tree` as diagnostics when inheritance or mediation is material. Do not generate or commit their output as project configuration.
- Dependency mediation generally selects the nearest declaration; direct declarations and managed versions can change the result. Confirm the effective tree rather than guessing.

## Lifecycle and plugins

- Map work to lifecycle phases (`validate`, `generate-sources`, `compile`, `test`, `package`, `verify`, `install`, `deploy`). Calling a later phase executes earlier bound phases.
- Distinguish a plugin goal invoked directly from an execution bound by ID. `plugin:goal@execution-id` requires that exact execution ID.
- Check execution phase, goals, inherited configuration, and profile activation before moving generated files or adding another execution.
- Treat `install` and `deploy` as mutating publication operations. Do not use them for routine validation when `verify` is sufficient.

## Profiles and properties

- Profiles alter the effective model; they are not general runtime feature flags.
- Confirm activation by command line, property, JDK, OS, file, or settings. Avoid depending on mutually exclusive implicit environment assumptions.
- User `settings.xml` and repository credentials are machine-local secrets. Never copy them into the project or reports.

## Multi-module reactors

- Read `<modules>` and packaging types to establish reactor order.
- Use `-pl` and `-am`/`-amd` only when the intended dependency direction is clear.
- Keep inter-module versions and dependency management consistent with the repository's release strategy.

## Reproducible validation

- Prefer `./mvnw` when present and verify wrapper properties/checksums under repository policy.
- Run the narrowest existing phase that proves the change, then escalate to `verify` when integration checks are relevant.
- Do not add repositories, mirrors, plugin groups, or version ranges as speculative fixes.

## Review checklist

1. Resolve parent, BOM, profiles, and effective plugin execution.
2. Explain the lifecycle phase that owns the behavior.
3. Preserve wrapper and repository conventions.
4. Avoid publication phases for local validation.
5. Report external repository or credential requirements explicitly.
