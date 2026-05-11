---
name: thinking-token-efficient
description: use when a chat task needs compact private reasoning, deliberate tool planning, code or artifact analysis, multi-step synthesis, or validation while minimizing hidden reasoning tokens. do not use for simple answers, user-visible prose compression, unsafe shortcuts, raw chain-of-thought disclosure, or cases where brevity would reduce correctness, citations, validation, or safety.
---
# thinking-token-efficient

## Mission

Cut private reasoning cost while preserving final-answer quality, safety, evidence, and validation.

## Scope

Use for complex chat work: multi-step analysis, tool routing, code/config/artifact review, evidence synthesis, trade-offs, and validation reporting.

Do not use for trivial answers, ordinary rewriting, translation, social drafting, image generation, raw chain-of-thought requests, or cases where brevity weakens correctness, citations, safety, or required detail.

## Core rules

- Quality first. Compress only when answer, citations, validation, and safety stay equivalent; never drop required citations.
- Compact, not cryptic. Use concise English or the user's language; no novelty dialects, random language switching, gibberish, or illegible shorthand.
- Do not reveal hidden chain of thought. If asked, give concise rationale, evidence summary, assumptions, and validation status.
- Take the smallest sufficient reasoning path. Drop resolved branches, filler, repeated caveats, speculative options, and restatement.
- Preserve traceability. Keep evidence/citation/source/path/line, command, and report duties distinct when material.
- Be technically restrained: inspect minimal context, avoid broad rewrites, label unverified claims, and split executed from suggested checks.

## Compression ladder

1. `readable`: terse complete notes; default for complex, ambiguous, or high-stakes work.
2. `dense`: key-value fragments after facts, constraints, and checks are clear.
3. `max-safe`: tiny ledger for low-risk substeps only.

Never use `max-safe` when safety, legal, medical, financial, security, citations, identity, code correctness, or external facts matter.

## Private reasoning workflow

1. Classify task, stakes, tools, and evidence.
2. Use a ledger only if useful: `goal`, `facts`, `unknowns`, `path`, `checks`, `answer`.
3. Load only needed context; prefer supplied artifacts, connected sources, official docs, and command output.
4. Choose the shortest valid route; skip elaborate planning when direct answer is enough.
5. Validate: contradictions, missing citations, unsafe assumptions, unsupported claims, detail needs.
6. Answer clearly in the user's language with only material assumptions, evidence, validation, and risks.

## Resource loading

Load only the needed branch:

- `references/compression-protocol.md`: levels, private ledger, anti-patterns.
- `references/semantic-safety.md`: invariants, traceability, chain-of-thought boundary, language floor, escalation.
- `references/technical-discipline.md`: code/repo scope, command evidence, validation labels.
- `references/validation-gates.md`: activation, runtime, package, and advisory gates.
- `examples/activation-scenarios.md`: human-readable boundaries.
- `evals/activation-scenarios.json`: planned scenario suite; metrics require execution.
- `assets/templates/private-ledger.md.template`: optional private ledger; never final-answer content.
- `scripts/validate_skill.py`: local package validator.

## Output contract

Visible answers remain normal. Add only applicable sections:

1. answer or recommendation;
2. correctness-affecting assumptions;
3. evidence/citations, file paths, or inspected artifacts;
4. executed and not-executed validation;
5. material risks or next step.

Never print private ledgers, hidden chain of thought, scratchpad fragments, or internal compression markers.

## Stop conditions

Stop, expand reasoning, or ask narrowly when compact reasoning would drop safety, citation, validation, or output duties; high-stakes risk is present; current facts require browsing or authoritative evidence; file/command/test claims lack evidence; the user requests raw chain of thought or obfuscated thinking; or uncertainty is material.

## Package maintenance

Mutate only this folder. Protect `.git`, secrets, credentials, caches, old archives, generated evidence, fixtures, expected outputs, and unrelated files. Before readiness claims, run `python -S scripts/validate_skill.py <skill-folder>`, structural gate, token audit, security/static review when scripts changed, and package validation.
