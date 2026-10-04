# Environment and Runtime Provenance

Use this profile only when model, host/harness, tool access, dependencies, locale/timezone, cache/concurrency, or budget can materially change a paired evaluation. Static repairs do not need it.

## Contract

Capture one capability-based runtime identity per evaluated arm. Prefer fields the host can actually expose; never fabricate provider-private ids. At minimum record:

- model/engine identity at the strongest available granularity;
- reasoning profile when exposed and material;
- host or harness identity;
- tool/capability surface;
- environment/dependency facts that can change the result;
- material budget such as attempts, tokens, or wall time when available.

Use `assets/templates/execution-environment.json.template` as a portable skeleton and `assets/schemas/execution-environment.schema.json` as the structural contract. `scripts/validate_execution_evidence.py --kind environment` validates the portable required fields and emits a canonical identity digest.

## Comparison rule

For `no-skill`, `parent`, and `candidate` paired evidence, material runtime identity must be equivalent. If a material field drifts, mark the comparison non-equivalent or explicitly re-baseline. Do not normalize away differences merely to keep a result comparable.

Host names are evidence, not branching semantics: core behavior remains capability-based across OpenAI/ChatGPT, Codex, Claude, GitHub Copilot, Cursor, and other Agent Skills-compatible hosts.
