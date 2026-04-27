# MAGO Evidence Contract

Use this reference when a run creates, refines, audits, or validates planning claims that depend on repository truth rather than only structure.

## Purpose

MAGO can make planning artifacts consistent and evidence-aware, but it cannot prove product implementation facts unless those facts are present in inspected repository files, existing canonical planning artifacts, user-provided evidence, or validator output. Treat evidence validation as a control that separates verified structure from unresolved repository truth.

## Evidence Classes

Use the strongest available evidence class for each material claim:

1. repository inspection: code, configs, schemas, tests, migrations, or repository docs inspected in the current run;
2. canonical planning truth: existing board, discovery, catalog, queue, package, notes, or validation artifacts;
3. user-provided roadmap or product evidence: supplied prompt content, linked context, or pasted artifact content;
4. measured validator output: command output produced during the current run;
5. explicit assumption: unresolved but necessary planning assumption recorded in the artifact.

Do not write owner commitments, dependency status, implementation completion, rollout state, validation success, or production-readiness claims unless the claim is backed by one of the first four classes. If only the fifth class exists, record it as an assumption, risk, blocker, or open question.

## Required Traceability

For package-scoped work, preserve or create a traceability trail that answers:

- which discovery, roadmap, repository, or package evidence justified the selected scope;
- which unresolved assumptions remain;
- which validation commands were actually run;
- which facts are intentionally not verified yet.

The manifest should keep a source-of-truth map and traceability summary. Notes or validation artifacts should carry the supporting narrative when the manifest is too small for details.

## Runtime Evidence Boundary

Runtime execution evidence is out of MAGO operating scope. MAGO may record existing execution evidence only when it is already present in repository truth or canonical planning artifacts. It must not run tests, simulate completion, mark runtime validation as passed, or infer production state from a planning request.

## Mechanical Validation

Run scripts/validate_evidence_contract.py when a touched package includes claims about repository facts, validation state, execution state, dependencies, or source traceability. This validator checks that package evidence fields are present, that local source-of-truth paths are resolvable where applicable, and that execution or validation claims are not silently treated as proven without traceability.

The validator does not replace human or live-model review. It is a deterministic gate that catches missing evidence structure, unresolved assumptions disguised as facts, and broken path traceability.
