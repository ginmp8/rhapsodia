---
name: context-architect
description: use when asked to map, plan, review, or safely execute repository changes whose impact may cross files, modules, services, tests, generated artifacts, configuration, schemas, or dependency boundaries. builds evidence-backed context maps by tracing definitions, consumers, runtime wiring, ownership, tests, patterns, risks, and validation; uses explicit evidence provenance, source precedence, bounded search and closure rules, and stale-map checks before implementation. use for refactors, features, migrations, pull requests, dependency-impact analysis, and cross-module bugfixes. do not use for self-contained snippets, non-code product planning, or skill-package work unless repository context mapping is the task.
---

# Context Architect

## Purpose

Map repository context before multi-file work so implementation starts from current evidence rather than guessed structure. For the same task and materially identical repository evidence, repeated runs should identify materially equivalent owners, consumers, risks, validation surfaces, and change order. Exact prose is not required to be identical.

## Core rules

1. Build a context map before modifying repository files when scope is multi-file, cross-boundary, or uncertain.
2. Treat repository evidence as primary; label inference instead of presenting it as observation.
3. Trace the owning source and relevant consumers before proposing edits. Do not stop at the first plausible file.
4. Use bounded, quality-aware context selection and explicit closure criteria. More files are not automatically better context; prefer the smallest evidence set that closes the required branches.
5. Before implementing from an approved map, verify that the evidence used by the map is still current. Refresh only invalidated branches unless a central contract changed.
6. Never invent paths, call sites, tests, commands, ownership, runtime wiring, or validation results.

## Scope

Own repository context mapping for code changes, refactors, feature implementation plans, dependency-impact analysis, PR preparation, code-review planning, migration planning, and execution after an approved map.

Do not own product governance, generic single-snippet explanation, skill-package hardening, or implementation that bypasses repository evidence.

## Host portability gate

Keep the core portable across compatible Agent Skills hosts. `agents/openai.yaml` and other host-specific adapters are optional and cannot own semantic rules. Before mapping, detect the runtime capabilities needed by the selected mode: filesystem/repository read, search/reference lookup, command execution, write access, Python helper availability, and network access when external freshness is required. Missing capability lowers the evidence level or makes the affected branch `blocked`; it never authorizes invented evidence.

For reusable maps, freeze evidence identities before implementation and revalidate them on reuse. Load `references/host-portability.md` for detailed degradation rules and launcher guidance.

## Modes

| User intent | Mode | Primary output | Edit allowed |
|---|---|---|---|
| Understand scope before work | `context-map-only` | evidence-backed context map | no |
| Prepare implementation | `implementation-plan` | context map plus ordered plan | no |
| Review a diff or PR | `review-impact` | impacted surfaces, hidden dependencies, risks, test gaps | no |
| Continue from an approved map | `apply-after-approved-map` | refreshed map branches, edits, validation summary | yes, after freshness checks |

## Required inputs

Resolve or conservatively infer these before finalizing a map:

1. Task or change objective.
2. Repository identity when available: root, revision/HEAD, dirty state, branch/worktree context, or a bounded set of supplied files.
3. Available evidence: paths, diff, stack trace, failing test, issue, symbols, config keys, or searchable codebase.
4. Mode from the table above.
5. Safety constraints: blocked/read-only paths, generated files, migrations, secrets, production data, access-control surfaces.
6. Validation expectation: tests, build, lint, type check, reproduction command, runtime check, or reason validation is unavailable.
7. Evidence tier: `focused`, `standard`, or `extended`.
8. Final artifact expectation when material: chat map/plan only, repository edits, or a durable context-map artifact.

### Evidence tier selection

- `focused`: small internal change with known owners and direct consumers already found.
- `standard`: default for ordinary multi-file work; trace owners, direct consumers, runtime wiring/config, nearest tests, and one analogous pattern.
- `extended`: public API/schema, migration, auth/security, cross-service/distributed behavior, generated clients, externally consumed contracts, or other high-ripple work. Include downstream boundaries, deployment/rollback, compatibility, and dynamic-consumer risks.

Do not choose `focused` merely to save tokens when scope is uncertain.

## Evidence discipline

