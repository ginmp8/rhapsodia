# Review Scenarios

## Scenario 1: Activation text hides the real trigger

**Observed package**

- Frontmatter says the skill "helps with documents".
- The body supports only legal memorandum review.
- Non-activation cases are absent.

**Calibrated result**

- 🟠 `MAJOR`, confirmed activation defect.
- Impact: broad false positives and missing common legal-review terms.
- Smallest fix: narrow the description to legal memorandum artifacts and add adjacent document exclusions.
- Do not recommend a package redesign unless other evidence shows mixed ownership.

## Scenario 2: Unreferenced example file

**Observed package**

- `examples/legacy-output.md` is not linked from `SKILL.md`.
- No script consumes it.
- Its content may still be intentionally retained for maintainers.

**Calibrated result**

- Start as 🟣 `QUESTION`, not a confirmed orphan defect.
- Confirm whether it is intentionally retained or stale.
- Upgrade to 🟡 `MINOR` only when its stale instructions can mislead maintenance or packaging.

## Scenario 3: Validator proves less than the report claims

**Observed package**

- A script validates JSON schema and file existence.
- The skill claims 100% activation accuracy and production readiness.
- No live or supplied behavioral evaluation exists.

**Calibrated result**

- 🟠 `MAJOR`, confirmed evidence-discipline defect.
- The validator may remain useful; the defect is the unsupported claim.
- Smallest fix: relabel results as structural coverage and add planned or executed behavioral evaluation before metrics.

## Scenario 4: Large but cohesive skill

**Observed package**

- `SKILL.md` is long but owns one regulated workflow.
- Modes share inputs, vocabulary, validators, outputs, and owner.
- Detailed tables are already in references.

**Calibrated result**

- Do not penalize size alone.
- Record a token-efficiency finding only when duplication, branch pollution, or context competition has evidence.

## Scenario 5: Security request

**User request**

"Audit this skill for exposed secrets and unsafe shell commands."

**Calibrated result**

- Do not activate this skill as the primary reviewer.
- Route to a dedicated security-and-governance or secure-code-review skill.
- This skill may later validate the quality of that review report, but it does not own the security judgment.


## Scenario 6: Current path always enters the legacy workflow

**Observed package**

- The current mode unconditionally loads `references/legacy-workflow.md`.
- The legacy branch decides validation order and output sections.
- No legacy format or consumer is detected before that branch runs.

**Calibrated result**

- 🟠 `MAJOR`, confirmed `contradictory` legacy classification: the current path is governed by replaced behavior.
- Smallest fix: make the current workflow canonical and invoke a boundary adapter only after explicit legacy detection.
- Validation: prove the current path passes with the legacy reference removed from its load path, then test one evidenced legacy input separately.

## Scenario 7: Isolated adapter with an active consumer

**Observed package**

- A supplied external workflow still sends the previous identifier format.
- Ingress detects the old format, converts it once to the canonical model, and uses the current workflow afterward.
- Separate scenarios cover current input, legacy input, and unknown input rejection.

**Calibrated result**

- Classify as `migration-only`; do not create a defect when every migration isolation gate passes.
- Record it as a positive signal when the consumer, adapter boundary, and tests are evidenced.

## Scenario 8: Silent fallback masks malformed current input

**Observed package**

- Absence of a current version field selects the old parser.
- Invalid current input therefore succeeds under legacy defaults.
- The output differs from the declared current contract without a warning.

**Calibrated result**

- 🟠 `MAJOR`, confirmed `contradictory` compatibility behavior because malformed current input is accepted by an old contract.
- Smallest fix: require explicit legacy detection; reject or ask for clarification on unknown/malformed current input.
- Validation: malformed current input must not execute the legacy branch.

## Scenario 9: Old and current validators are competing sources of truth

**Observed package**

- The current template requires a new section.
- The packaged validator still rejects that section and expects the old shape.
- Instructions tell maintainers to satisfy both.

**Calibrated result**

- 🔴 `BLOCKER` when no deterministic output can satisfy both contracts; otherwise 🟠 `MAJOR`.
- Classify as `contradictory`; identify the canonical current schema and remove or isolate the replaced validator.
- Select one canonical schema and update the adapter or validator around it.

