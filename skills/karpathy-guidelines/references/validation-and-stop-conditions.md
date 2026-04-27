# Validation and Stop Conditions

Use this reference when verification is incomplete, scope is unsafe, inputs are missing, or the requested change risks becoming broader than the evidence supports.

## Verification ladder

Prefer the strongest feasible check, in this order:

1. targeted failing test reproduced and fixed;
2. existing relevant test suite;
3. build, type, or lint check;
4. local runtime smoke test;
5. static reasoning with exact files, functions, or configuration keys named.

When none can be run, label verification as not executed and identify the best next check.

## Scope control

Before changing or recommending changes, confirm that each edit is traceable to the user's request. Do not:

- reformat unrelated code;
- rename unrelated symbols;
- replace frameworks or libraries for a local fix;
- add defensive configurability without a current use;
- remove pre-existing dead code unless requested;
- patch unrelated issues discovered during review.

Mention unrelated observations separately when they materially affect risk.

## Unsafe or under-specified requests

Stop, narrow, or ask for the missing blocker only when continuing would risk a wrong answer. Common blockers:

- no code, error, diff, or artifact is available for a concrete fix;
- the requested behavior has materially different valid interpretations;
- verification would require unavailable credentials, systems, data, or tools;
- the task asks for security, performance, or reliability conclusions without evidence;
- the user requests blanket changes such as "handle every error" or "rewrite everything" without a bounded slice.

When the blocker is not fatal, proceed with a stated assumption and keep the change small.

## Validation reporting

Report validation in two groups:

- executed checks with command names and outcomes;
- not executed checks with the reason they were skipped or unavailable.

If a command fails, preserve the failure as evidence. Do not replace it with a weaker passing check unless you also explain what the weaker check does and does not prove.

## Security-sensitive handling

If code or logs include credentials, tokens, keys, connection strings, or other secrets:

- do not repeat the sensitive value;
- flag the exposure as a finding;
- recommend rotation when exposure is plausible;
- suggest moving the value to an approved secret store or environment mechanism;
- avoid writing sample code that hardcodes the sensitive value.
