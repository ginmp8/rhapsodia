# Skill Creation Scenarios

Planned examples for `skill-creator-juiced`; do not report metrics unless executed.

- should activate: "create a skill for auditing kafka consumer runbooks with validators and packaging" -> design a cohesive skill package with resources, validation, and package gates.
- should activate: "upgrade this skill with benchmark, hardening, cleanup, and token efficiency" -> orchestrate specialist passes, freeze evaluation, validate, and report evidence.
- should not activate: "review this pull request for a null reference bug" -> hand off to code review unless the user wants a skill around it.
- should not activate: "rewrite this standalone prompt only" -> hand off to prompt-architect unless skill packaging is requested.
- ambiguous: "make this reusable for my team" -> infer or ask whether the artifact is a skill, prompt, template, script, or process doc.
- edge case: "package it even though the validator failed" -> do not claim readiness or return `skill.zip` until validation and package checks pass.

- should activate quality gate path: "update this existing skill and make sure the patch does not regress activation or safety" -> use `skill-change-gate` or its checklist before accepting material changes and packaging.
