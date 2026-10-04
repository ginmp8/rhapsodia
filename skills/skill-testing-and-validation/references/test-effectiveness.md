# Test intent, oracle provenance, and effectiveness

Use this reference for test generation, test-suite assessment, and claims about whether tests can detect incorrect behavior.

## Three distinct questions

Keep these evidence dimensions separate:

1. **Execution:** did the selected gate execute and pass?
2. **Reliability:** does comparable execution remain stable?
3. **Effectiveness/oracle:** would the test fail when the required behavior is wrong?

A passing, stable suite can still have a weak oracle or miss required behavior.

## Test intent

Before generating or materially evaluating tests, record the primary intent. Use the narrowest applicable value or explicit equivalent:

- `regression-characterization`: preserve behavior already established as correct;
- `bug-finding`: expose behavior suspected to be wrong;
- `contract`: prove an interface/message/schema agreement;
- `property`: prove an invariant, relation, or state-model property;
- `security`: exercise an explicitly scoped security property;
- `compatibility`: prove supported-version/platform behavior.

Intent changes what counts as a valid oracle. Do not silently treat characterization as bug finding.

## Oracle source

Record where expected behavior comes from. Prefer independent sources when correctness is disputed:

- requirement/specification;
- API/schema/message contract;
- trusted reference implementation;
- previously validated correct baseline;
- metamorphic relation/invariant;
- independent domain/model evidence;
- human/domain judgment with explicit rationale;
- SUT observation only.

For `bug-finding`, observation of the suspected faulty SUT is not sufficient by itself to define the expected result. If no independent oracle can be established, mark the test design `blocked`, `uncertain`, or `planned` rather than encoding the current output as truth.

When deriving a trustworthy oracle is itself the hard problem, route that bounded work to a dedicated test-oracle workflow when available instead of expanding this skill into oracle engineering.

## Behavioral coverage before proxy metrics

When requirements, contracts, states, invariants, or known failure classes exist, map them to tests/evaluations explicitly. Report uncovered behaviors even if structural coverage is high.

Coverage, mutation score, and similar measurements are **proxy metrics**. They may expose gaps, but they are not proof of correctness or sufficient acceptance evidence by themselves.

Rules:

- never infer correctness from line/branch coverage alone;
- use mutation analysis only with a green baseline and record tool/operator configuration when the score matters;
- do not compare mutation scores as if all operator sets were equivalent;
- do not use mutation/coverage to validate a bug-finding oracle derived only from a possibly faulty implementation;
- keep proxy metrics secondary to explicit behavior/oracle evidence.

## Generated-test evidence

Generated-but-unexecuted tests remain `planned`. Generated-and-passing tests prove only what their oracle and behavioral mapping actually cover. Preserve the source of each material expected outcome when the source is not obvious from the test itself.
