# External capabilities

Veyrix does not install or configure agent-browser, Impeccable, HyperFrames,
Headroom, Graphify or Playwright Skills/MCPs. None is a bundled plugin or required
runtime. OpenCode/OMO/user tooling retains ownership.

| Candidate | Separate adoption decision |
| --- | --- |
| agent-browser | Review CLI, browser runtime and Skill scope independently. |
| Impeccable | Preserve chosen global/project command+Skill owner; avoid overlap with Taste/Emil in one task. |
| HyperFrames | Project-specific video capability; review any lazy installation. |
| Headroom | Provider/proxy traffic and memory implications require separate testing. |
| Graphify | Index/graph capability; compare with existing codegraph/OMO tools. |
| Playwright Skill/MCP | Skill and MCP are separate installations; choose responsibility and permissions. |

This is a boundary/adoption checklist, not fresh compatibility or installation
certification. Check current official sources and the actual installed versions
before each external adoption. Never change models/providers/MCPs as a side effect
of `veyrix sync`. Register extra disk Skill roots with the CLI when inventorying
possible same-ID collisions. Actual plugin registrations require host diagnostics.
