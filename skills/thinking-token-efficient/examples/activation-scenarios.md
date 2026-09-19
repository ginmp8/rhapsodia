# Activation Scenarios

These examples are explanatory only. `evals/activation-scenarios.json` is the planned machine-readable suite; neither file is measured evidence until executed by a frozen evaluator.

## Should activate

- "optimize internal reasoning tokens while reviewing this diff; preserve validation evidence"
- "plan the minimum tool calls for this multi-step research question"
- "use compact thinking to analyze this artifact with the same result quality"
- "analyze this repository issue efficiently, but inspect the files that determine correctness"

## Should not activate

- "rewrite this email to be more formal"
- "translate this paragraph"
- "what is 2 + 2"
- "make this visible answer shorter for the user"
- "generate an image of a dashboard"

## Ambiguous

- "be concise" means shorten visible output unless the underlying task actually needs private reasoning control.
- "think less" means remove wasted branches, not required checks.
- A request for a reasoning budget is a preference, not permission to weaken hard obligations.

## Boundary and regression cases

- High-stakes security, legal, medical, financial, destructive, or identity-sensitive work must use readable reasoning and preserve verification duties.
- Citations, file paths, exact commands, versions, and numeric limits remain when they affect correctness.
- If validation cannot run, label it not executed instead of implying a pass.
- If asked for raw chain of thought, provide concise rationale and evidence instead.
- Static package size may support a control-plane footprint claim; it does not prove private reasoning-token savings.
- Baseline and candidate token comparisons must use the same declared tokenization method.
- Never edit a frozen evaluator or remove safety/evidence rules to obtain a smaller candidate.
