# Profiles and add-ons

Profiles are explicit, versioned inputs. No stack is inferred. All IDs below
are availability/routing contributions, not instructions to eagerly load them.
A profile name alone does not prove runtime or complete language expertise.

## Base profiles

| Profile | OMO role and selected IDs |
| --- | --- |
| `flutter` | fixer: `flutter-add-widget-test`, `flutter-build-responsive-layout`, `flutter-setup-declarative-routing` |
| `java-spring-maven` | fixer: `java-style`, `maven-build`, `spring-boot` |
| `java-spring` | fixer: `java-style`, `spring-boot` |
| `java` | fixer: `java-style` |
| `kotlin-android` | fixer: `android-clean-architecture`, `edge-to-edge`, `kotlin-patterns`; designer: `mobile-android-design` |
| `kotlin-kmp` | fixer: `compose-multiplatform-patterns`, `kotlin-patterns` |
| `kotlin` | fixer: `kotlin-patterns` |
| `node` | fixer: `nodejs-backend-patterns` |
| `python` | fixer: `python-code-style`, `python-type-safety` |
| `react-vite` | fixer: `vercel-composition-patterns`, `vercel-react-best-practices`, `vite` |
| `swift-ios` | designer: `mobile-ios-design` |

## Optional add-ons

| Add-on | OMO role and selected IDs |
| --- | --- |
| `api` | fixer: `api-contract` |
| `frontend-craft` | designer: `animate`, `design-taste-frontend`, `emil-design-eng`, `redesign-existing-projects`, `review-animations`, `web-design-guidelines` |
| `generated` | fixer: `generated-code` |
| `jpa` | fixer: `jpa-patterns` |
| `mariadb` | fixer: `mariadb-features`, `mariadb-query-optimization` |
| `maven` | fixer: `maven-build` |
| `mobile-web` | designer: `mobile-native` |
| `motion-discovery` | designer: `find-animation-opportunities` |
| `mybatis-dynamic-sql` | fixer: `mybatis`, `mybatis-dynamic-sql` |
| `mybatis-generator` | fixer: `generated-code`, `mybatis`, `mybatis-generator` |
| `mybatis` | fixer: `mybatis` |
| `nestjs` | fixer: `nestjs-best-practices` |
| `pnpm` | fixer: `pnpm` |
| `python-testing` | fixer: `python-testing-patterns` |
| `react-testing` | fixer: `react-testing` |
| `redis` | fixer: `redis-connections`, `redis-core` |
| `source-verification` | librarian: `source-driven-development` |
| `spring-security` | fixer: `spring-security` |
| `swift-testing` | fixer: `swift-testing-expert` |
| `vitest` | fixer: `vitest` |

Example conventional YAML:

```yaml
schema: 1
repository: https://github.com/unofficialmmon/veyrix.git
profile: python
addons: [python-testing]
accept_limitations: [python-testing-patterns]
```

Read the catalog limitations before accepting an ID. Changing this manifest
does not change the existing source SHA during sync. An unavailable framework
or incompatible add-on is not permission to install that application framework.
Use add-ons only where the project actually uses the relevant technology.
