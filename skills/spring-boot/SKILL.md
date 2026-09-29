---
name: spring-boot
description: Spring Boot configuration, auto-configuration, profiles, externalized configuration, application startup, testing slices, and executable packaging. Use when a repository uses Spring Boot and the task concerns Boot-specific runtime or build behavior.
license: MIT
metadata:
  author: pi-dev-kit
  source-type: official-doc-derived
  reviewed: "2026-08-21"
---

# Spring Boot

Use repository evidence first: the Spring Boot parent or BOM, starter dependencies, application class, configuration files, active profiles, and tests. Confirm the project's Boot version before applying version-sensitive guidance.

## Official references

- https://docs.spring.io/spring-boot/reference/
- https://docs.spring.io/spring-boot/reference/features/external-config.html
- https://docs.spring.io/spring-boot/reference/using/auto-configuration.html
- https://docs.spring.io/spring-boot/reference/testing/
- https://docs.spring.io/spring-boot/maven-plugin/

This is an original pi-dev-kit summary derived from the official references; it does not copy an upstream Skill.

## Configuration ownership

- Prefer typed `@ConfigurationProperties` for service-owned settings. Keep framework settings under their standard `spring.*`, `server.*`, and management namespaces.
- Resolve property precedence before changing defaults: command-line arguments, environment variables, system properties, profile-specific files, and base configuration can override one another.
- Treat profile activation and profile groups as deployment inputs. Do not silently hardcode an active profile in shared application configuration.
- Keep secrets outside committed configuration. Placeholder syntax does not make a secret safe if the fallback contains a real credential.

## Auto-configuration

- Inspect the condition report or relevant `@Conditional*` annotations before replacing Boot auto-configuration with manual beans.
- Add explicit configuration only for a demonstrated override. A missing bean may result from classpath, property, profile, or package-boundary conditions rather than requiring a new framework wrapper.
- Put application bootstrap under the intended base package. Moving the `@SpringBootApplication` class changes component and auto-configuration package discovery.

## Tests

Choose the narrowest test form that proves the behavior:

- plain unit test for framework-independent logic;
- slice tests such as `@WebMvcTest`, `@DataJpaTest`, or `@JsonTest` for one integration boundary;
- `@SpringBootTest` only when the full context or real application wiring is material;
- `ApplicationContextRunner` for focused auto-configuration conditions.

Do not assume a slice includes every production bean. Import only the configuration needed by the boundary under test.

## Packaging and execution

- Distinguish Maven/Gradle lifecycle output from Spring Boot repackaging. An executable Boot archive and a plain library archive are different artifacts.
- Verify the configured main class, layers, image builder, and plugin execution before changing packaging commands.
- Prefer the repository wrapper (`mvnw` or `gradlew`) and existing validation lifecycle.

## Review checklist

1. Confirm Boot version and dependency management source.
2. Identify configuration origin and active profile.
3. Explain the auto-configuration condition that owns the behavior.
4. Preserve package scanning and bean ownership boundaries.
5. Select a proportional test and run the repository's existing lifecycle.
