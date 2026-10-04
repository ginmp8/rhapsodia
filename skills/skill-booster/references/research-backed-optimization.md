# Research-Backed Optimization

Use this branch only when research evidence materially determines what the target skill should gain, remove, or change. It must remain optional: Skill Booster works without a research skill or a web capability.

## Contract

1. Freeze or otherwise identify the bounded research corpus before deriving target changes.
2. Extract atomic findings with stable ids and give every finding one terminal disposition: `implement`, `already-covered`, `rejected`, `not-applicable`, `uncertain`, or `conflict`.
3. Translate accepted findings into testable requirements; do not paste research prose into `SKILL.md` when a smaller operational rule is sufficient.
4. Define deciding evaluations before candidate mutation when feasible and preserve pre-existing evaluator assets unchanged.
5. Require every substantive change to trace backward to one or more requirements and every accepted requirement to implementation plus evaluation.
6. Validate bidirectional references and finding accounting mechanically when a traceability validator is available; otherwise perform the same accounting and label it checklist-only.
7. Review semantic fidelity separately from structural trace completeness. A 100% matrix proves coverage of the recorded corpus, not completeness of all relevant knowledge.
8. Freeze the passing candidate and research/evaluator identities. Any later candidate edit reopens affected validation.

`research-traceability` is the preferred specialist when installed, but the portable Booster core must not require its private invocation API or package path.
