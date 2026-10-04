# Evolution Architecture

**Contract version:** 1.0.0

Use for `evolution-architecture-review` and whenever a structural decision depends on how the package absorbs future change. This is a lightweight scenario method inspired by architecture tradeoff analysis; it is not a mandatory full ATAM ceremony.

## Quality/change scenarios

Use a small number of scenarios that can change the architecture decision. A useful scenario states:

- `id`;
- stimulus/change, such as adding a mode, host, validator, policy, or adjacent skill;
- affected resources/owners/activation surfaces;
- expected change radius;
- context/loading impact;
- validation/evidence impact;
- authority/trust impact when material;
- evidence IDs.

Prefer realistic likely changes over hypothetical catalogues of every possible future.

## Sensitivity and tradeoff points

A **sensitivity point** is an architectural choice where a small change materially affects a quality attribute, such as activation clarity, context cost, validation independence, or ownership isolation.

A **tradeoff point** is a choice that improves one quality while worsening another, for example:

- extracting a mode reduces local context but increases composition/activation overhead;
- centralizing a rule reduces drift but broadens change radius;
- adding a router simplifies entry but creates another dispatch surface that must stay narrow.

Record only points supported by observations. Do not invent tradeoffs to make a report look complete.

## Change isolation

Use current structure first:

- which decision/rule is likely to change;
- which files/resources/validators must move with it;
- whether edits cross ownership or evidence boundaries;
- whether the same semantic change must be repeated in several locations;
- whether the package contains stable seams that confine the change.

Large change radius is evidence only when tied to a concrete scenario or repeated observed change pattern.

## Optional change-coupling evidence

When trustworthy repository history is available, change coupling can corroborate hidden evolution relationships. Record:

- exact repository/revision/time range;
- files/resources that repeatedly changed together;
- reason/issue/commit grouping when available;
- obvious mass-format, vendoring, rename, release, or migration events that can create false co-change signals;
- whether static dependency/consumer evidence corroborates the relationship.

**Change coupling is corroborating evidence, not a structural decision rule.** Never recommend split, merge, extraction, routing, deletion, or ownership transfer from co-change frequency alone.

If history is unavailable or unsuitable, record `history_status: not-inspected` or `unknown`; do not penalize the package merely for missing VCS history.

## Decision use

Use scenario/sensitivity/tradeoff evidence to test whether an otherwise eligible decision remains sensible under realistic change. Preserve the rubric's minimum evidence and tie-breakers. When two architectures remain valid, prefer the smallest change that resolves the evidenced present and evolution risk.
