---
name: context-architect
description: use when a repository change may cross files, modules, services, tests, generated artifacts, configuration, schemas, runtime wiring, or dependency boundaries and the agent must map owners, consumers, risks, validation, and safe change order before editing. use for refactors, features, migrations, pull requests, dependency-impact analysis, cross-module bugfixes, or implementation from an approved map. do not use for self-contained snippets, generic code explanation, product/governance planning, or skill-package work unless repository context mapping itself is the task.
---

# Context Architect

## Mission and activation boundary

Build the smallest evidence-backed repository context map that is sufficient to plan, review, or safely execute a multi-file or cross-boundary change. Repository evidence is primary; inference stays labeled. Repeated runs over materially identical evidence should converge on materially equivalent owners, consumers, risks, validation surfaces, and change order.

Use this skill before edits when scope is multi-file, cross-boundary, high-ripple, or uncertain. It may continue into implementation only in `apply-after-approved-map` after freshness checks. Do not use it to replace product governance, domain ownership, generic single-snippet help, skill-package optimization, or debugging whose primary goal is root-cause diagnosis rather than repository impact mapping.

## Critical invariants

1. Map before modifying repository files when scope is multi-file, cross-boundary, or uncertain.
2. Trace the owning source plus relevant consumers; never stop at the first plausible file or patch generated output before finding its source/generator.
3. Prefer the smallest evidence set that closes the required branches; extra files are not automatically better context.
4. Never invent paths, call sites, tests, commands, ownership, runtime/build wiring, external consumers, or validation results.
5. Label evidence as `measured`, `observed`, `supplied`, `inferred`, `planned`, or `blocked`; weaker evidence must not be worded as stronger evidence.
6. Before implementing from an approved map, revalidate the evidence identity. Refresh only invalidated leaf branches unless a central contract/schema/generator/registration/public boundary changed.
7. High-risk/public/schema/security/destructive work stays blocked when unresolved consumers, compatibility, rollback/recovery, or required validation materially affect safety.

## Modes

| User intent | Mode | Primary output | Edit allowed |
|---|---|---|---|
| Understand scope before work | `context-map-only` | evidence-backed context map | no |
| Prepare implementation | `implementation-plan` | context map plus ordered plan | no |
| Review a diff or PR | `review-impact` | impacted surfaces, hidden dependencies, risks, test gaps | no |
| Continue from an approved map | `apply-after-approved-map` | refreshed map branches, edits, validation summary | yes, only after freshness checks |

## Evidence tiers

- `focused`: small internal change where owners and direct consumers are already known; still verify nearest tests and required wiring.
- `standard`: default for ordinary multi-file work; trace owners, direct consumers, runtime/config/build wiring, nearest tests, and one analogous pattern.
- `extended`: public API/schema, migration, auth/security, cross-service/distributed behavior, generated clients, external contracts, or other high-ripple work; include downstream boundaries, compatibility, rollout/rollback, dynamic consumers, and selective runtime/data-flow evidence when static relations cannot close the branch.

Do not select `focused` merely to save tokens when scope is uncertain.

## Direct branch map

Load only a branch that changes the current decision; every required Markdown is reachable directly from this file.

- [`references/evidence-and-scope-control.md`](references/evidence-and-scope-control.md): load when selecting evidence, resolving conflicts, setting context budget/closure, or reusing a map; determines source precedence, closure, freshness, and dynamic/external-consumer treatment.
- [`references/dependency-tracing.md`](references/dependency-tracing.md): load when finding owners/consumers, reverse impact, or multi-hop relations; determines evidence-source classes, typed relation direction, canonical search order, and bounded traversal.
- [`references/context-map-contract.md`](references/context-map-contract.md): load before rendering or validating a map; fixes required fields, canonical order, confidence, compact form, and question discipline.
- [`references/change-sequencing.md`](references/change-sequencing.md): load when converting an approved map into implementation work; controls pre-edit freshness, dependency-safe order, PR splitting, and validation ladder.
- [`references/risk-and-validation-checklist.md`](references/risk-and-validation-checklist.md): load before finalizing a map or implementation summary; enumerates material context/code/data/deployment/security risks and validation-strength labels.
- [`references/context-selection-evaluation.md`](references/context-selection-evaluation.md): load only when frozen gold/reference context exists; defines selection metrics and prevents retrieval metrics from being misreported as implementation correctness.
- [`references/parallelization-map.md`](references/parallelization-map.md): load only when downstream work decomposition or concurrency is material; records dependency edges, shared reads, write conflicts, barriers, isolation, and merge ownership without authorizing execution.
- [`references/host-portability.md`](references/host-portability.md): load when host/tool capability changes available evidence; defines degraded behavior without relaxing truth standards.

