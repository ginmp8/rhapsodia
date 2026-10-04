# Host Portability

The semantic core follows the portable Agent Skills model. Host-specific metadata is optional and must not be required for correctness.

## Capability model

Resolve capabilities, not product names:

1. `artifact-read` — read reference/candidate images or rendered pages;
2. `metadata-read` — read identities, intended state, capture facts, rubric, and policy;
3. `python-3` / command execution — run the standard-library validator when available;
4. `visual-review` — inspect rendered/image content with a human or image-capable reviewer;
5. `capture-render` — optional browser/app/page capture owned by the caller, not this gate;
6. `deterministic-measurement` — optional pixel/geometry/DOM/layout measurement;
7. `independent-review` — optional second reviewer/adjudicator for stronger policies.

## Structural targets

The portable package is intended to remain structurally usable on:

- portable Agent Skills hosts;
- OpenAI/ChatGPT and Codex;
- Claude-compatible Agent Skills hosts;
- GitHub Copilot/VS Code Agent Skills;
- Cursor Agent Skills.

`agents/openai.yaml` is an optional OpenAI adapter. Ignoring it must leave the workflow, schemas, scripts, and references usable.

## Degradation

- Without visual review: request design and deterministic contract validation can run; perceptual review is `blocked`/`not-run`.
- Without Python execution: visual review can still produce a contract-shaped result, but deterministic validator evidence is `not-run`; do not claim mechanical contract validation passed.
- Without capture/render: compare only supplied artifacts. Do not fabricate a capture state.
- Without independent review: policies requiring agreement cannot pass; return `blocked`/`inconclusive` as appropriate.

## Runtime comparability

A host/model/runtime label is not by itself a visual-state identity. Record only environment/capture facts that can materially alter the reviewed surface. If they differ on a declared comparison key, state alignment cannot be `matched` until the pair is re-normalized or recaptured.

Structural multi-platform validation does not prove equivalent perceptual judgments across hosts or reviewers.
