# Project AGENTS Authoring Prompt

Use this template when creating a root `AGENTS.md` for a new project or updating it
because a durable project rule has changed. Do not copy this template verbatim into
`AGENTS.md`. The resulting file is project-owned and is not a Veyrix-managed artifact.

Write the resulting project `AGENTS.md` in concise English. Preserve the meaning of
existing project-owned rules when updating them; do not translate or rewrite unrelated
project files.

## Execution prompt

Inspect the current repository and create or minimally update the root `AGENTS.md`.
Record only durable project facts, contracts, and commands. Do not duplicate generic
technology tutorials, Veyrix Skill bodies, OMO orchestration rules, or transient task
state.

### 1. Boundary and existing state

- Prefer the project boundary explicitly given by the user. Otherwise, determine the
  current worktree/repository root.
- Read the user-owned global OpenCode instructions separately before authoring project
  guidance. Use `$OPENCODE_CONFIG_DIR/AGENTS.md` when `OPENCODE_CONFIG_DIR` is set;
  otherwise use `$XDG_CONFIG_HOME/opencode/AGENTS.md`, normally
  `~/.config/opencode/AGENTS.md`, when that file exists.
- Treat global AGENTS as read-only cross-project guidance. Do not copy its generic
  rules into the project `AGENTS.md`; add only project-specific durable facts,
  contracts, commands, ownership, and exceptions.
- For project-scoped AGENTS discovery, inspect the root and relevant nested
  `AGENTS.md` files within the determined project boundary. Do not keep walking
  above the project/repository root toward the filesystem root unless the user
  explicitly identifies an external instruction source.
- Check README/CONTRIBUTING, maintained design documents, and current working-tree
  changes that are relevant to the authoring task.
- If root `AGENTS.md` already exists, preserve user-owned rules, managed sections,
  and established project meaning. Write the maintained document in English unless
  the user explicitly requires another language.
- Do not overwrite symlinks or files owned by another tool.
- The only persistent file this authoring task may change is the target root
  `AGENTS.md`. If preview was requested, do not write it.

### 2. Evidence-first investigation

Understand repository structure first, then inspect only the evidence needed.

- Build, package, workspace, and runtime version configuration; wrappers; scripts;
  formatter/linter configuration; CI.
- Representative source, tests, and ADRs that establish major module responsibility
  and proven dependency direction.
- Test types, locations, actual execution paths, and required local service or
  environment names.
- API, database, message, and serialization contracts; migrations; generator
  configuration; generated-code ownership.
- Existing Veyrix or OMO material only when it actually exists and is relevant to this
  document.

Distinguish command existence from successful execution. Do not turn one
implementation example into policy. Do not invent architecture, versions, coverage,
runtime activation, or supported scope that cannot be established from evidence.

### 3. Responsibility boundaries

- Do not redefine OpenCode host/permission behavior or OMO Slim agent, delegation, or
  model policy.
- If Veyrix is present, treat `veyrix.yml` as user-selected desired state and the
  lock/managed receipt as resolution and ownership evidence.
- Do not assume all of `.agents/skills/` is Veyrix-owned; distinguish only verified
  managed IDs.
- Do not copy Skill selections or routing lists into AGENTS. Distinguish selected,
  materialized, allowed, loaded, and actually used states.
- If Veyrix is absent, continue authoring the document. Installing Veyrix, changing a
  profile, or widening permissions is outside this task.

### 4. Authoring criteria

Use only sections that have repository evidence and future decision value. Omit empty
sections.

- Project: minimum context needed to understand the purpose and structure.
- Authority: sources of truth for rules/contracts and when they must be consulted.
- Architecture: module responsibilities and proven dependency/process boundaries.
- Ownership: generated/vendor/external areas and supported modification paths.
- Contracts: authoritative sources for API/DB/message/schema behavior.
- Development / Verification: actual commands, execution location, prerequisites, and
  what each check proves.
- Project-specific constraints: repository-proven traps, exceptions, or non-obvious
  rules.

Prefer repository-relative paths. Aim for roughly 50–120 lines when that is enough,
but do not delete important existing contracts merely to hit a line target. For long
details, point to the maintained source and state when it should be read.

Do not add generic framework best practices, common review/security/regression
checklists, automatic installation, new MCPs/agents/commands, guessed
commands/architecture/test PASS claims, current branch progress, TODO placeholders,
Veyrix ownership headers, or instructions to regenerate AGENTS on every task.

### 5. Safe application

If the existing document is already correct, return `NOOP`. Updating or deleting
stale content requires evidence. Re-read the target immediately before writing; if a
concurrent user change occurred, recompute against the current contents.

After writing, verify only the authorized target and do not re-audit unrelated dirty
or untracked files that were already present.

- If `AGENTS.md` was newly created, read it once and run
  `git status --short -- AGENTS.md`. An untracked `?? AGENTS.md` is sufficient
  target-state evidence. Do not use or retry `git diff --no-index` variants merely
  to manufacture a diff for the new file.
- If an existing tracked `AGENTS.md` was modified, inspect
  `git diff -- AGENTS.md` once.
- Run each final verification check at most once unless the target changes again or
  the first check returns an actual error that requires a different check.
- Existing unrelated working-tree changes are baseline state: preserve them, but do
  not repeatedly re-scan them to prove they remained untouched.

Do not commit, push, open a PR, or merge unless separately requested.

### 6. Result report

- Result: `CREATED`, `UPDATED`, `NOOP`, `PREVIEW`, or `BLOCKED`.
- Key changes: rules added, changed, preserved, or intentionally omitted.
- Evidence: material facts/rules and the files, configuration, symbols, or sections
  actually inspected.
- Verification: distinguish `ACTUAL_PASS`, `ACTUAL_FAIL`, `STATIC`,
  `NOT_RUN`, and `BLOCKED`.
- Unresolved items: conflicts, inaccessible evidence, investigation limits, and
  unverified runtime or commands.

This static authoring procedure does not prove actual OpenCode loading, OMO
delegation, or model quality.
