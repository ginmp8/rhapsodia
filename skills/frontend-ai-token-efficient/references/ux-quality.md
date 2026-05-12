# UX quality tied to frontend implementation

Use this reference when UX, CRO, visual quality, onboarding, forms, empty states, or friction are connected to frontend code, design-system usage, accessibility, analytics, or runtime validation.

This reference should not turn the skill into a pure creative design generator. In existing products, project consistency and user task clarity matter more than novelty.

## Existing project: preserve the product language

Before proposing UI changes, inspect or ask for:

- the design system and component library;
- color, spacing, typography, radius, shadow, and motion tokens;
- layout, grid, breakpoint, and responsive patterns;
- similar components already used by another feature;
- existing loading, empty, error, disabled, success, and permission-denied states.

Preserve the established visual language. Do not introduce a new font, palette, animation style, or library just to make a screen look different.

## New interface without a design system

When there is no design system or the task is a new interface, define before coding:

1. purpose: problem, user, and primary task;
2. tone: utilitarian, editorial, institutional, premium, minimal, dense, technical, playful, or another product-fit direction;
3. constraints: framework, accessibility, performance, responsiveness, and sensitive data;
4. signature element: what makes the screen recognizable without hurting usability.

Use explicit tokens for color, spacing, radius, typography, and motion. Avoid generic generated UI patterns: context-free card grids, default gradient hero sections, vague microcopy, unmotivated decorative animation, and visual choices unrelated to the product task.

## Visual intensity by context

| context | preferred intensity |
|---|---|
| backoffice, dashboard, regulatory flow, registration | refined precision, clear hierarchy, low distraction |
| landing page or public product | more expressive identity without sacrificing performance or accessibility |
| onboarding or first use | guidance, progression, and quick wins |
| critical screen with sensitive data | sobriety, trust, explicit feedback, and minimal noise |

## Forms and friction

For each field, ask:

- Is it required before the user receives value?
- Can it be inferred, enriched, or requested later?
- Is there a legal, compliance, or risk requirement to collect it now?
- Is the information actually used by the follow-up flow or backend process?

Good practices:

- one topic per field;
- visible labels, with placeholders used as examples only;
- easier fields first; sensitive or difficult fields later;
- clear masks and normalization for phone, document, currency, and date fields;
- correct mobile keyboard type: `email`, `tel`, `numeric`, and related input hints;
- one-column layout by default; multiple columns only for short, related fields;
- multi-step flow when there are many sections, with progress, back navigation, and preserved data;
- specific errors close to the field, without clearing user input;
- on submit, focus the first error and preserve data;
- CTA copy that states the action or outcome, not only `Submit` when the result is meaningful;
- trust microcopy near sensitive fields without promising privacy the product cannot guarantee.

## Onboarding, activation, and first use

Before designing onboarding, identify:

- the `aha moment` or activation event;
- the shortest path to first value;
- where users abandon today;
- whether setup is required before value is visible;
- which steps are required, optional, or deferrable.

Principles:

- reduce time to value;
- one main goal per session;
- let the user perform the real task instead of only watching a tutorial;
- empty states should explain value, show an example or preview, and offer one primary action;
- checklists should have 3-7 items, start with quick wins, show progress, and allow dismissal;
- tours should be short, point to real UI, be dismissible, and not repeat for returning users;
- progress indicators should not block core value without a strong reason.

## Metrics and experiments

When the decision involves conversion, activation, or friction, propose a testable hypothesis rather than certainty.

Useful metrics:

- form start rate, completion rate, field drop-off, error rate, and time-to-complete;
- activation rate, time-to-activation, onboarding completion, and feature adoption;
- CTA click-through, dismiss rate, retry rate, task success, mobile versus desktop.

Hypothesis format:

```txt
if we reduce [friction] for [segment], we expect [metric] to improve because [mechanism]. validate with [test/evidence].
```

## Visual accessibility and interaction

Do not treat aesthetics as a substitute for accessibility:

- sufficient contrast;
- visible focus;
- adequate touch targets;
- keyboard navigation;
- screen reader behavior for modals, errors, and dynamic states;
- reduced-motion behavior when relevant;
- important information not communicated by color alone.

## UX review output

For a UX review, respond with:

1. flow objective;
2. findings by impact;
3. smallest recommended adjustment;
4. associated hypothesis or metric;
5. required validation: user test, analytics, Playwright, screenshot, or manual review.
