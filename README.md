# Veyrix

Veyrix is a small, deterministic project configuration and Skill distribution layer for OpenCode + Oh My OpenCode Slim.

The project is intentionally narrower than `agent-reference`:

- profiles are explicit instead of inferred implicitly;
- Veyrix-managed Skills are materialized under `.agents/skills/`;
- project OMO Skill additions are reconciled through `.opencode/oh-my-opencode-slim.jsonc`;
- source revisions are pinned and resolved from a repository cache rather than a developer working checkout;
- external operational tools remain external instead of becoming another orchestration layer.

The repository is currently being bootstrapped. Architecture, ownership rules, profiles, and the first deterministic sync contract will be added through pull requests.
