# Evaluation Suite Health

Evaluation suites need maintenance as capabilities and failure distributions change.

- Distinguish capability/quality suites from regression suites. A capability suite near saturation stops providing useful optimization signal; graduate stable cases to regression and add harder, representative capability cases.
- Keep positive and negative routing cases balanced enough to detect both under-triggering and over-triggering.
- For hard behavioral gates, prefer a known-good reference solution, expert-validated expected outcome, or equivalent oracle probe that demonstrates the task/grade contract is solvable. If none exists, record the limitation explicitly.
- Sample traces/transcripts from passes and failures to verify graders are fair; a passing aggregate score can hide grader loopholes and a failing score can reflect a broken task.
- Grow regression/adversarial coverage from confirmed real failures. Do not tune holdout cases into the same candidate lineage and still call them unseen.
- Outcome correctness normally outranks exact trajectory conformance. Gate an exact path only when the path itself is a safety/authority/protocol requirement.
