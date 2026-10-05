# Mature Skill Patterns

## Preserve

1. **Scope/authority boundary:** owned artifact family, explicit non-goals, handoffs, protected evidence, and unknowns.
2. **Mode before work:** select one primary mode from intent/inputs/outputs/closure; use a mode matrix only when multiple modes genuinely exist.
3. **Portable core:** one host-neutral Agent Skills workflow; isolate host adapters and discovery/install concerns.
4. **Top-100 progressive loading:** keep `SKILL.md` as the control plane. If it exceeds 100 physical lines, the first 100 must expose purpose/scope, discriminative activation/non-use boundaries, material mode choice, usable workflow, critical invariants, and direct pointers. Long editable supporting Markdown should expose an early decision-useful `Purpose` / `Load when` / `Decision impact` preview. Prefer `SKILL.md -> supporting file`; do not hide required instructions behind multi-hop Markdown chains.
5. **Need-aware resources:** scripts/references/templates/examples/evals are optional. Add them only when they reduce variance, encode a stable artifact, or produce useful evidence; presence alone is not maturity.
6. **Deterministic helpers:** use scripts for fragile/repeated mechanics, not as ornamental wrappers around clear instructions.
7. **Template-backed artifacts:** keep reusable templates operationally connected to a fill/copy/writer/validator path when their structure matters.
8. **Truthful closure:** exact commands, gate states, files changed, evidence layer, blockers, and residual risk before completion claims.
9. **Stop/rollback:** explicit conditions preventing invented facts, unsafe writes, evaluator weakening, or invalid delivery.
10. **Research traceability when applicable:** research-backed changes need evidence→finding→requirement→change→evaluation justification and semantic review.

## Avoid

- long `SKILL.md` carrying every branch/example;
- optional resources added only to improve a score;
- resources with no use/loading/integration path;
- target-owned package builder copied into every skill despite no target-specific need;
- universal scenario-count requirements unrelated to a claim;
- host-private dependencies in the semantic core;
- structural scores presented as behavioral proof;
- benchmark results without frozen evaluators/executed evidence;
- post-pass cosmetic edits without revalidation;
- research prose copied into the target without an operational requirement.
