# Resume, reproducibility and checkpoints

## When to load

Load when resuming prior research, refreshing stale results, applying a schema change, editing items, or claiming repeatability across host/model executions.

## Explicit scope identity

`check_resume.py` calculates semantic hashes of the global research scope plus the **relevant item**, the field contract, the skill VERSION and a canonical fingerprint of `_sources`; raw file hashes are recorded for audit, but comment-only edits do not force re-research. Missing `_run`, changed relevant scope/schema/version/sources or a failed result validator causes `needs-revalidation`. The first stamp requires independently reviewed, research-ready evidence; use `--stamp` only then. This is a guarded, atomic JSON write, not an instruction to fetch sources automatically.

`check_resume.py --max-age-days N` or `research.max_age_days` imposes an age bound on recorded identity. Even a passing age/hash check is **not** proof that source contents are still accurate: its output explicitly sets `freshness_verified=false`. Time-sensitive conclusions require renewed external checks and an appropriately updated source stamp. Stable historical facts may be reused if the task permits and evidence is still relevant.

## Crash safety and concurrency

Use one writer per item; separate filenames by stable IDs or collision-resistant fallback. Write new/changed JSON to a temporary sibling, flush and atomically replace after validation. Never mutate frozen evaluator fixtures or original source artifacts. If concurrency is available, schedule at most `batch_size` groups concurrently, with `items_per_agent` as the grouping hint; otherwise process sequentially and preserve identical validation gates. Parallel workers should not write to the same result path.

## Reproducibility ceiling

Mechanically repeatable: parsing, result validation, identity checks, report ordering, report output and exact fixture comparisons. Not guaranteed deterministic: web search ranking, changing external pages, model-generated analysis, human interpretation and across-model behavior. Pin dates, versions, sources, questions, budget and evaluator whenever performing a paired comparison. Report separately what was reproduced, estimated, observed or not run.