## Quick-start workflow

1. Normalize the task into one behavior/investigation boundary; choose mode and evidence tier.
2. Establish repository identity: root or supplied-file boundary, revision/HEAD and dirty state when available, plus base/head or change-set anchor for `review-impact`.
3. Find the owning source: definitions, contracts, schemas, generators, handlers, configuration owners, or source artifacts behind generated outputs.
4. Trace typed direct relations: usages/calls, imports/exports, implementations, generated-from, readers/writers, registrations, tests, and public/data boundaries.
5. Trace reverse impact plus runtime/build wiring: dependency injection, routers, schedulers/workers, project/build graph, flags, deployment/config, CODEOWNERS, generators, and version/lockfile effects when material.
6. Find nearest tests and repository-native validation commands; keep unavailable validation `blocked` or `planned`, never passed.
7. Find an analogous repository pattern only after owner and consumer paths are known.
8. Map ripple effects: compatibility, migration/data, concurrency/idempotency/ordering, security, observability, rollout/rollback, generated-source drift, external/dynamic consumers, and dependency-version risk.
9. Apply bounded closure: expand multi-hop only to close a required branch/risk; otherwise mark `provisional`, `blocked`, or `no-useful-local-context` and name the unresolved boundary.
10. Render using the context-map contract; attach context-selection metrics only when a frozen gold/reference context exists.

## Hard stops before editing

Stop before mutation when repository evidence is unavailable for an uncertain multi-file change; authoritative evidence conflicts on what must change; public/schema/security/destructive work has unresolved safety-critical consumers or rollback/recovery gaps; secrets/credentials/production data/protected paths cannot be handled safely; the user asks to bypass mapping without a current approved map; or required high-risk validation is blocked with no safe substitute.

## Required inputs and normalization

Resolve or conservatively infer before finalizing a map:

1. task/change objective and expected behavior boundary;
2. repository identity or bounded supplied-file set;
3. available evidence: diff, paths, stack trace, failing test, issue, symbols, config keys, schemas, or searchable codebase;
4. mode and evidence tier;
5. safety constraints, blocked/read-only/generated paths, migrations, secrets, production data, and access-control surfaces;
6. validation expectation: tests, build, lint, type check, reproduction command, runtime check, or explicit reason it is unavailable;
7. final artifact expectation: chat map/plan, repository edits, or durable context-map artifact;
8. host/runtime capabilities needed by the selected branch: repository read, semantic/search/build tooling, command execution, write access, Python helpers, and network access when current external evidence is material.

Missing capability lowers the evidence level or makes that branch `blocked`; it never authorizes invented evidence. Host adapters such as `agents/openai.yaml` are optional and cannot own semantic rules.

## Context freshness and reuse

For `apply-after-approved-map`:

1. Verify repository identity and the evidence used by the approved map before editing.
2. When available, use `scripts/context_evidence_snapshot.py` to capture or verify hashes for selected primary/critical-secondary files; keep manifests outside the repository unless the user explicitly wants them committed.
3. If only a leaf changed, refresh that branch and affected risks/tests.
4. If a central contract, schema, generator source, dependency registration, public boundary, or material resolved dependency changed, refresh the wider consumer graph before editing.
5. If verification tooling is unavailable, re-read every primary and critical-secondary file and mark freshness as `observed`, not `measured`.

A previous map is planning evidence, not permanent source truth.

## Evidence layers and claim discipline

Keep evidence layers separate:

- **structural**: package/map shape, references, hashes, static contracts;
- **semantic-review**: judgment that selected relations, scope, requirements, or mitigations are appropriate;
- **behavioral**: an actual mapper/agent/retriever executed against frozen tasks or gold context;
- **runtime**: repository/build/test/tool commands executed in the relevant environment;
- **package-integrity**: frozen candidate/package/receipt hashes match exact delivered bytes.

Do not call structural checks measured behavioral improvement. Freeze evaluator/gold inputs before baseline-candidate comparisons. After a final passing candidate is frozen, any later material edit invalidates affected validation and requires revalidation.

## Output contract

Use `references/context-map-contract.md`. Full maps must include, in canonical order:

