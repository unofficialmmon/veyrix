# Veyrix

Explicit Skill profiles for **OpenCode + OMO Slim**. A small project configurator,
not an agent harness. No APM, daemon, stack guessing, global configuration rewrite
or user-maintained source checkout.

```text
reviewed Git commit -> private bare-object cache -> explicit profile + add-ons
                                              -> .agents/skills/<id>/
                                              -> OMO skills_add contributions
```

## Install the CLI once

Use a reviewed **full Veyrix commit SHA**, not an unrelated PyPI package with a
similar name. Python 3.11+ and Git are required. For example, with an existing uv:

```sh
uv tool install "git+https://github.com/unofficialmmon/veyrix.git@<FULL_VEYRIX_COMMIT>"
veyrix --version
```

Alternatively install that same pinned Git URL with `pipx install`. These native
installers manage the CLI environment; you do not maintain a working clone or run
`git pull`. Source catalog revisions are separately pinned in each project.
Private repositories use existing Git HTTPS credentials or SSH. Never put tokens
in `veyrix.yml`. Authenticated private-Git and macOS host smoke remain NOT RUN.

## First project

Work at the Git project root. Inspect the available catalog before selecting a
profile or add-on:

```sh
veyrix profiles
veyrix profile show java-spring-maven
veyrix addons
```

When the CLI was installed from the same reviewed Git repository/commit, `init`
can reuse that immutable installed commit. For a Maven Spring project using MyBatis:

```sh
veyrix init --profile java-spring-maven --addon mybatis --dry-run
veyrix init --profile java-spring-maven --addon mybatis
```

If installed-source provenance is unavailable or the selected repository differs,
Veyrix fails with `PIN_REQUIRED`; provide the reviewed full SHA explicitly:

```sh
veyrix init --profile java-spring-maven --addon mybatis \
  --ref <FULL_VEYRIX_COMMIT> --dry-run
```

For frontend implementation plus Taste/Emil craft:

```sh
veyrix init --profile react-vite --addon frontend-craft --dry-run
```

Remove `--dry-run` only after reviewing the intended changes. No unrelated Skill
is selected. `java-spring` deliberately does not assume Maven; use the explicit
`java-spring-maven` profile or `maven` add-on. Kotlin/Swift coverage is currently
partial: known-problem concurrency snapshots are deferred, not silently replaced.

## Day-to-day

```sh
veyrix profiles                    # list profiles at the current/installed pin
veyrix profile show <PROFILE_ID>   # inspect one profile
veyrix addons                      # list add-ons and limitations
veyrix doctor                      # cache-only static diagnostics; never repairs
veyrix sync --dry-run              # current manifest, existing commit
veyrix sync                        # materialize only planned owned changes
veyrix --offline sync              # same operation from a warm cache
veyrix audit                       # project read-only; may populate source cache
veyrix info                        # selected IDs and upstream limitations
veyrix update --ref <TAG_OR_SHA>   # preview only; does not change the project
veyrix update --ref <FULL_SHA> --apply
```

Apply requires a full SHA; named refs are supported only in previews. `sync`
never chooses a newer commit. Edit add-ons/profile in `veyrix.yml`, preview, then
sync at the same pin. Updating source and changing selection are distinct actions.

CLI results are JSON. Exit codes: `0` success/preview, `1` audit/doctor drift,
`2` blocked/error. `NOOP` means no project content changed, not that OpenCode
loaded or used a Skill. `STATIC_MATCH` and doctor `HEALTHY` are static
configuration/disk results, not runtime or security certification.

## Files and ownership

| File | Owner |
| --- | --- |
| `veyrix.yml` | User's explicit desired profile/add-ons/source |
| `veyrix.lock.json` | Veyrix's resolved commit, IDs, source hashes and limitations |
| `.agents/veyrix/managed.json` | Veyrix's deployed file hashes and only its OMO additions |
| `.agents/skills/<id>/` | Complete selected Skill copies managed per Veyrix receipt |
| `.opencode/oh-my-opencode-slim.jsonc` | Shared file; Veyrix changes only owned `skills_add` values |
| `.opencode/commands/veyrix-{setup,sync,audit}.md` | Three thin prompts calling the installed CLI |
| `AGENTS.md`, application files, global OpenCode/OMO, MCPs, plugins, memory | User / existing tools; never rewritten by sync |

Existing `.json` OMO files, APM deployments, duplicate same-ID Skills and unknown
files are **not automatically migrated or adopted**. An explicit ownership
migration must happen first. Repeated setup must not "fix" this by deleting copies.
The CLI does not run imported scripts, install application dependencies or execute
Skills to test their existence. See [ownership and recovery](docs/ARCHITECTURE.md).

## Catalog and quality

There are **47 available/conditional Skill directories**: the preserved 44-Skill
seed plus three Veyrix-authored common-quality Skills
(`engineering-quality`, `regression-proof`, `security-review`). The historical
95-entry migration inventory remains unchanged; the three later additions are
tracked separately with exact source identities.

There are **11 explicit profiles and 21 optional add-ons**. These are availability
and routing choices, not 47 always-loaded instructions. The
`engineering-quality` add-on exposes the three common-quality Skills to fixer and
oracle without creating another orchestration layer. No Vue/Nuxt or operational
suite is added.

External and previously adapted snapshots keep their original bytes. The original
three local-derived references and six official-document-derived references retain
those labels; the three new quality Skills are separately identified as Veyrix
local additions. Four conditional Skills require explicit `accept_limitations`
in the manifest. This acknowledges limitations, not a waiver for broken recipes
or evidence claims.

- [Profiles and add-ons](docs/PROFILES.md)
- [Essential UX](docs/UX.md)
- [Common quality layer](docs/QUALITY.md)
- [Global AGENTS baseline](docs/agents/GLOBAL_AGENTS.md)
- [Project AGENTS authoring prompt](docs/agents/PROJECT_AGENTS_AUTHORING_PROMPT.md)
- [Catalog quality, provenance and frontend selection](docs/CATALOG.md)
- [Migration decisions and existing-project migration](docs/MIGRATION.md)
- [External tools stay external](docs/EXTERNAL_TOOLS.md)
- [Tests and unverified host behavior](docs/VALIDATION.md)
- [Implementation decisions and recovery checkpoint](docs/IMPLEMENTATION.md)

## Development

```sh
python3 -m pip install -e .
python3 tools/check_catalog.py
python3 -m unittest discover -s tests -v
```

The CLI tests use disposable local Git remotes and projects. They do not modify
user projects or certify OpenCode/OMO runtime behavior or output quality.
