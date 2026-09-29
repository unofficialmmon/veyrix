---
name: security-review
description: Review changed trust boundaries involving authentication, authorization, untrusted input, sensitive data, queries, subprocesses, files, uploads, external APIs, webhooks, dependencies or security configuration. Use for a scoped security review or security-sensitive implementation assessment; not for automated hardening, scanner installation or a blanket security certification.
---

# Security Review

Treat a review request as read-only. Establish the changed surface, assets,
attacker-controlled inputs and applicable repository security policy. Read the
relevant sections of [Review checks](references/review-checks.md), not every check
for every task. Assess actual reachability and impact, not keyword presence alone.

Trace input -> trust boundary -> validation/authorization -> sensitive operation
and output. Verify controls in their real execution path. Distinguish observed
vulnerabilities, plausible concerns requiring evidence, and controls actually
checked without an issue. Missing deployment context is uncertainty, not proof
that no protection exists or that protection is active.

For each finding report severity, exact location, triggering conditions, violated
boundary, plausible impact, supporting evidence and a minimal mitigation direction.
Do not include real secrets or personal data in findings, logs, test fixtures or
responses. Redact values; identify the relevant key/location only.

Report verification separately (`STATIC`, `ACTUAL_PASS`, `ACTUAL_FAIL`, `NOT_RUN`,
`BLOCKED`), with scope and limitations. A static review or clean scanner run does
not establish complete security, vulnerability absence or regulatory compliance.
Use current primary documentation/advisories for material version-specific claims;
when unavailable, label that part unverified instead of inventing advisory details.

Do not install scanners, update dependencies, rotate secrets, change policies,
probe live targets, or run hardening/deployment commands automatically. Existing
approved tools can supply evidence within their authorization and data boundaries;
inspect their configuration and coverage before trusting an empty result. Never
bypass denied tools or weaken a control to satisfy a test. Fixer may apply these
criteria during separately authorized implementation; Oracle may use them for
review. Do not create agents, force delegation or grant additional permissions.
