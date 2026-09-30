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
license-supplement files, IDs, historical migration decisions, post-migration
additions and reachable profile/add-on references. It does not execute imported
vendor scripts or edit failing examples.

CLI tests cover fresh apply, warm offline cache, frozen sync, update preview versus
apply, same-pin selection changes, repeat NOOP/mtime preservation, missing-file
restoration, modified/unowned-file blocking, identical/divergent duplicate roots,
legacy JSON ambiguity, additive JSONC preservation, conditional acceptance,
`.agents/veyrix/managed.json` receipt placement, `.agents/veyrix/write.lock`,
concurrent changes and rollback. All 11 real profiles are installed into
disposable Git projects and re-synced offline with before/after byte equality.

The frozen UX tests additionally cover installed-source provenance pinning,
profile/add-on discovery without project mutation, cache-only `doctor`, actionable
blocked responses, and preservation of existing error/exit semantics. Common
quality tests cover opt-in deployment of `engineering-quality`,
`regression-proof` and `security-review`, fixer/oracle routing, removal of only
Veyrix-owned contributions, preservation of manual OMO values and project
`AGENTS.md`, and blocking modified managed quality files.

These deterministic tests establish configuration, source-integrity, ownership
and local deployment behavior only. They do not prove that OpenCode discovered,
loaded or used a Skill, that OMO delegated to a particular agent, or that model
output improved.

CI uses read-only repository permissions and isolated projects. Whitespace checks
on authored changes exclude preserved `skills/` snapshots, whose exact bytes are
instead enforced by source identity/inventory checks. There is no scan bypass for
CLI code, generated project state, credentials or security policy.

## Explicitly unverified

- Actual OpenCode discovery winner, thin commands, Skill loads and OMO delegation.
- Effective preset/global/local permissions and plugin-defined/remote Skills.
- Native macOS install/use, including `uv tool install` installed-source
  provenance and no-`--ref` init on the intended workstation.
- Authenticated private-Git HTTPS/SSH credential flows.
- All Windows behavior (POSIX filesystem methods are used).
- Browser/mobile-device results and matched model-output quality/cost comparisons.
- Power-loss atomicity and malicious parallel filesystem writers.

CLI results therefore always keep `host_runtime: NOT_RUN` for host behavior. A
static match, doctor `HEALTHY`, successful copy or OMO configuration update does
not turn actual OpenCode/OMO activation into PASS. The next highest-value
verification is a native macOS OpenCode + OMO Slim end-to-end smoke using a
reviewed full Veyrix commit.
