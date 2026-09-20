# Host Portability

The semantic core is Agent Skills-compatible and uses relative files, JSON contracts, and standard-library Python helpers. Do not require a vendor-private invocation API.

Detect capabilities instead of branching on product name:

- readable/writable filesystem;
- Python 3.10+ or equivalent execution;
- ability to invoke caller-provided mutation/evaluation actions;
- artifact/report delivery.

If mutation/evaluation actions cannot be invoked, use `plan-only`, `selection-only`, or `validation-only`. Never fabricate candidate creation or measured evaluation.

Treat `agents/openai.yaml` as optional UI metadata, not part of search semantics.
