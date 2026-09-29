---
description: Read-only project audit of Veyrix pin, deployment and OMO additions.
---
Run the installed `veyrix --project <current-project-root> audit` and inspect the
reported drift or ownership error. It may fetch the exact pinned source into its
private cache; it must not change project files. Use `--offline` when cache-only
verification is requested. Report static file evidence, known upstream limitations
and remaining host-runtime uncertainty separately. Do not repair, update, delete,
install dependencies or execute imported Skills. The disk inventory does not
cover plugin-registered Skills/remote catalogs or prove OMO effective permissions.
Requested audit scope: $ARGUMENTS
