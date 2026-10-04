# Host Adapters and Portability

Use this reference only when host/model-specific behavior is material.

## Portable-core rule

The semantic contract owns behavior that should survive host changes. Host adapters own volatile execution details such as:

- instruction file/message surfaces;
- precedence/scoping rules;
- tool names and invocation syntax;
- model-specific prompting strategies;
- context placement guidance;
- structured-output/tool-call mechanisms;
- approval and side-effect UI/runtime controls.

Ignoring an optional adapter must leave the core skill coherent.

## Capability first

Do not branch only on product name. Resolve capabilities and instruction surfaces first. Product/provider names are useful identity, not sufficient behavior contracts.

## Adapter workflow

1. identify the requested host/provider/model or capability profile;
2. verify volatile behavior against current authoritative documentation when it matters;
3. isolate host-specific assumptions in an execution profile or adapter section;
4. render the semantic contract into that profile;
5. validate the rendered result with host-specific scenarios when a runtime claim is required;
6. keep portable requirements free from vendor-private invocation APIs.

## Default portability matrix

Target a portable Agent Skills core that can be interpreted on OpenAI/ChatGPT, Codex, Claude, GitHub Copilot, and Cursor when each host exposes the required capabilities.

`agents/openai.yaml` is an optional OpenAI discovery/UI adapter. It must not redefine semantic behavior.

## Instruction-surface differences

Hosts can combine, scope, prioritize, or omit instruction files/messages differently. Therefore:

- never assume one universal file precedence;
- avoid conflicting instruction surfaces;
- record which surfaces were active for behavioral evidence;
- prefer scoped instructions when the host supports them;
- revalidate when surface semantics or enabled files change materially.

## Unknown or unsupported host behavior

If a host-specific prompt depends on semantics that cannot be verified, either:

- produce a host-neutral prompt plus explicit assumptions; or
- mark the host-specific portion blocked/not-validated.

Do not invent a precedence rule or capability for completeness.
