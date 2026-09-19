# Resource Integration Checklist

**Contract version:** 2.0.0

Use for `resource-integration-review` and before any merge, deprecation, or deletion advice.

## Resource states

After consumer tracing, classify resources as one of:

- `integrated`
- `weakly-integrated`
- `misplaced`
- `duplicate`
- `obsolete`
- `generated-debris`
- `orphaned`
- `unknown`

The deterministic inventory state `unresolved-no-evidence` is not equivalent to `orphaned`.

## Consumer tracing gate

Before `obsolete`, `orphaned`, merge, deprecation, or removal advice, inspect:

1. `SKILL.md` path/concept/loading references;
2. reference-to-reference declarations;
3. imports, dynamic imports, reads/writes, path joins, globs, templates, validators, package commands;
4. examples and evals;
5. runtime/asset-only use;
6. host adapters;
7. external consumers indicated by package/repository evidence.

If a relevant consumer surface is unavailable, use `unknown` and state the gap.

## Integration signals

A resource is integrated when evidence shows at least one:

- declared conditional load/run rule;
- script or validator consumer;
- output/template consumer;
- mode/workflow/checklist/stop-condition link;
- intentional runtime/asset-only role;
- eval/example role with planned-versus-measured discipline.

## Duplication review

Duplication is architectural evidence only when it creates drift, contradiction, redundant ownership, unnecessary co-loading, or maintenance burden. Check:

- same consumers and same decision ownership;
- conflicting severity/scoring/mode/output rules;
- always-co-loaded references with duplicated semantics;
- validators enforcing the same gate with different thresholds;
- examples carrying obsolete duplicated contract text.

Do not merge resources that have independent consumers or lifecycle value merely to reduce file count.

## Deletion discipline

Prefer, in order:

1. integrate useful resources;
2. relocate misplaced resources;
3. merge only evidence-backed duplicates;
4. deprecate/delete only with positive evidence of obsolete/orphan/generated state and a validation gate.

A deletion recommendation must include:

- consumer surfaces checked;
- why retention is unnecessary;
- evidence IDs;
- compatibility/migration risk;
- validation gate after removal.
