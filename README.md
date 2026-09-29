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

Work at the Git project root. Review the profile and any upstream limitations.
For a Maven Spring project using MyBatis:

```sh
veyrix init --profile java-spring-maven --addon mybatis \
  --ref <FULL_VEYRIX_COMMIT> --dry-run
veyrix init --profile java-spring-maven --addon mybatis \
  --ref <FULL_VEYRIX_COMMIT>
```

For frontend implementation plus Taste/Emil craft:

```sh
veyrix init --profile react-vite --addon frontend-craft \
  --ref <FULL_VEYRIX_COMMIT> --dry-run
```

Remove `--dry-run` only after reviewing the intended changes. No unrelated Skill
is selected. `java-spring` deliberately does not assume Maven; use the explicit
`java-spring-maven` profile or `maven` add-on. Kotlin/Swift coverage is currently
partial: known-problem concurrency snapshots are deferred, not silently replaced.

## Day-to-day

```sh
veyrix sync --dry-run              # current manifest, existing commit
veyrix sync                       # materialize only planned owned changes
veyrix --offline sync             # same operation from a warm cache
veyrix audit                      # project read-only; may populate source cache
veyrix info                       # selected IDs and upstream limitations
veyrix update --ref <TAG_OR_SHA>   # preview only; does not change the project
veyrix update --ref <FULL_SHA> --apply
```

Apply requires a full SHA; named refs are supported only in previews. `sync`
never chooses a newer commit. Edit add-ons/profile in `veyrix.yml`, preview, then
sync at the same pin. Updating source and changing selection are distinct actions.

The five CLI commands return JSON. Exit codes: `0` success/preview, `1` audit drift,
`2` blocked/error. `NOOP` means no project content changed, not that OpenCode loaded
or used a Skill. `STATIC_MATCH` is not a security audit or runtime certification.

## Files and ownership

| File | Owner |
| --- | --- |
| `veyrix.yml` | User's explicit desired profile/add-ons/source |
| `veyrix.lock.json` | Veyrix's resolved commit, IDs, source hashes and limitations |
| `.veyrix/managed.json` | Veyrix's deployed file hashes and only its OMO additions |
| `.agents/skills/<id>/` | Complete byte-preserved copies selected by Veyrix |
| `.opencode/oh-my-opencode-slim.jsonc` | Shared file; Veyrix changes only owned `skills_add` values |
| `.opencode/commands/veyrix-{setup,sync,audit}.md` | Three thin prompts calling the installed CLI |
| `AGENTS.md`, application files, global OpenCode/OMO, MCPs, plugins, memory | User / existing tools; never rewritten by sync |

Existing `.json` OMO files, APM deployments, duplicate same-ID Skills and unknown
files are **not automatically migrated or adopted**. An explicit ownership
migration must happen first. Repeated setup must not "fix" this by deleting copies.
The CLI does not run imported scripts, install application dependencies or execute
Skills to test their existence. See [ownership and recovery](docs/ARCHITECTURE.md).

## Catalog and quality

44 available/conditional Skill directories (43 selected from agent-reference
0.6.0 plus Emil `emil-design-eng`). The full 95-entry migration inventory has
KEEP/EXCLUDE/DEFER reasons. There are 11 explicit profiles and 20 optional add-ons;
these are not 44 always-loaded instructions. No Vue/Nuxt or operational suites.

External and previously adapted snapshots keep their original bytes. Three
existing local-derived references and six official-document-derived references
retain those labels; they are **not** advertised as official external Skills.
Four conditional Skills require explicit `accept_limitations` in the manifest.
This acknowledges limitations, not a waiver for broken recipes or evidence claims.

- [Profiles and add-ons](docs/PROFILES.md)
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
