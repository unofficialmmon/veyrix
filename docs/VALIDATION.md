# Validation

## Repeatable local checks

```sh
python3 tools/check_catalog.py
python3 -m unittest discover -s tests -v
python3 -m pip wheel --no-deps . -w dist
```

Wheel builds use the declared isolated build backend. A pre-provisioned offline
maintainer environment may use `--no-build-isolation` only after installing the
`[build-system]` requirements itself; editable installation does not guarantee
that the runtime environment contains setuptools.

The source tree includes real CLI/local-Git tests, not just expected-output
strings. The catalog verifier checks hashes, complete inventories, original versus
license-supplement files, IDs, migration reasons and reachable profile/add-on
references. It does not execute imported vendor scripts or edit failing examples.

CLI tests cover fresh apply, warm offline cache, frozen sync, update preview versus
apply, same-pin selection changes, repeat NOOP/mtime preservation, missing-file
restoration, modified/unowned-file blocking, identical/divergent duplicate roots,
legacy JSON ambiguity, additive JSONC preservation, conditional acceptance,
locks, concurrent changes and rollback. All 11 real profiles are installed into
disposable Git projects and re-synced offline with before/after byte equality.
Catalog mutations exercise actual failures for changed source bytes, unknown IDs
and missing migration reasons. CLI application tests do not imply every source
example is correct; see CATALOG.md for preserved limitations.

CI uses read-only repository permissions and isolated projects. Whitespace checks
on authored changes exclude preserved `skills/` snapshots, whose exact bytes are
instead enforced by the source hash/inventory checks. There is no scan bypass for
CLI code, generated project state, credentials or security policy.

## Explicitly unverified

- Actual OpenCode discovery winner, commands, Skill loads and OMO delegation.
- Effective preset/global/local permissions and plugin-defined/remote Skills.
- Authenticated private-Git HTTPS/SSH credential flows.
- Native macOS usage and all Windows behavior (POSIX filesystem methods used).
- Browser/mobile-device results and matched model-output quality/cost comparisons.
- Power-loss atomicity and malicious parallel filesystem writers.

CLI results therefore always include `host_runtime: NOT_RUN`. A static match or
successful copy does not turn any item above into PASS. No internal inference
runner or credentials are needed for the deterministic CLI/catalog test suite.
