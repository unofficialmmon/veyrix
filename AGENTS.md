# Veyrix maintenance

Veyrix is a CLI configurator and curated source catalog, not a second harness.
Preserve explicit profiles, bare-cache/exact-pin source reads, on-disk ownership
and normal `sync` idempotency. Do not add automatic stack inference or upgrades.

Never modify a preserved Skill body/resource to make a test pass. Review and
replace a complete upstream snapshot with its provenance when explicitly requested.
Keep local-derived and adapted labels honest. Catalog presence is not activation.

Project writes are limited to the manifest/lock/receipt, selected complete Skill
copies, three CLI wrapper commands and owned OMO skills_add contributions. Preserve
comments and all unrelated JSONC values. Block ambiguous .json/.jsonc ownership,
unowned files, modified managed files and duplicate Skill owners before writes.
Global settings, memory, providers, MCPs, user AGENTS and application code are not
Veyrix-owned. Do not add a generic `--force` that bypasses these checks.

Test actual CLI outcomes with disposable local Git remotes. Include negative
cases and before/after content checks; phrase-presence tests are not behavior
proof. Run `python3 tools/check_catalog.py` and `python3 -m unittest discover -s
tests -v`. Keep source/packaging checks separate from host and model evidence.
Record design decisions and limitations in docs instead of accumulating commands.
