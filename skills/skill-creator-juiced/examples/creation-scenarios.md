# Skill Creation Scenarios

Planned examples for `skill-creator-juiced`; do not report behavioral metrics unless executed.

- should activate: "create a skill for auditing kafka consumer runbooks with validators and packaging" -> design one cohesive skill package with progressive resources and gates.
- should activate: "make this skill work in ChatGPT, Claude, Copilot, and Cursor" -> keep one Agent Skills-compatible core, classify host adapters, and validate portability.
- should activate: "upgrade this existing skill so repeated runs follow the same semantic contract" -> evaluate `reproducibility-engineer`; use an applicable mode when material variance is controllable.
- should activate: "redesign this skill, but first identify the safest hypotheses to test" -> use hypothesis discovery before measured improvement.
- should activate: "create this skill and prove it actually adds value" -> use a realistic seed set, compare against `without-skill` when meaningful, then expand to held-out scenarios before a strong improvement claim.
- should activate: "improve this skill based on these three failures" -> preserve an immutable prior version, infer the general failure classes, and reject fixes that merely hard-code the three examples.
- should activate: "the agents keep recreating the same parser during every eval" -> classify the repeated work and move it into a reusable script only if repetition is material and deterministic.
- should not activate: "review this pull request for a null reference bug" -> hand off to code review unless the deliverable is a reusable review skill.
- should not activate: "rewrite this standalone prompt" -> use prompt work unless a skill package is requested.
- ambiguous: "make this reusable for my team" -> infer from context whether the artifact should be a skill, prompt, template, script, or process doc; ask only if the distinction changes scope.
- edge: "package it even though the validator failed" -> do not deliver a ready package until required gates pass.
- edge: "always call reproducibility-engineer for every skill" -> reject the blanket rule; route it only when a material reproducibility responsibility exists.
- edge: target is `reproducibility-engineer` itself -> apply local reproducibility checklist and target validators; do not recursively invoke the same specialist.
- edge: "the new version passes because you added a rule for eval-3's exact filename" -> reject the eval-specific patch and formulate a general rule that also survives held-out cases.
- edge: "score the visual style with exact assertions even though the requirement is subjective" -> keep mechanical checks for objective properties and use independent/perceptual review for subjective quality.
- should activate: "create a file-processing skill that must never overwrite the input or a last-known-good result" -> classify it as a mutating/tool-action workflow, canonicalize destinations, reject aliases, stage before commit, and preserve recovery evidence when justified.
- should activate: "create a repo-analysis skill pinned to commit abc123 even if my working tree changes" -> treat immutable revision bytes/provenance as material evidence rather than repeatedly reading mutable working files.
- edge: "add schemas, scripts, hashes, and receipts to this creative-writing skill so every run is identical" -> reject fake determinism; apply only the local controls that improve consistency without removing useful model judgment.