Read `references/evidence-and-scope-control.md` whenever repository evidence must be selected, conflicting sources exist, the map may be reused later, or scope is broad.

Use these labels when materially useful:

- `measured`: command/tool execution result;
- `observed`: directly inspected repository bytes or diff;
- `supplied`: user-provided fact not independently verified;
- `inferred`: conclusion from evidence that is not directly present;
- `planned`: proposed future state;
- `blocked`: evidence could not be obtained.

When evidence conflicts, apply the precedence rules in the reference and report unresolved conflicts instead of silently picking the convenient source.

## Evidence acquisition model

Load `references/dependency-tracing.md` when selecting repository evidence. Classify both the **provenance label** and, when material, the **evidence source class**: semantic index, build/project graph, syntax/AST, runtime/data-flow, exact lexical search, semantic/fuzzy retrieval, or historical association.

Prefer stronger repository-native evidence for the relation being claimed, but do not require a specific vendor/tool. Represent material dependencies with typed directional relations such as `calls`, `implements`, `runtime-registers`, `build-depends-on`, `tested-by`, or `generated-from`. For `review-impact`, use a base/head or changed-file anchor when available, then follow reverse dependents with bounded multi-hop expansion rather than unbounded transitive search.

When a frozen gold/reference context exists, load `references/context-selection-evaluation.md` and evaluate selection quality separately from final implementation. If no useful local repository context exists, return `no-useful-local-context` rather than forcing a plausible path.

## Progressive loading

Use `SKILL.md` as the control plane. Load a supporting reference only when its branch is active: evidence/scope, dependency tracing, context-selection evaluation, map rendering, implementation sequencing, risk/validation, parallelization, or host portability. This keeps context bounded without changing the output contract.

## Context mapping workflow

Use repository-native tools first; use shell search only when appropriate. Follow the canonical search order in `references/dependency-tracing.md`.

1. **Normalize the task** into one sentence and identify the expected behavior change or investigation boundary.
2. **Establish repository identity** and record the evidence tier. If the map will be reused for implementation, capture stable identities for the files that materially support the map when tooling allows.
3. **Find the owning source** with the strongest available evidence class: definitions, contracts, schemas, generators, handlers, configuration owners, or source artifacts behind generated outputs.
4. **Trace typed direct relations**: usages/calls, imports/exports, implementations/inheritance, generated-from relationships, writers/readers, registrations, tests, and public/data boundaries. Record direction and material hop when it explains scope.
5. **Trace reverse impact and runtime/build wiring**: for a diff/change-set, map changed files to owners and reverse dependents; inspect dependency injection, routers, schedulers, workers, project/build targets, feature flags, deployment/configuration, CODEOWNERS, and generator commands.
6. **Find tests and validation**: nearest unit/integration/contract/migration/e2e coverage and repository-native commands.
7. **Find one or more analogous patterns** only after the owning and consumer paths are known.
8. **Map ripple effects**: compatibility, data migration, concurrency/idempotency/ordering, security, observability, rollout, generated-source drift, external-consumer uncertainty, and dependency-version risk. In `extended`, selectively consider data-flow/runtime evidence when references cannot close a behavior/source-to-sink branch. When downstream work may be decomposed, load `references/parallelization-map.md` and capture evidence-backed dependency edges, shared reads, write conflicts, barriers, isolation needs, and merge ownership.
9. **Apply bounded closure criteria** from `references/evidence-and-scope-control.md`. Expand multi-hop only while it closes a required branch or risk class. Stop when the selected tier is closed; otherwise mark the map `provisional`, `blocked`, or `no-useful-local-context` as appropriate and name the unresolved boundary.
10. **Render the map** using `references/context-map-contract.md`. Order entries using its canonical ordering and tie-breakers. When a gold/reference context exists, attach executed context-selection metrics from `references/context-selection-evaluation.md`; otherwise state that those metrics are not available.

## Context freshness and reuse

For `apply-after-approved-map`:

