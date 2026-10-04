# Artifact Profiles

Profiles provide conservative starting rubrics. They do **not** create hidden acceptance criteria. Resolve selected criteria into `request.rubric.criteria` and freeze them with the request.

## `ui`

Use for screenshots and rendered UI states.

Typical criteria: content presence, structure/grouping, layout, alignment, spacing, typography, hierarchy, component shape. Add interaction-state semantics to intended/capture state; do not use the perceptual result to prove interactions actually work.

Material capture facts often include viewport, theme, locale, fixture/data snapshot, zoom/device scale, font availability, expanded/collapsed state, and loading/error/success state.

## `document-page-slide`

Use for PDF pages, report renders, documents, and slides.

Typical criteria: content presence, page/slide structure, layout, alignment, spacing, typography, hierarchy, and overflow/cutoff visibility. Page count or text correctness may need separate deterministic content checks when exactness matters.

## `chart`

Use for statistical/data visualizations.

Typical criteria: content presence, chart structure, chart encoding, labels/legend, relative geometry, hierarchy, and readable typography. Explicitly review the semantic encoding that matters: axis/scale, series mapping, ordering, direction, legend association, labels, or annotations.

Do not infer data correctness from visual resemblance alone; use data/query assertions when underlying values must be proven.

## `diagram`

Use for architecture, flow, sequence, relationship, process, or other node/edge diagrams.

Typical criteria: entity/content presence, structure, layout, and **diagram relations**. Relation correctness is distinct from recognizing the right entities; name the relation or path in criterion evidence when it matters.

## `general-image`

Use for images that do not fit the semantic UI/document/chart/diagram profiles.

Choose only the observable properties relevant to the task. Avoid generic “looks similar” criteria when the user can specify shape, placement, content, color, texture, or hierarchy separately.

## `custom`

Use when none of the standard profiles fit. A custom profile must still resolve to explicit rubric criteria, scope, gate policy, and evaluator protocol before review.

## Profile selection rules

1. Select the narrowest profile matching the artifact's semantics.
2. Remove irrelevant default criteria before freeze; do not evaluate noise.
3. Add domain-specific criteria only when the acceptance requirement actually needs them.
4. Keep deterministic behavior/data correctness outside this perceptual gate.
5. If two artifact classes materially coexist (for example a chart inside a UI), keep one primary profile and add explicit cross-profile criteria rather than silently running two different policies.
