# Reproducibility and evidence contract

Use this reference to keep repeated frontend reviews/plans materially comparable without pretending that architecture, UX, or code-review judgment is byte-deterministic.

## Evidence labels

Use the strongest label actually supported:

| label | meaning |
|---|---|
| `measured` | command, test, scanner, browser check, or deterministic calculation executed in the current run |
| `observed` | directly read from inspected files, diff, screenshots, traces, logs, or supplied runtime output |
| `supplied` | user/tool supplied a result that was not independently rerun here |
| `inferred` | conclusion derived from partial evidence or established patterns |
| `assumed` | unverified premise needed to proceed |
| `planned` | validation/change proposed but not executed |
| `blocked` | required evidence/action could not be obtained |

Do not upgrade `observed`, `supplied`, `inferred`, `assumed`, or `planned` to `measured` for presentation.

## Context identity and source snapshot

For repo-dependent conclusions, record enough identity to make the analysis reproducible when practical. When the scanner is used, its `input_identity.sha256` is the exact hash of the eligible source bytes it analyzed, in stable relative-path order. Treat that hash as a source snapshot identity, not as proof of correctness.

Record when practical:

- repository/worktree or supplied file set;
- branch/commit when known and material;
- target feature/diff/paths;
- framework/tool versions when they affect the recommendation;
- inspected files/contracts/tests;
- material dependencies that were not inspected.

Do not claim "the repository uses X everywhere" from a local sample unless that broader claim was actually checked.

## Context-budget rules

Start narrow and expand only on evidence.

### Initial set

Prefer:

1. target/changed file;
2. nearest feature README or local instructions;
3. imported API/schema/type boundary needed to understand the change;
4. nearest relevant test;
5. design-system primitive only when UI semantics depend on it.

### Expansion triggers

Expand when one of these is observed:

- unresolved import or symbol ownership;
- contract defined outside the current feature;
- shared abstraction whose ownership/safety is material;
- cross-feature behavior;
- route/provider/config behavior;
- authentication/authorization/security boundary;
- failing typecheck/test/runtime evidence;
- design-system behavior that cannot be inferred safely from the usage site.

Do not expand merely because more files exist.

## Stable finding contract

For architecture, code, security, and UX findings, use these fields conceptually even when rendering prose:

```text
severity
code/category
subject/location
evidence_label
evidence
impact
smallest_fix
validation
```

Severity definitions come from `output-contracts.md`. A severity must reflect the failure impact, not the amount of code required to fix it.

When two findings share the same root cause, prefer one causal finding with affected subjects rather than duplicated symptoms.

## Deterministic ordering

Unless the user requests another order:

1. blocking/critical security or correctness;
2. high severity;
3. medium severity;
4. low severity;
5. within one severity: dependency/root-cause order, then stable path/name order when ties remain.

For implementation plans, order by prerequisite and dependency rather than by visual convenience.

## Repair loop

Use:

`diagnostic -> smallest causal fix -> same gate -> adjacent gates`

Avoid broad refactors while a focused gate is failing. If two consecutive repair rounds do not reduce the same objective failure set, stop that repair branch and report the unresolved evidence instead of trying unrelated changes.

Do not fix a UI failure by hiding required content, weakening accessibility, lowering a test expectation, suppressing an error, or moving security responsibility into the frontend.

## Comparison discipline

For before/after claims:

- use the same target files/diff and relevant runtime environment;
- keep the acceptance criteria unchanged;
- separate code/static validation from browser/runtime validation;
- separate runtime validation from subjective visual/UX approval;
- do not call a static checklist score a behavioral improvement.

If the evidence changed between baseline and candidate, state that the comparison is not clean rather than implying equivalence.

## Validation layers

Treat these as independent:

1. **structural/static**: imports, types, schemas, lint, scanner output, architecture rules;
2. **test/build**: unit/component/integration/build/typecheck commands;
3. **runtime/browser**: actual route, interaction, network, console, focus, responsive state;
4. **perceptual/editorial**: visual polish, UX preference, wording, hierarchy, CRO hypothesis.

Passing one layer does not imply the next.

## Final freeze

Once the response or proposed patch has passed the applicable final checks, treat that version as frozen. A later material edit requires rerunning the checks affected by that edit.

For delivered scanner reports or generated guidance, do not claim a report corresponds to a code state if the inspected files changed afterward.

## Scanner receipt and delivery integrity

The JSON scanner output is a stage-aware machine-readable receipt. It includes:

- `receipt_version`;
- `stage`;
- scanner/schema version;
- target;
- exact input identity for scanned bytes;
- stable finding codes/severities/subjects;
- severity counts;
- explicit limitations.

When `--output` is used, the scanner writes via a temporary sibling and atomic replacement. If the report is placed inside the scanned root, that output path is excluded from the input identity so repeated runs do not hash the previous report as source code. Existing symbolic-link outputs are rejected before write to avoid alias ambiguity.

Do not edit a scanner receipt after generation and still present it as evidence for the original input identity.

## Freeze after pass

After the applicable final validation passes, freeze the result. Do not make cleanup/cosmetic edits afterward without rerunning the affected checks. A scanner receipt, runtime trace, or review tied to one source identity must not be presented as current evidence after the relevant source changed.
