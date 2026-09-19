# Security Review Rubric — SGR-2.0

`rubric_version: SGR-2.0`

Use this versioned rubric for every finding, report, and comparison. Do not silently mix classifications from older reports with SGR-2.0. Legacy labels such as `confirmed risk`, `potential risk`, and `evidence limitation` may be interpreted as historical input, but new output uses the canonical classifications below.

## Canonical finding classifications

- `confirmed`: direct evidence establishes the unsafe condition or missing control being claimed. This does **not** by itself prove exploitability, concrete exposure, CVE applicability, or real-world harm unless the evidence establishes that too.
- `suspicious-pattern`: a concrete pattern warrants review, but authenticity, reachability, exploitability, runtime state, or policy context is incomplete.
- `governance-risk`: evidence shows an authority, policy, approval, audit, fallback, or human-oversight weakness. This classification is for governance/control risk, not a software vulnerability claim.
- `needs-verification`: the requested conclusion depends on evidence that is missing, stale, blocked, or not independently verified. Critical missing evidence is fail-closed and must not be converted into a positive assurance claim.
- `not-applicable`: the criterion is demonstrably outside the target/mode. State the reason; do not use this to hide an uninspected surface.

## Evidence sufficiency

A finding should map:

`finding -> evidence -> risk -> recommendation -> validation`

Evidence should identify the exact source and identity when possible: file/line, file SHA-256, manifest/lockfile identity, scanner result identity, advisory/source identity, policy version, or user-supplied evidence reference. Sensitive evidence must be masked or represented by a non-reversible description/fingerprint that does not reveal the full secret.

Never promote `suspicious-pattern` or `needs-verification` to `confirmed` based only on variable names, filenames, keywords, severity intuition, or repeated model agreement.

## Stable severity criteria

Severity and confidence are independent. Apply the highest criterion fully supported by the evidence; when two levels fit equally, choose the lower severity unless a concrete impact/authority fact justifies the higher one.

- `critical`: evidence supports a direct path to severe compromise or harm with high-impact authority/blast radius, such as exposed live privileged credentials, arbitrary code execution in a reachable privileged path, destructive unaudited authority over critical resources, or unsafe autonomous action capable of severe financial/legal/safety/data harm.
- `high`: evidence supports a serious control failure or exploitable condition with substantial impact, but one material precondition or blast-radius constraint separates it from critical.
- `medium`: meaningful weakness requiring additional conditions, narrower authority, or limited blast radius; includes missing approval/audit controls, traversal/injection primitives not proven reachable, or policy gaps with plausible misuse.
- `low`: hygiene, defense-in-depth, documentation, sample safety, or validation weakness with limited direct impact.
- `informational`: source identity, context, not-applicable result, or evidence limitation without a risk claim.

### Severity tie-breakers

Apply in this order:

1. concrete impact demonstrated;
2. reachable authority/privilege demonstrated;
3. blast radius demonstrated;
4. exploitability/misuse path demonstrated;
5. otherwise select the lower applicable severity and state the missing evidence.

A `needs-verification` item can be high/critical only when the **missing evidence itself** is a high-impact assurance gate (for example, inability to verify authorization for destructive production actions). It must not imply that the underlying vulnerability is confirmed.

## Confidence

- `high`: exact target evidence, deterministic local scan, signed/scanner output, manifest/lock identity, current authoritative source, or supplied runtime evidence directly supports the claim.
- `medium`: strong pattern or structural evidence exists, but exploitability, environment, policy, current status, or runtime behavior is incomplete.
- `low`: weak indicators, inferred context, or indirect evidence only.

## External vulnerability/CVE claims

Do not claim a CVE is applicable, exploitable, or exposes the target unless evidence includes enough identity to bind the claim to the target, typically:

- dependency/package name and resolved version;
- ecosystem/source identity or lockfile/manifest identity;
- scanner result or authoritative advisory/current primary source;
- applicability context when the advisory is conditional.

If current vulnerability evidence is unavailable or cannot be tied to the resolved dependency, use `needs-verification` and record the evidence gap. Never convert stale advisory knowledge into a current confirmed finding.

## Governance and authority criteria

For authority-capable agents/workflows, identify at least:

- action: read | write | execute | delete | send | publish | schedule | deploy | approve | delegate;
- target/resource scope;
- authorization source;
- approval requirement;
- audit/receipt requirement;
- failure behavior when authorization is ambiguous;
- rollback/containment where applicable.

Missing or ambiguous authorization for a high-impact action is fail-closed: do not infer permission from capability.

## Critical review gates

A review is not `complete` unless all applicable gates hold:

1. target/mode and evidence snapshot identity are stated;
2. protected secret material is never printed in full;
3. all findings use SGR-2.0 classifications/severity/confidence;
4. each material finding maps evidence -> risk -> recommendation -> validation;
5. high/critical findings have containment or validation guidance;
6. dependency/CVE claims are bound to source/dependency identity and current evidence;
7. governance findings identify the relevant authority boundary;
8. threat-model conclusions state assumptions/evidence refs instead of pretending judgment is mechanical;
9. structural evidence is separated from behavioral/runtime/external-current evidence;
10. critical evidence gaps force `review_status=blocked-critical-evidence`.

## Finding format

```markdown
### [finding-id] [short title]
- **Mode:** ...
- **Classification:** confirmed | suspicious-pattern | governance-risk | needs-verification | not-applicable
- **Severity:** critical | high | medium | low | informational
- **Confidence:** high | medium | low
- **Location:** file/line, function, section, source id, or unavailable
- **Evidence:** masked/minimal description + source identity
- **Risk:** concrete impact/misuse path, or explicit uncertainty
- **Recommendation:** minimal auditable control
- **Validation:** exact gate/probe that would verify remediation or resolve uncertainty
- **Residual risk:** what remains
```
