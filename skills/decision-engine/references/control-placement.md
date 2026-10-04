# Control Placement

Use the lowest reliable control layer.

| Decision class | Preferred control | Use Decision Engine? |
|---|---|---|
| Mechanical | script, schema, type, validator | only to report/route around the mechanical result, not to replace it |
| Constrained heuristic | explicit defaults, tie-breakers, limits | yes when semantic context still matters |
| Judgment | rubric, evidence, criteria | yes when the decision is bounded |
| Subjective | independent evaluation or explicit preference | only if the caller intentionally converts it into a bounded decision |

Examples:

- `Is this YAML syntactically valid?` -> parser/validator, not Binary judgment.
- `Does this change semantically weaken activation?` -> Binary can be appropriate with evidence/rubric.
- `Which of these three workflows fits the evidence?` -> Choice with explicit exhaustiveness.
- `How severe is this bounded risk on three described levels?` -> ordinal Score.
- `What is this bounded measured value from 0 to 100?` -> numeric Score.
- `Write the best architecture proposal` -> open-ended analysis first; optionally use Choice later to select among explicit proposals.

Do not turn every model judgment into this skill. Structured decisions are useful at boundaries, routers, gates, and explicit selection points.

Keep operational policy at its lowest reliable layer too. If a threshold, weight, permission, or approval rule is deterministic caller policy, apply it in policy/code rather than asking the Decision Engine to invent or reinterpret it.
