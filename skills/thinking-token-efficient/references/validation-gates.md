# Validation Gates

## Runtime behavior gate

Before finalizing a response, check:

- final answer addresses the actual user request;
- compression did not remove a material assumption, caveat, citation, validation result, or safety boundary;
- sources and dates are current when required;
- claims about files, commands, tests, packages, or production behavior have evidence labels;
- user-facing text is readable, in the expected language, and not a dump of private reasoning.

## Activation gate

Activate for multi-step private reasoning, tool planning, code/artifact analysis, evidence synthesis, validation-heavy work, or requests to optimize internal thinking. Do not activate for simple direct answers or visible prose compression unless another skill specifically handles it.

## Package validation gate

For package maintenance, pass only when:

- exactly one root `SKILL.md` exists;
- frontmatter name and description are valid;
- referenced files exist;
- activation, non-activation, ambiguous, and edge scenarios exist;
- scripts compile and run at least one smoke check;
- no caches, archives, secrets, or scaffold markers are included;
- package validation passes before reporting a zip path.

## Advisory change gate

For a net-new package, advisory acceptance is enough when structural validation, custom validation, token audit, security/static scan, and archive validation pass. For existing package updates, require a before/after change gate.
