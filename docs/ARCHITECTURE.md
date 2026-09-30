# Architecture and ownership

## Boundaries

OpenCode owns discovery, permissions and execution. OMO owns routing semantics,
models, presets and delegation. Veyrix owns explicit catalog selection and a
bounded on-disk contribution, not effective host policy. Adding `skills_add`
grants availability only where the host permits it; it does not force loading.
A user-global denial, disabled agent, plugin registry or stale session can still
prevent use. Veyrix does not override those controls or claim it resolved them.

The source contract was checked against OMO configuration documentation at
`729311a376bf2ccf7b233055d2b02a0462b0c596` (`docs/configuration.md`, Skills Assignment).
Host versions/configuration must be checked on the target machine. Do not assume
all future OpenCode/OMO versions share the same discovery or merge behavior.

## Repo cache

The CLI is installed independently. It reads `veyrix.yml` and a full locked SHA,
then uses Git objects under `$XDG_CACHE_HOME/veyrix/repositories/<url-hash>.git`
(or `~/.cache/veyrix/...`). There is no working tree, branch checkout or pull.
Named refs may be resolved for a preview; applying requires the preview's full
commit. Warm exact pins work offline. Missing/unfetchable pins block; no fallback
to main. Refs under `refs/veyrix/pins/` retain fetched objects. Git/SSH handles
credentials; output does not echo raw Git authentication diagnostics.

Cache must be outside the project and declared disk Skill roots. URL schemes
are restricted to credential-free HTTPS or SSH; local file:// access requires
explicit development/test permission. No remote helper protocols, submodules,
LFS pointers, symlink source files, cached scripts or post-install hooks execute.
A SHA/content hash establishes identity, not publisher trust or safe prose.

## Manifest and lock

The generated `veyrix.yml` uses JSON syntax (valid YAML) to avoid ambiguous
scalars. Conventional YAML edits are accepted with duplicate keys rejected.
The schema has exactly: `schema`, `repository`, `profile`, `addons`,
`accept_limitations`. Profiles/add-ons are explicit data, not executable scripts.
The lock records the source SHA, resolved inputs, complete selected file hashes,
profile definition hashes and retained limitations. No absolute cache path is
stored in portable desired/lock state.

`sync` may change selection at the same source pin when the user edits the
manifest. `update --ref <full-SHA> --apply` is the only source upgrade path. Source
repository migration is deliberately not an automatic v0.1 operation.

## Shared OMO JSONC

New projects get exactly `.opencode/oh-my-opencode-slim.jsonc`. Existing `.json`
blocks setup, including when both forms exist: creating a new higher-precedence
file must not silently disable the user's existing configuration.

The parser rejects duplicate keys/malformed JSONC. It records source spans and
changes only `agents.<role>.skills_add` values or missing ancestor objects. Bytes
outside the changed value are preserved, including unrelated comments, model,
MCP and permission configuration. Comments *inside a replaced owned array* may
be normalized; do not claim full-file byte preservation on an actual change.

Receipt ownership is per contributed ID, not per entire shared array. Existing
manual additions are not claimed. Subsequent manual extra entries survive.
Deleting an owned entry or explicitly excluding a wanted ID blocks reconciliation.
One profile implies one deterministic managed selection; entire config files need
not be identical when projects have different user-owned settings.

## Disk ownership and recovery

One intended owner per Skill ID in this project's discovery context. Both
identical and divergent external collisions block a new deployment. Existing
untracked files are not permission to overwrite/adopt them. The CLI checks native
project/user roots plus explicitly supplied extra disk roots. It does not inspect
plugin definitions or remote catalogs. A malformed non-Skill file is not treated
as a valid registration. Symlink subtrees requiring traversal block rather than
being guessed. Supported v0.1 targets are explicit Git roots (including worktree
.git files); no automatic nested-monorepo or sibling workspace traversal.

Complete relative inventories/hashes are verified before deployment. Project-local
ownership state is stored at `.agents/veyrix/managed.json`; the transient apply
mutex is `.agents/veyrix/write.lock`. Veyrix does not create a separate `.veyrix/`
project directory. A changed owned file blocks; a missing owned file can be
restored. Removal is limited to unchanged paths recorded by Veyrix. Unknown extra files in an owned Skill directory
block. Shared parent directories are never recursively deleted. Application,
AGENTS, global config and Git index/history are not written.

Apply takes an exclusive project operation lock, rechecks planned bytes and
writes via same-directory temporary files and replace. Private recovery copies
use opaque non-Skill names under the cache. Receipt is written last. Caught errors
attempt rollback only where bytes still equal this operation's write; intervening
user changes are preserved and reported. This is not a multi-file filesystem
transaction: power loss/kill can leave partial files. Inspect recovery.json and
restore only reviewed operation-owned changes. No blind reset/clean/rm fallback.
Abandoned locks require human review; the CLI never guesses that a writer is dead.

No filesystem checks can eliminate hostile concurrent TOCTOU races. Do not run
untrusted parallel writers while applying. Backups may contain project config;
keep them private. There is no automatic backup garbage collection in v0.1.
