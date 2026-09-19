# Authority and Conflict Resolution

Resolve contradictions by concern, not by file order or blanket "SKILL.md always wins" rules. Preserve the conflicting evidence until ownership is established.

## Concern-specific authority

| Concern | Primary authority | Dependent surfaces |
|---|---|---|
| Activation, non-activation, scope, modes, stop conditions, role ownership | `SKILL.md` control plane | metadata, references, examples |
| Detailed semantic rules/rubrics | Reference explicitly delegated by `SKILL.md` | examples, templates, reports |
| Machine-readable schema | Schema/validator explicitly declared by the control/reference contract | generators, templates, examples |
| Executable CLI behavior | Script is observed implementation evidence; intended authority comes from the declared contract | docs, examples |
| Evaluator expected outcomes used for acceptance | Frozen evaluator version | candidate implementation; never the reverse during an experiment |
| Templates/assets | Owning output/reference contract | examples, renderers |
| Examples | Never authoritative unless explicitly promoted | must conform to owner |
| Host metadata (`agents/openai.yaml`, Claude/Cursor extensions, etc.) | Adapter only | may narrow host behavior but cannot broaden semantic scope or weaken core gates |
| Packaging/release gate | Hard gate declared by control plane plus its delegated validator | package scripts/receipts |

## Conflict algorithm

1. Identify the exact concern and all competing claims.
2. Trace which surface owns that concern and whether authority was delegated.
3. Record consumers that would be affected by changing either side.
4. If authority is clear, repair the dependent surface with the smallest patch.
5. If authority is unclear or multiple owners are legitimate, classify `contradictory` or `blocked`; do not choose by recency, verbosity, filename, or convenience.
6. For a frozen evaluator conflict, invalidate the experiment, repair/review evaluator separately, freeze a new version, then restart candidate acceptance.
7. Re-run the same gate and adjacent consumer gates.

## Stricter-gate rule

When two sources disagree about a safety, validation, deletion, or packaging gate and ownership is not yet resolved, apply the stricter behavior temporarily and keep the contradiction visible. This is a safety default, not a permanent authority decision.

## Semantic judgment rubric

When judgment remains necessary, report:

- concern being resolved;
- candidate owners;
- direct evidence for each;
- consumer impact;
- compatibility/migration obligations;
- confidence (`high|medium|low`);
- chosen owner or `blocked` decision;
- what evidence would change the decision.
