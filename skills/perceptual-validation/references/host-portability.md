# Host Portability

Canonical semantics are host-neutral. Do not name a required vision vendor/model in the core.

Capability levels:

- request design: file/context read only;
- visual review: image/render inspection by an image-capable model or human;
- capture: optional browser/app/page-render capability;
- supplemental deterministic measurements: optional.

Target structural profiles: portable-core, OpenAI/ChatGPT, Codex, Claude, GitHub Copilot/VS Code, and Cursor. Runtime equivalence is not claimed unless the target host actually executes a perceptual review.

If visual review is missing, emit `not-run` or `blocked`; never treat structural package compatibility as perceptual evidence.
