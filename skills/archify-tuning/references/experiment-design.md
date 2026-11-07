# Experiment design

## At a Glance

- **Purpose:** Choose trustworthy comparison designs for Archify diagram optimization.
- **Load when:** Comparing authoring instructions, full prompt-to-diagram workflows, browser output or runtime behavior.
- **Decision impact:** Prevents model, input, timing and visual-state confounds from being mistaken for improvements.

## Contents

- Frozen comparison
- Timing
- Semantic and visual assessment

## Frozen comparison

Pin the source revision, task, baseline/candidate runtimes and any frozen JSON. Record models, reasoning effort and tool access when known; if unknown, say so. Author-run comparisons require independent contexts and comparable tasks. For runtime comparisons, feed both variants the same JSON; for agent instruction comparisons, preserve each original first draft and correction history. Separate synthetic fixtures from real-repository generation cases and do not change the frozen denominator after seeing results.

Use stable replays for renderer/validator rule claims. For authoring outcomes, compare at least one contrasting source/example before claiming general benefit. Record any permitted semantic edits and distinguish data corrections from information deleted merely to satisfy checks. Independently review source meaning, not only element counts.

## Timing

Record task dispatch, actual work start (including reading), first JSON, first usable artifact, reviews and completion. Attribute CLI time and waiting separately; do not call unexplained gaps model thinking. Failed or unfinished attempts remain failures, not faster successes. Parallel agent workloads measure contention unless concurrency is itself the target.

## Semantic and visual assessment

Audit main and exception paths, endpoints, directions, conditions, roles, labels, sources and completeness. Match viewport, zoom, theme, preset, detail mode and scroll position; compare both visible region and necessary long-page states. An automated green receipt verifies defined checks, not semantic truth or perceived readability. A pixel diff alone is not an acceptance judgment. Preserve actual captures and rejected approaches.

Original guidance: [archify-tuning/references/experiment-design.md](https://github.com/ginmp8/archify/blob/a4065941f12be7967436261d9934784e381d423c/.agents/skills/archify-tuning/references/experiment-design.md).
