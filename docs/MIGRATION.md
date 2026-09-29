# Migration from agent-reference

Source commit: `2053b47cd291db5d00d7c9df9932764aca7b3859`. Machine-readable decisions live in
`catalog/migration.json`; this table is a readable projection, not a second policy.

## Existing consumers

Veyrix init intentionally does not adopt APM-managed files, even when identical.
Keep agent-reference and its consumers unchanged until a separate migration is
approved. In a disposable clone, inventory APM selection/lock/commands, manual
changes and user/global same-ID copies first. Retire the old owner using its
supported process only after backup/review; do not delete the whole .agents tree.
Resolve .json/.jsonc OMO ownership explicitly and preserve user models/MCPs.
Then preview Veyrix init at a reviewed SHA and verify only the selected targets.
Do not remove Spec Kit, global commands, external tools or user AGENTS as cleanup.

## All 95 decisions

| Skill | Decision | Reason |
| --- | --- | --- |
| `android-clean-architecture` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `android-cli` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `animate` | KEEP | KEEP frontend-craft add-on: motion implementation; no implicit component-library installation. |
| `api-contract` | KEEP | KEEP optional API-contract reference, explicitly local-derived rather than an official external Skill. |
| `browser-tools` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `bug-reproduction-brief` | EXCLUDE | EXCLUDE: no separate lifecycle/reproduction control plane in Veyrix. |
| `compose-multiplatform-patterns` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `deprecation-and-migration` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `design-taste-frontend` | KEEP | KEEP frontend-craft add-on: marketing/landing art direction, not a universal dashboard workflow. |
| `durable-objects` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `eas-workflows` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `edge-to-edge` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `expo-api-routes` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `expo-data-fetching` | EXCLUDE | EXCLUDE: Expo/React Native is outside the initial web/native language profiles. |
| `expo-deployment` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `expo-dev-client` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `expo-dom` | EXCLUDE | EXCLUDE: Expo/React Native is outside the initial web/native language profiles. |
| `expo-module` | EXCLUDE | EXCLUDE: Expo/React Native is outside the initial web/native language profiles. |
| `expo-native-ui` | EXCLUDE | EXCLUDE: Expo/React Native is outside the initial web/native language profiles. |
| `expo-tailwind-setup` | EXCLUDE | EXCLUDE: Expo/React Native is outside the initial web/native language profiles. |
| `expo-upgrade` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `find-animation-opportunities` | KEEP | KEEP optional motion-discovery add-on, not ambient animation on every UI. |
| `flutter-add-widget-test` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `flutter-apply-architecture-best-practices` | DEFER | DEFER: unkeyed user cache example can return a different requested user; architecture choice is also opinionated. |
| `flutter-build-responsive-layout` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `flutter-fix-layout-issues` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `flutter-setup-declarative-routing` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `frontend-design` | EXCLUDE | EXCLUDE: selected Taste art direction and Emil component craft instead; not a claim of inferior output. |
| `generated-code` | KEEP | KEEP optional generated-source ownership reference; preserve original local provenance. |
| `java-coding-standards` | EXCLUDE | EXCLUDE v0.1: broad overlap and version-sensitive examples; java-style is only a local style guide, not a complete replacement for Java expertise. |
| `java-style` | KEEP | KEEP: bounded handwritten-Java style and generator boundaries; original user-specific preferences remain subordinate to the project. |
| `jpa-patterns` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `kotlin-coroutines-flows` | DEFER | DEFER: preserved dispatcher platform guidance requires upstream correctness review; do not mask it with another Skill. |
| `kotlin-patterns` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `mariadb-features` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `mariadb-query-optimization` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `maven-build` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `mcp-builder` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `mobile-android-design` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `mobile-ios-design` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `mobile-native` | KEEP | KEEP optional mobile-web add-on: touch/viewport polish, not native mobile implementation. |
| `mybatis` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `mybatis-dynamic-sql` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `mybatis-generator` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `navigation-3` | EXCLUDE | EXCLUDE v0.1: specialized Navigation 3 adoption is not required by the initial Android profile. |
| `nestjs-best-practices` | KEEP | KEEP conditional NestJS add-on: retained original limitations require explicit acceptance. |
| `next-cache-components-adoption` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `next-cache-components-optimizer` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `nodejs-backend-patterns` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `nuxt` | EXCLUDE | EXCLUDE: Vue/Nuxt/Pinia/VueUse are explicitly outside the requested Veyrix scope. |
| `performance-optimization` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `pinia` | EXCLUDE | EXCLUDE: Vue/Nuxt/Pinia/VueUse are explicitly outside the requested Veyrix scope. |
| `pnpm` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `python-code-style` | KEEP | KEEP Python profile: concrete style/tooling reference with original preferences, no automatic whole-project formatting. |
| `python-testing-patterns` | KEEP | KEEP conditional testing add-on: failing email example and strict async fixture limitations are retained; explicit acceptance required. |
| `python-type-safety` | KEEP | KEEP Python profile: types/generics/protocols; retained non-null Result example limitation. |
| `r8-analyzer` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `react-testing` | KEEP | KEEP conditional testing add-on: JSDOM contrast and unavailable ECC companions remain documented; explicit acceptance required. |
| `receiving-code-review` | EXCLUDE | EXCLUDE v0.1: focus the initial catalog on language/framework craft; keep review workflow outside profile defaults. |
| `redesign-existing-projects` | KEEP | KEEP frontend-craft add-on: explicitly requested existing-UI redesign, preserve the current stack. |
| `redis-connections` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `redis-core` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `refactor-plan` | EXCLUDE | EXCLUDE: planning/delegation remains OMO-owned. |
| `review-animations` | KEEP | KEEP frontend-craft add-on: motion review, not automatic fixes. |
| `security-and-hardening` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `source-driven-development` | KEEP | KEEP optional source-verification add-on: version-sensitive official API evidence, not a mandatory step on every task. |
| `spring-boot` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `spring-security` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `springboot-patterns` | EXCLUDE | EXCLUDE v0.1: keep the narrower Boot/configuration and explicit persistence add-ons; broader application patterns can be reviewed later. |
| `springboot-tdd` | EXCLUDE | EXCLUDE: mandatory TDD/coverage methodology is not an ambient stack default. |
| `sql-optimization-patterns` | EXCLUDE | EXCLUDE: a preserved aggregate optimization changes query semantics; prefer selected engine-specific references. |
| `supabase-postgres-best-practices` | EXCLUDE | EXCLUDE v0.1: PostgreSQL/Supabase is not part of the initial selected DB add-ons; file count alone is not a quality verdict. |
| `swift-concurrency` | DEFER | DEFER: preserved task-group cancellation guidance requires upstream correctness review. |
| `swift-testing-expert` | KEEP | KEEP conditional testing add-on: retain the documented invalid seconds-based time limit example; explicit acceptance required. |
| `swiftui-expert-skill` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `terraform-style-guide` | EXCLUDE | EXCLUDE v0.1: outside the selected language/framework scope; not a judgment that the upstream is low quality. |
| `terraform-test` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `testing-setup` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `translation-review` | EXCLUDE | EXCLUDE v0.1: outside the selected language/framework scope; not a judgment that the upstream is low quality. |
| `vercel-composition-patterns` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `vercel-react-best-practices` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `vercel-react-native-skills` | EXCLUDE | EXCLUDE: React Native is separate from React web and outside this initial language/application scope. |
| `vercel-react-view-transitions` | EXCLUDE | EXCLUDE v0.1: specialized transition surface; motion craft is separately selected. |
| `verification-before-completion` | EXCLUDE | EXCLUDE: avoid an additional completion workflow; CLI evidence and OMO remain distinct owners. |
| `vite` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `vitest` | KEEP | KEEP as a matching explicit language/framework profile or add-on; install only selected IDs and preserve project conventions. |
| `vue` | EXCLUDE | EXCLUDE: Vue/Nuxt/Pinia/VueUse are explicitly outside the requested Veyrix scope. |
| `vue-best-practices` | EXCLUDE | EXCLUDE: Vue/Nuxt/Pinia/VueUse are explicitly outside the requested Veyrix scope. |
| `vue-router-best-practices` | EXCLUDE | EXCLUDE: Vue/Nuxt/Pinia/VueUse are explicitly outside the requested Veyrix scope. |
| `vue-testing-best-practices` | EXCLUDE | EXCLUDE: Vue/Nuxt/Pinia/VueUse are explicitly outside the requested Veyrix scope. |
| `vueuse-functions` | EXCLUDE | EXCLUDE: Vue/Nuxt/Pinia/VueUse are explicitly outside the requested Veyrix scope. |
| `web-design-guidelines` | KEEP | KEEP frontend-craft add-on: separate web-quality review from art direction. |
| `web-perf` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `webapp-testing` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |
| `wrangler` | EXCLUDE | EXCLUDE: external operational tools, deployments and migrations remain outside Veyrix core. |

Additional directly reviewed inclusion: `emil-design-eng`; source/license/hash
are in catalog/skills.json. The 44th entry is not an unlisted migration decision.
