# Essential UX

This release intentionally limits UX changes to four items.

## 1. Installed-source pin for init

`veyrix init` may omit `--ref` only when the running non-editable Git installation
has matching PEP 610 `direct_url.json` metadata with a full immutable `commit_id`.
`requested_revision`, main, HEAD and latest are never substituted. Missing,
editable, ambiguous, shadowed or repository-mismatched provenance requires an
explicit full `--ref`. An explicit `--ref` always wins.

This is local provenance consistency, not signature or supply-chain verification.

## 2. Profile and add-on discovery

```sh
veyrix profiles
veyrix profile show java-spring-maven
veyrix addons
```

Before project adoption these use the matching installed source pin. In an
initialized project they use the existing project lock pin. Explicit repository/ref
overrides inspect another immutable snapshot without repinning or modifying the
project. These commands do not infer stack compatibility or select anything.

## 3. Doctor

`veyrix doctor` is a cache-only static diagnostic. It reuses audit protections,
never fetches source, repairs files, rewrites OMO, or claims host activation.
`HEALTHY` means static managed disk/configuration consistency only; drift returns
exit 1 and blocked/inconsistent state returns exit 2.

## 4. Actionable errors

Existing error codes and exit semantics are preserved. Blocked results add a
`next_action` that points to the safe recovery path without force-overwrite,
automatic deletion, permission bypass or hidden source upgrades.

No interactive wizard, stack auto-selection, dashboard, human-output mode, profile
recommendation engine or additional OpenCode command is added.
