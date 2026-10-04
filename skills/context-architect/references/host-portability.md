# Host Portability

## Contract

`Context Architect` is a portable Agent Skills workflow. Core semantics must not depend on a vendor-private invocation API, host name, install path, or an OpenAI-only adapter. Host integrations may expose different tools, but they must preserve the same evidence labels, source-class semantics, typed-relation rules, closure/freshness checks, output contract, and stop conditions.

## Capability model

| Capability | Required for | Degraded behavior when absent |
|---|---|---|
| file/repository read | all substantive maps | block exact-path claims and return a provisional discovery plan |
| semantic symbol/reference lookup | high-confidence definitions/references/implementations | fall back to syntax/exact search and label the weaker source class |
| build/project graph | project/target ownership and reverse dependents | infer from project manifests/imports only when evidence supports it; keep unresolved affected-set risk explicit |
| syntax/AST index | parser-backed declarations/imports/calls | use exact lexical search; do not claim semantic precision |
| command execution | measured revision/tests/build/snapshot verification | use observed bytes and label validation `planned` or `blocked` |
| runtime/data-flow analysis | selective extended-tier behavior/source-to-sink questions | keep the branch inferred/unresolved unless other evidence closes it |
| dependency/lockfile inspection | version-specific external API evidence | record external dependency/version evidence as blocked or supplied |
| filesystem write | implementation or durable artifact output | keep work read-only and return the map/plan in the response |
| Python 3.10+ | bundled helper scripts only | perform equivalent inspection manually; do not claim helper execution |
| network/external source access | current external API/version evidence | keep external/current branches unresolved unless supplied evidence is sufficient |

Semantic indexes, build graphs, AST tools, data-flow engines, and external package inspectors are **capability classes**, not required products. A host may satisfy them using LSP/compiler services, repository-native build tools, SCIP-like indexes, parser tooling, CodeQL-like analysis, or equivalent mechanisms.

## Host adapters

`agents/openai.yaml` is optional metadata for OpenAI hosts. It must not contain semantic rules required by the portable core. Claude, GitHub Copilot, Cursor, Codex, and other compatible hosts should use their native filesystem/search/command capabilities rather than requiring a package-specific adapter.

## Python launcher

When a bundled helper is useful, resolve an available Python 3.10+ launcher from the environment (`python3`, `python`, `py -3`, or equivalent). Do not encode one launcher spelling into the semantic contract. Helpers use only the standard library.

## Evidence parity

Different hosts may expose different tooling. Tool differences may change the evidence source class or provenance level, not the truth standard:

- executed tool/command result -> `measured`;
- directly inspected repository bytes -> `observed`;
- user-provided fact -> `supplied`;
- reasoned relationship -> `inferred`;
- future check -> `planned`;
- unavailable required branch -> `blocked`.

A host that cannot execute tests may still produce a valid provisional context map, but it must not report those tests as passed. A host without semantic/build tooling may still map by syntax/text evidence, but must not present that fallback as compiler-backed certainty.
