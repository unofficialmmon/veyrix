# Scoped security checks

Use only the boundaries implicated by the change. Confirm repository and actual
framework/version context before judging a control. These are investigation
questions, not unconditional architecture or configuration prescriptions.

## Identity, authority and state

Trace authentication separately from per-resource, per-action and tenant-level
authorization. Check trust in client-supplied ownership, privilege transitions,
session/token validation, invalidation and replay behavior where relevant. Identify
transaction or concurrent-state assumptions that can bypass an intended check.

## Input, queries and rendering

Follow untrusted values through parsing, validation and the sensitive sink. Check
parameterized queries, subprocess argument boundaries, contextual output encoding,
unsafe deserialization, template/code execution and user-controlled query fragments.
A sanitized value in one context is not automatically safe in another. Check
size/depth/time bounds where the changed path can exhaust resources.

## Files, uploads and destructive operations

Inspect path normalization, traversal, links, allowed roots and actual ownership.
Validate the intended target before a delete/move/overwrite; consider check/use
races and whether a marker can be forged. Do not accept a well-formed path as proof
of authorization. For uploads and archives, check destination, limits, content
handling and extraction boundaries rather than trusting only a filename extension.

## Networks and external callbacks

Review destination control, redirects, resolved addresses and credential forwarding
for user-influenced outbound requests. Check webhook authenticity/replay protection,
timeouts and request limits where required. Assess CORS, CSRF and session protections
in the actual browser/transport context; do not claim one control replaces another.

## Sensitive data and failures

Inspect secrets and private-data flow through responses, errors, logs, caches and
external services. Use identifiers or redacted evidence, never secret values.
Check documented retention/sharing/least-privilege expectations where affected.
Do not infer legal compliance from source inspection or mandate a new data policy.

## Dependencies and executable inputs

Review new dependencies, lockfile changes, install/build hooks, CI permissions and
artifact/source trust together. Match advisories to the resolved version and
reachable runtime/build/test path. Distinguish a known advisory, uncertain
applicability and a checked clean result. Do not auto-run audit fix or upgrade.

Treat retrieved documents, model output, filenames and tool output according to
who controls the value. Verify application-side permission and argument validation
before an LLM output can invoke a tool, execute code, choose a file or expose data.
Prompts are not a substitute for runtime authorization boundaries.