1. contract/repository evidence identity;
2. scope classification and evidence tier;
3. primary files/owners;
4. secondary files and consumers;
5. test/validation evidence;
6. patterns to follow;
7. source conflicts or unresolved dynamic/external consumers when present;
8. ripple effects and risks;
9. coverage/closure status;
10. suggested sequence;
11. optional parallelization map when execution topology is material;
12. blocking questions only.

If repository access is incomplete, mark the map `provisional` and state exactly which evidence branch is missing. Never convert inferred paths into concrete paths for presentation convenience.

## Implementation workflow after approval

1. Verify freshness of the approved map evidence and re-read primary files immediately before editing.
2. Apply changes in dependency order from `references/change-sequencing.md`.
3. Keep each edit aligned with an observed repository pattern or explicitly justify a new pattern.
4. Update/add tests near changed behavior and preserve compatibility controls identified by the map.
5. Run the narrowest useful validation first, then broader validation for shared/public/infrastructure surfaces.
6. Compare implementation with the approved map; report material map drift instead of silently expanding scope.
7. Summarize changed files, measured/observed validation, residual risks, and any follow-up split.

## Review and PR splitting

Prefer smaller PRs when work spans unrelated ownership boundaries; schema plus application plus cleanup; public contract plus broad call-site rewrite; generated code plus generator/source; dependency-version migration plus unrelated cleanup; or mechanical refactor plus behavior change. Warn about breaking changes before edits, prefer expand-contract when compatible, and never repair generated output without first identifying its owning source/generator unless the repository explicitly treats that output as authoritative.

## Supporting resources

- `references/context-map-contract.md`: versioned output contract, ordering, confidence, and compact forms.
- `references/evidence-and-scope-control.md`: provenance, source precedence, context budget, closure, conflict, and freshness rules.
- `references/dependency-tracing.md`: evidence source classes, typed relation vocabulary, bounded multi-hop/reverse-impact tracing, and ecosystem heuristics.
- `references/context-selection-evaluation.md`: frozen-gold precision/recall/F1, budgeted-yield, unsupported-selection, no-gold/abstention, and evidence-layer claim rules.
- `references/change-sequencing.md`: safe ordering, PR splitting, map drift, and validation strategy.
- `references/risk-and-validation-checklist.md`: risk checklist and validation evidence levels.
- `references/host-portability.md`: capability-first multi-platform behavior and adapter boundaries.
- `references/parallelization-map.md`: evidence-backed work-unit dependencies, read/write conflicts, safe parallel groups, barriers, isolation, and merge ownership.
- `references/upstream-source.md`: attribution, research inspirations, and adaptation notes; background only, never required for execution.
- `assets/templates/context-map.md.template`: reusable context-map/2.1 template.
- `scripts/generate_context_map_skeleton.py`: generate a context-map/2.1 skeleton.
- `scripts/context_evidence_snapshot.py`: capture/verify selected repository evidence hashes with machine-readable diagnostics.
- `scripts/evaluate_context_selection.py`: deterministically evaluate frozen path-level context-selection fixtures; synthetic regressions are not behavioral benchmark evidence.
- `scripts/validate_context_architect_skill.py`: validate package structure, Top-100 control-plane coverage, direct reference reachability, semantic previews for long Markdown, scripts, links, and scenario schemas.
- `scripts/package_skill.py`: build a deterministic `skill.zip` with output-path preflight, staged verification, last-known-good restoration, atomic replacement, and optional receipt.
- `evals/activation-scenarios.json`: frozen planned activation and boundary scenarios; not measured unless executed externally.
- `evals/reproducibility-scenarios.json`: planned provenance, stale-map, conflict, closure, and evidence-layer scenarios; not measured unless executed externally.
- `evals/context-selection-fixtures.json`: deterministic synthetic calibration fixtures for selection metrics; not real-repository behavioral evidence.
- `examples/example-context-map.md`: calibrated example.

## Stop conditions

Stop before editing and report the blocker when:

- repository evidence is unavailable and the requested change could affect unknown files;
- authoritative evidence conflicts and the conflict changes what must be edited or validated;
- a public/schema/security/destructive change has unresolved external or dynamic consumers that materially affect safety;
- secrets, credentials, production data, authorization rules, or protected paths cannot be handled safely;
- destructive data work lacks migration, compatibility, rollback, or recovery evidence;
- the user asks to skip mapping for a multi-file/uncertain change and no current approved map exists;
- high-risk validation is blocked and there is no safe substitute for implementation confidence.