1. Verify repository identity and the evidence used by the approved map before editing.
2. When available, use `scripts/context_evidence_snapshot.py` to capture or verify hashes for the selected primary/critical-secondary files. Keep evidence manifests outside the repository unless the user explicitly wants them committed.
3. If only a leaf file changed, refresh that dependency branch and affected risks/tests.
4. If a central contract, schema, generator source, dependency registration, or public boundary changed, refresh the wider consumer graph before editing.
5. If verification is unavailable, re-read every primary file and all critical secondary files before implementation and mark freshness as `observed`, not `measured`.

A previous map is planning evidence, not permanent source truth.

## Evidence layers and claim discipline

Keep evidence layers separate:

- **structural**: package/map shape, references, hashes, static contracts;
- **semantic-review**: judgment that selected relations, scope, requirements, or mitigations are appropriate;
- **behavioral**: an actual mapper/agent/retriever executed against frozen tasks or gold context;
- **runtime**: repository/build/test/tool commands executed in the relevant environment;
- **package-integrity**: frozen candidate/package/receipt hashes match exact delivered bytes.

Do not call structural checks measured behavioral improvement. Freeze evaluator/gold inputs before baseline-candidate comparisons. After a final passing candidate is frozen, any later edit invalidates affected validation and requires revalidation.

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

If repository access is incomplete, mark the map `provisional` and state exactly which evidence branch is missing. Do not convert inferred paths into concrete paths for presentation convenience.

## Implementation workflow after approval

1. Verify freshness of the evidence used by the approved map.
2. Re-read primary files immediately before editing.
3. Apply changes in dependency order from `references/change-sequencing.md`.
4. Keep each edit aligned with an observed repository pattern or explicitly justify a new pattern.
5. Update/add tests near changed behavior and preserve compatibility controls identified by the map.
6. Run the narrowest useful validation first, then broader validation for shared/public/infrastructure surfaces.
7. Compare the implemented change against the approved map; report material map drift rather than silently expanding scope.
8. Summarize changed files, measured/observed validation, residual risks, and any follow-up split.

## Review and PR splitting

- Prefer smaller PRs when work spans unrelated ownership boundaries, schema plus application changes plus cleanup, public contract changes plus broad rewrites, generated code plus generator/source changes, or mechanical refactors plus behavior changes.
- Warn about breaking changes before edits.
- Prefer expand-contract for migrations and externally consumed contracts when compatible with the task.
- Never directly repair generated output without identifying its owning source/generator first, unless the repository explicitly treats that output as authoritative source.

## Supporting resources

- `references/context-map-contract.md`: versioned output contract, ordering, confidence, and compact forms.
- `references/evidence-and-scope-control.md`: provenance, source precedence, context budget, closure, conflict, and freshness rules.
- `references/dependency-tracing.md`: evidence source classes, typed relation vocabulary, bounded multi-hop/reverse-impact tracing, and ecosystem heuristics.
- `references/context-selection-evaluation.md`: frozen-gold precision/recall/F1, budgeted-yield, unsupported-selection, no-gold/abstention, and evidence-layer claim rules.
- `references/change-sequencing.md`: safe ordering, PR splitting, map drift, and validation strategy.
- `references/risk-and-validation-checklist.md`: risk checklist and validation evidence levels.
- `references/upstream-source.md`: attribution and adaptation notes.
- `references/host-portability.md`: capability-first multi-platform behavior and adapter boundaries.
- `references/parallelization-map.md`: evidence-backed work-unit dependencies, read/write conflicts, safe parallel groups, barriers, isolation, and merge ownership for downstream orchestration.
- `assets/templates/context-map.md.template`: reusable context-map/2.1 template.
- `scripts/generate_context_map_skeleton.py`: generate a context-map/2.1 skeleton.
- `scripts/context_evidence_snapshot.py`: capture/verify selected repository evidence hashes with machine-readable diagnostics.
- `scripts/evaluate_context_selection.py`: deterministically evaluate frozen path-level context-selection fixtures; synthetic regressions are not behavioral benchmark evidence.
- `scripts/validate_context_architect_skill.py`: validate package structure, references, scripts, and scenario schemas.
- `scripts/package_skill.py`: build a deterministic `skill.zip` with canonical output-path preflight, staged verification, last-known-good restoration, atomic replacement, and optional receipt.
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
