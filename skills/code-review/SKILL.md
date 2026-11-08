---
name: code-review
description: "Review a frozen code diff against documented repository standards and original requirements in two independently reported axes. Use for PR/branch/diff review; not for implementing fixes, approving/merging changes or replacing the deeper Audit Spec Implementation coordinator."
---

# Code Review

## Mission and boundaries

Review a fixed Git diff in **two separate axes**: (1) Standards: documented coding standards and cautious maintainability observations; (2) Spec: changes against the original requirement/issue. Preserve the split; neither axis substitutes for the other's evidence.

Use for ordinary PR and branch reviews. For exhaustive requirement-to-reachable-behavior and test-oracle coverage use **audit-spec-implementation**; its coordinator may delegate the Spec axis to this skill, but must avoid duplicated evidence or unsupported independent-agent claims. **Magia** owns execution of authorized fixes. A review never authorizes approval or merge.

## Quick start

1. Resolve repository, immutable base and candidate HEAD commits, requested scope and optional spec/issue identity. Reject missing or stale refs and empty diffs.
2. Read repo standards, including `CODING_STANDARDS.md` and `CONTRIBUTING.md` where present; identify changed files, existing checks and the original requirement text. Do not invent missing specs.
3. Freeze one `git diff BASE...HEAD` view (merge-base semantics) and relevant commit list. If direct Git is unavailable, use an equivalent source-linked comparison and label its limits.
4. Execute Standards and Spec reviews with **fresh independent context** where the host truly supports parallel subagents. Otherwise run sequentially with clearly separated evidence and disclose that no independent subagents ran.
5. Standards: report enforceable violations with cited rule/hunk and cautious maintainability observations. Do not flag lint-enforced style as a fresh expert finding. Use [smell baseline](references/smell-baseline.md) for subjective patterns, subordinated to documented repo conventions.
6. Spec: trace user requirements to changed behavior, identify missing/partial implementation, unrequested scope and potentially incorrect behavior. If no normative source exists, label Spec `unverified` instead of inventing acceptance criteria.
7. Present **Standards** and **Spec** sections separately, including strongest material finding and source locations per axis. A reported issue requires a reproducible trigger or code hunk, effect, severity and verification/fix direction. Do not average or rerank both axes into a single verdict.

## Invariants

- Preserve original requirement meaning, branch identities and evidence freshness; verify candidate HEAD again before concluding.
- A code hunk, test name or CI green status alone is not proof of runtime behavior. State unrun checks.
- Do not copy sensitive code into public comments or external tools without authorization. Do not post, approve, merge, push, or rewrite the issue/spec.
- No automatic single reviewer substitutes for independent verification or gives two axes the false appearance of two agents.
- Keep explicit source pointers and note where a stricter RhapsodIA specialist should be invoked.

## Host portability

Git and independent subagents are optional. Without Git, use a supplied or authorized connector-provided diff pinned to exact refs; disclose when those identities cannot be verified. If no reliable diff exists, provide a scoped review checklist rather than a code verdict. A single context must never be presented as independent parallel review.

## Output contract and stop conditions

Report the fixed-point comparison and separate Standards and Spec findings, each with severity, source location, consequence, corrective direction and test/evidence limitations. Stop without a complete verdict when the diff or normative requirements are unavailable; never approve or merge a PR.