## Scenario 10: Locally unreferenced alias with unknown external consumers

**Observed package**

- An old command alias is not referenced inside the package.
- No repository, usage log, migration note, or consumer inventory is supplied.

**Calibrated result**

- 🟣 `QUESTION`, `blocked` classification until external-consumer evidence resolves removal safety.
- Do not mandate deletion. Request the smallest evidence that can prove active use or safe removal.

## Scenario 6: Keyword match is not a legacy finding

**Observed package**

- A factual changelog says a field was "previously named priority".
- The current schema, validators, templates, and examples use only the new field.
- No normal-path reader accepts the old field.

**Calibrated result**

- Classify the changelog sentence as `current` historical fact or bounded `noise` depending on length and relevance.
- Do not report obsolete compatibility solely because the word `previously` exists.
- Verify that the changelog is not the only source of a current rule.

## Scenario 7: Current validator silently accepts an old handoff

**Observed package**

- The normal validator tries schema v2.
- On failure, it invokes a v1 parser and builds a partial v2 envelope.
- The migration behavior has no separate mode or rejection tests.

**Calibrated result**

- 🟠 `MAJOR`, confirmed compatibility defect.
- Legacy classification: `obsolete` when v1 support ended, otherwise `blocked` until support commitment is known.
- Smallest fix: reject v1 in the normal path and place any still-supported adapter behind an explicit migration mode.
- Validation: current v2 positive test, normal-path v1 rejection test, and isolated migration test if retained.

## Scenario 8: Migration-only behavior is valid

**Observed package**

- A command named `adapt-v1-to-v2` requires explicit legacy input.
- Normal execution rejects v1.
- The adapter emits a complete v2 artifact before handoff, reports unmapped fields, and has positive and negative tests.

**Calibrated result**

- Classification: `migration-only`.
- Do not recommend removal merely because v1 code exists.
- Record the migration owner and removal condition when available.

## Scenario 9: Runtime coupling between peer skills

**Observed package**

- One skill imports a validator from a sibling skill directory using an absolute `/home/oai/skills/...` path.
- Local execution fails when the sibling is not installed.
- The shared contract has no package-independent canonical representation.

**Calibrated result**

- 🟠 `MAJOR`, confirmed runtime-coupling and architecture defect.
- Legacy classification: `contradictory` when package independence is part of the current contract.
- Smallest fix: package the shared schema or equivalent validator locally and verify byte or semantic equivalence in integration tests.

## Scenario 10: Generic priority transfers authority

**Observed package**

- A planning skill writes `priority: high`.
- A governance skill owns `business_priority` and a technical skill owns `technical_criticality` and `execution_sequence`.
- A fallback reads `business_priority ?? priority`.

**Calibrated result**

- 🟠 `MAJOR`, confirmed ownership and compatibility defect.
- Legacy classification: `obsolete` for the generic alias and `contradictory` for the cross-domain fallback.
- Require explicit rejection of `priority` and owner-specific positive tests.

## Scenario 11: Changelog is a second operational manual

**Observed package**

- The only complete current handoff contract is inside `CHANGELOG.md`.
- A keyword validator passes because required phrases exist there.
- Current references contain no equivalent schema or normative rule.

**Calibrated result**

- 🟠 `MAJOR`, confirmed consistency and fragile-validation defect.
- Classification: `contradictory` for current authority placement and `noise` for duplicated historical detail after consolidation.
- Move the current contract to a canonical operational source, keep only a factual changelog entry, and replace the keyword gate.

## Scenario 12: Old-named script with a current consumer

**Observed package**

- `validate_v1.py` is invoked by the current package builder.
- The name is historical, but the script validates the only current schema.

**Calibrated result**

- Start as 🟣 `QUESTION`, not an orphan or obsolete finding.
- Classification may be `current` with a naming `NIT`, or `contradictory` if its behavior still implements v1 semantics.
- Inspect imports, CLI behavior, tests, and schema before recommending rename or removal.
