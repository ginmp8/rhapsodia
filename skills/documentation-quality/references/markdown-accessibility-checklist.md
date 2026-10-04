# Markdown accessibility checklist

Use this checklist when reviewing or improving Markdown accessibility, scanability, and readability. Preserve technical meaning and separate source-level mechanics from rendered/runtime accessibility.

## Source-level checks

### Headings

- Use one `#` H1 per standalone document when that is the target convention.
- Keep heading levels sequential; do not jump from `##` to `####`.
- Make headings descriptive enough to support navigation by outline.
- Prefer task-oriented headings such as `Run the validator` over vague headings such as `More information`.
- Avoid using bold text as a substitute for headings.

### Links

- Use descriptive link text that makes sense outside the sentence.
- Avoid ambiguous link labels such as `here`, `this`, `click here`, or repeated `read more`.
- Prefer local relative links for bundled Skill resources.
- Verify that local links point to existing files or sections when the environment/checker can do so reliably.
- Do not expose long raw URLs when a clear link label is available.

### Lists and procedures

- Use ordered lists only when sequence matters.
- Keep parallel grammar in list items.
- Avoid deeply nested lists; convert complex lists into subsections or compact tables.
- Put conditions before actions when a step depends on a mode, state, or artifact.

### Tables

- Use tables for compact comparisons, mode matrices, gates, or parameter references.
- Keep headers short and meaningful.
- Avoid wide tables that become unreadable in narrow contexts.
- Provide surrounding text when the table encodes important decisions.
- Do not rely on icons/symbols alone to communicate a state.

### Images and diagrams

- Informative images require meaningful alt text or an equivalent nearby text description.
- Empty Markdown alt text is a mechanical warning that requires semantic review: it may represent a decorative image, but the checker cannot prove decorative intent.
- For screenshots, describe the important UI state or decision, not merely that it is a screenshot.
- For charts or complex diagrams, include the conclusion or a nearby text summary.
- Do not invent visual details when the image was not inspected.

### Code blocks and command examples

- Add a language tag to fenced code blocks when known.
- Use shell prompts consistently; avoid copying prompt symbols into commands when they would break execution.
- Separate command input from expected output.
- Mark output as illustrative when not generated from an actual run.
- Avoid fake secrets, production credentials, or private tokens in examples.

### Readability

- Put the most common path before rare edge cases.
- Prefer direct sentences and concrete nouns.
- Break long paragraphs when it improves scanning.
- Define acronyms on first use when the intended reader may not know them.
- Preserve established domain terminology and contracts.
- Load `language-and-global-readiness.md` when ambiguity/terminology or a global audience is material.

## Rendered/runtime accessibility

Source Markdown cannot prove rendered accessibility. When the rendered surface is in scope and the required capabilities exist, inspect relevant behavior such as:

- keyboard reachability and focus order;
- screen-reader interpretation;
- information remaining understandable without images, color, sound, or position-only cues;
- responsive/zoom behavior when the delivery surface matters;
- captions/transcripts for media when present.

If the rendered surface, browser, assistive technology, or equivalent evidence is unavailable, report this layer `not-run` or `blocked`. Do not infer a rendered-accessibility pass from the source checker.

## Final accessibility pass

Before returning changes, check:

- heading outline is logical;
- links are descriptive;
- local links and referenced files were verified or gaps were recorded;
- tables are not being used for large prose blocks;
- informative images have alt text/text equivalents, while decorative intent is explicitly reviewed;
- examples remain understandable without visual-only cues;
- rendered/runtime accessibility status is separate from source-level status.
