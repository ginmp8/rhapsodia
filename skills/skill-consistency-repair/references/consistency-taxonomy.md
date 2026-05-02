# Consistency Taxonomy

Use to classify target skill audit and repair findings.

## Severity

- `blocker`: package cannot be trusted or safely packaged: missing/multiple `SKILL.md`, invalid frontmatter, broken required local links, unsafe secrets, post-repair validator failure, or core ownership contradiction.
- `high`: likely wrong activation or artifacts: activation conflicts with scope, role contradicts owned artifacts, modes overlap, stop conditions contradict workflow, or output-critical resources are absent.
- `medium`: runnable but brittle: useful resources unreferenced, scenario gaps, weak output contract, undocumented scripts, templates without usage rules, validators not mentioned.
- `low`: clarity/hygiene: stale wording, duplicate examples, minor metadata mismatch, inconsistent casing, non-critical generated files.

## Categories

1. **Package structure**: exactly one root, one `SKILL.md`, minimal YAML frontmatter if present, expected directories, readable text resources, no cache/generated-report pollution, no nested roots unless documented.
2. **Activation and scope**: compare frontmatter description, scope, positive/negative triggers, modes, stops. Flag broad activation, implementation ownership while body forbids it, governance-only scope with architecture artifacts, or packaging allowed while stops forbid archives.
3. **Ownership and role**: owned artifacts must match declared responsibility, not historical file names. Example: governance may own delivery posture logs, not architecture decisions unless explicitly scoped.
4. **Resource integration**: classify supporting files as loaded reference, script/validator, operational template, example/planned scenario, runtime asset, generated evidence, or placeholder/duplicate/obsolete/misleading. Useful resources need a loading rule, workflow step, script consumer, template-fill instruction, validator, scenario rule, or asset-only rationale.
5. **Output and evidence**: separate measured evidence from plans/assumptions. Flag claims about validation, benchmark scores, package readiness, scenario precision/recall, conformance, or production behavior without command output or supplied results.
6. **Workflow and modes**: mode selection precedes work; each mode defines inputs, output, mutation rights, closure gate. Flag hidden mode mixing, missing stops, unclear handoffs, or mutation before baseline.
7. **Validation and packaging**: archive only after folder/archive validation. Exclude generated reports, caches, old zips, secrets, and evaluator fixtures. Document validators and script CLI usage.

## Finding evidence

Each finding includes path; line/section when available; observed inconsistency; impact; smallest repair; validation gate; severity; confidence. If line evidence is unavailable, cite section or path and say so.
