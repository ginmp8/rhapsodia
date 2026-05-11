# Markdown accessibility checklist

Use this checklist when reviewing or improving Markdown accessibility, scanability, and readability. Apply changes that preserve technical meaning.

## Headings

- Use one `#` H1 per document.
- Keep heading levels sequential; do not jump from `##` to `####`.
- Make headings descriptive enough to support navigation by outline.
- Prefer task-oriented headings such as `Run the validator` over vague headings such as `More information`.
- Avoid using bold text as a substitute for headings.

## Links

- Use descriptive link text that makes sense outside the sentence.
- Avoid ambiguous link labels such as `here`, `this`, `click here`, or repeated `read more`.
- Prefer local relative links for bundled Skill resources.
- Verify that local links point to existing files or sections when the environment allows.
- Do not expose long raw URLs when a clear link label is available.

## Lists

- Use ordered lists only when sequence matters.
- Keep parallel grammar in list items.
- Avoid deeply nested lists; convert complex lists into subsections or tables.
- Put conditions before actions when a step depends on a mode or artifact.

## Tables

- Use tables for compact comparisons, mode matrices, gates, or parameter references.
- Keep headers short and meaningful.
- Avoid wide tables that become unreadable in narrow contexts.
- Provide surrounding text when the table encodes important decisions.
- Ensure every row has the same number of cells.

## Images and diagrams

- Require meaningful alt text for informative images.
- For screenshots, describe the important UI state or decision, not just that it is a screenshot.
- For charts or complex diagrams, include the conclusion or provide a nearby text summary.
- Mark decorative images as decorative only when they carry no technical information.
- Do not invent visual details when the image was not inspected.

## Code blocks and command examples

- Add a language tag to fenced code blocks when known.
- Use shell prompts consistently; avoid copying prompt symbols into commands when they would break execution.
- Separate command input from expected output.
- Mark output as illustrative when not generated from an actual run.
- Avoid fake secrets, production credentials, or private tokens in examples.

## Readability

- Put the most common path before rare edge cases.
- Prefer direct sentences and concrete nouns.
- Break long paragraphs into short paragraphs or bullets when it improves scanning.
- Define acronyms on first use when the intended reader may not know them.
- Preserve established domain terminology and contracts.

## Final accessibility pass

Before returning changes, check:

- heading outline is logical;
- links are descriptive;
- local links and referenced files were verified or gaps were recorded;
- tables are not being used for large prose blocks;
- images have alt text or explicit review gaps;
- examples are readable with assistive technologies and without visual-only cues.
