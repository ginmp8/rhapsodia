# Security Taxonomy and Vulnerability Prioritization

Use this reference when a finding benefits from standardized weakness/control metadata or when known-CVE prioritization is part of the review. Taxonomy is metadata and hypothesis support; it never replaces target evidence, impact analysis, or the skill severity model.

## CWE root-cause mapping

- Map CWE only after the weakness mechanism is evidenced.
- Prefer a CWE at `Base` or `Variant` abstraction when the evidence supports that specificity.
- If only a broad weakness class is defensible, either use the broader mapping with lower mapping confidence or omit CWE; do not manufacture precision.
- Record mapping confidence separately from finding confidence when useful.
- Multiple tool alerts that map to the same weakness do not create multiple findings when they share the same root cause, subject, mechanism, and material impact.

Suggested metadata:

```yaml
cwe:
  - id: CWE-862
    mapping_level: Base
    mapping_confidence: confirmed
```

Allowed mapping confidence: `confirmed`, `likely`, `needs-verification`.

## ASVS control mapping

ASVS is a control/verification reference, not evidence that a vulnerability exists.

- Include the ASVS version in every identifier, for example `v5.0.0-1.2.5`.
- Use an ASVS mapping to state the expected control or verification requirement.
- Keep target evidence and severity rationale independent from the ASVS reference.

## CAPEC usage

Use CAPEC primarily before finding promotion:

- generate attack/abuse hypotheses;
- construct security test cases;
- identify likely attacker actions across a mapped attack surface;
- challenge mitigations and control selection;
- correlate a demonstrated attack path with an evidenced weakness.

A CAPEC pattern is not proof that the target is vulnerable. Do not promote a CAPEC-derived hypothesis to a finding without target-specific evidence.

## CVSS, EPSS, and CISA KEV

For a known CVE or dependency vulnerability, treat these as different signals:

- **CVSS-B**: intrinsic vulnerability severity; it is not complete organizational risk.
- **EPSS**: estimated probability of observed exploitation in the wild over the next 30 days; it is not impact or environment-specific risk.
- **CISA KEV**: evidence that exploitation in the wild is known; it is a strong prioritization signal, not proof that this target is reachable or exploitable.

Never map a CVSS score directly to `BLOCKER`, `MAJOR`, or another review severity. Determine review severity from the changed path and target context: affected version, reachability, exposure, exploit preconditions, authentication, tenant boundary, compensating controls, data/side-effect impact, blast radius, rollback/recovery, operational exposure, and evidence confidence. Use EPSS/KEV to refine urgency when a CVE is actually relevant.

## Research basis

- MITRE CWE root-cause mapping guidance.
- OWASP ASVS 5.0 identifier guidance.
- MITRE CAPEC use cases.
- FIRST CVSS v4 and EPSS guidance.
- CISA Known Exploited Vulnerabilities catalog guidance.
