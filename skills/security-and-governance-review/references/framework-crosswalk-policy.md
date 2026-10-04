# Framework Crosswalk and Compliance Claim Policy

Use when mapping findings to external security/governance frameworks, standards, adversary-technique catalogs, or regulation.

## Mapping record

Every material mapping should record:

- `framework` and exact control/category/technique/provision identifier when available;
- `source_locator`;
- `source_version_or_date` (or explicit current retrieval date for living sources);
- `mapping_type`: `coverage`, `threat-technique`, `control-family`, or `regulatory-reference`;
- `claim_level`: `mapped-only` or `supports-assessment`;
- local finding/control/evidence refs;
- limitations/conditions when the external text is contextual or evolving.

Mappings are metadata about coverage/interpretation. They do not override SGR classification, severity, confidence, or evidence sufficiency.

## Crosswalk rules

- OWASP/agentic taxonomies: use as coverage lenses, not a requirement to invent findings.
- MITRE ATLAS or similar technique catalogs: map evidenced abuse paths/techniques; do not derive severity from technique presence.
- NIST/ISO/control frameworks: map governance/control families only when the local evidence supports the relationship.
- SLSA/OpenSSF/CycloneDX or similar supply-chain sources: use for provenance/inventory/control interpretation without requiring one vendor/tool/format.
- Living sources: record version/date and revalidate when a current claim materially depends on them.

## Compliance boundary

`mapped to` != `conforms to` != `certified to`.

A strong `compliant` or `non-compliant` conclusion requires, at minimum:

- jurisdiction/scope;
- actor/role (for example provider, deployer, operator, processor, controller, or organization-specific role);
- exact provision/policy/control set;
- effective date/version;
- current authoritative source;
- target evidence showing the requirement applies and is or is not satisfied.

If any material element is missing, use `needs-verification` or a narrower governance finding. Do not convert a checklist gap into a legal violation.
