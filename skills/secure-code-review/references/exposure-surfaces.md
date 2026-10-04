# Secret Exposure Surfaces and Coverage

## Coverage states

Use one state per material surface:

- `complete` — every requested and supported item in that surface was inspected with no material skip.
- `partial` — some requested/material items were skipped or unsupported.
- `not-run` — capability existed in principle but the surface was not inspected in this review.
- `unavailable` — the required artifact/tool/access was not available.
- `not-applicable` — evidence shows the surface does not apply.

Never aggregate a complete working-tree scan into a complete repository/system claim.

## Surface catalog

| Surface | What counts as evidence | Important limitation |
|---|---|---|
| working tree | supplied/readable text files | excludes Git history and unsupported/binary files |
| Git history | commits/patch additions across requested refs | requires Git and available repository objects |
| generated/build artifacts | generated configs, dist/build/bin/obj/target text, packages when inspectable | binary packages/images may need dedicated extraction |
| container/image | Dockerfile plus built image/layers when supplied | Dockerfile review alone is not image-content proof |
| CI/CD configuration | workflow/pipeline definitions, actions/tasks, permissions, secret mappings | config cannot prove remote log/runtime state |
| CI/CD logs/artifacts | supplied logs and build artifacts | unavailable remote logs stay unavailable |
| IaC/state/plan | Terraform/IaC source plus state/plan when supplied | `sensitive` display redaction is not persistence proof |
| docs/examples/issues | supplied docs/examples/tickets/comments | external collaboration surfaces require access |
| agent skill / LLM | SKILL.md, scripts, hooks, tool args, outputs, stdout/stderr, temp files | do not execute untrusted skills merely to inspect them |
| external secret store | configuration/policy metadata, not secret values | lack of store access does not prove absence of leaks |
| external validity | provider/user supplied status | this skill never authenticates with the discovered credential |

## Clean-result language

Preferred:

`No candidate secrets were found in the inspected working-tree text scope. Git history and remote CI logs were not inspected.`

Avoid:

`No secrets exist in the repository.`

unless the requested definition of repository coverage is actually satisfied.
