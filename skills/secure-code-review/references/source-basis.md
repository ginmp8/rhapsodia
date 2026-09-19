# Source Basis

Policy basis reviewed on 2026-09-19. These sources ground the general rules but are not required at runtime.

- MITRE CWE-798, Use of Hard-coded Credentials: hardcoded credentials are a recognized weakness; client-side embedded credentials are especially extractable.
  - https://cwe.mitre.org/data/definitions/798.html
- MITRE CWE-532, Insertion of Sensitive Information into Log File: secrets and other sensitive information should not be written to logs.
  - https://cwe.mitre.org/data/definitions/532.html
- OWASP Secrets Management Cheat Sheet: emphasizes lifecycle controls including rotation, revocation/deletion, least privilege, and careful logging.
  - https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- GitHub Secret Scanning and Push Protection documentation: repository scanning detects hardcoded credentials; push protection can prevent supported secrets from entering repository history; exposed real secrets should be remediated/revoked.
  - https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning
  - https://docs.github.com/en/code-security/concepts/secret-security/push-protection

Provider token formats and product features change. When a review depends on the current format or response process for a specific provider, verify that provider's current primary documentation rather than treating bundled regexes as authoritative.
