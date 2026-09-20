# Host Portability

## Contract

`Context Architect` is a portable Agent Skills workflow. Core semantics must not depend on a vendor-private invocation API, host name, install path, or an OpenAI-only adapter. Host integrations may expose different tools, but they must preserve the same evidence labels, closure rules, freshness checks, output contract, and stop conditions.

## Capability model

| Capability | Required for | Degraded behavior when absent |
|---|---|---|
| file/repository read | all substantive maps | block exact-path claims and return a provisional discovery plan |
| search/reference lookup | consumer tracing | use available repository-native search; unresolved dynamic/consumer branches stay explicit |
| command execution | measured revision/tests/build/snapshot verification | use observed bytes and label validation `planned` or `blocked` |
| filesystem write | implementation or durable artifact output | keep work read-only and return the map/plan in the response |
| Python 3.10+ | bundled helper scripts only | perform equivalent inspection manually; do not claim helper execution |
| network | current/external evidence only | keep external/current branches unresolved unless supplied evidence is sufficient |

## Host adapters

`agents/openai.yaml` is optional metadata for OpenAI hosts. It must not contain semantic rules required by the portable core. Claude, GitHub Copilot, Cursor, Codex, and other compatible hosts should use their native filesystem/search/command capabilities rather than requiring a package-specific adapter.

## Python launcher

When a bundled helper is useful, resolve an available Python 3.10+ launcher from the environment (`python3`, `python`, `py -3`, or equivalent). Do not encode one launcher spelling into the semantic contract. Helpers use only the standard library.

## Evidence parity

Different hosts may expose different tooling. Tool differences may change the evidence level, not the truth standard:

- executed tool/command result -> `measured`;
- directly inspected repository bytes -> `observed`;
- user-provided fact -> `supplied`;
- reasoned relationship -> `inferred`;
- future check -> `planned`;
- unavailable required branch -> `blocked`.

A host that cannot execute tests may still produce a valid provisional context map, but it must not report those tests as passed.
