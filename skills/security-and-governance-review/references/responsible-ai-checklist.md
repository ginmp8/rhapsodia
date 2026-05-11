# Responsible AI Checklist

Use this checklist for `responsible-ai-review`. Keep the review domain-specific and evidence-based.

## Domain framing

Before listing risks, identify:

- What automated decision, recommendation, classification, generation, moderation, or action the system performs.
- Who is affected directly and indirectly.
- Whether the system handles personal data, sensitive attributes, financial data, employment data, health data, children, accessibility needs, or regulated decisions.
- Whether the user can understand, contest, opt out, or reach a human.
- Whether failures create denial of service, exclusion, surveillance, economic harm, safety harm, reputational harm, or legal exposure.

## Fairness and bias

Inspect for:

- Unequal outcomes for equivalent inputs across names, languages, regions, age ranges, disabilities, dialects, or cultural conventions.
- Missing test cases for accents, non-Latin characters, long names, hyphenated names, apostrophes, empty values, and assistive-technology workflows.
- Proxies for protected or sensitive attributes.
- Explanations that are unavailable for consequential decisions.

## Accessibility and inclusion

Inspect for:

- Keyboard and screen-reader usability in user-facing flows.
- Alt text, labels, error messages, focus order, contrast, zoom behavior, and color-independent status indicators.
- Alternatives for users who cannot use the primary automated flow.
- Language localization and support for non-English characters where relevant.

## Privacy and consent

Inspect for:

- Data minimization and clear purpose limitation.
- Consent separation for essential versus optional use.
- Retention and deletion rules.
- Sensitive data in prompts, logs, analytics, training data, examples, or reports.
- Ability to opt out of non-essential profiling or automation when appropriate.

## Automation safety

Inspect for:

- Human override for high-impact decisions.
- Confidence thresholds and abstention behavior.
- Fail-safe behavior when model output is uncertain, incomplete, or inconsistent.
- Monitoring for drift, abuse, and disparate impact.
- Clear escalation when legal, ethical, or domain tradeoffs are unresolved.

## Reporting rule

Do not produce a generic responsible-ai checklist as the final answer. Map every responsible-ai finding to a real domain risk, affected user group, evidence, mitigation, and validation probe. If the domain is unknown, report an evidence limitation and ask for domain context only if required to proceed.
