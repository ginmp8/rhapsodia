# Source Basis

Research basis refreshed on **2026-10-04**. These sources ground the bundled policy; provider/product details remain version-sensitive and should be re-verified when a review depends on exact current behavior.

## Standards and primary guidance

- OWASP ASVS 5.0 V13.3 Secret Management: secret management, least privilege, rotation/expiration, and prohibition on secrets in source/build artifacts.
  - https://github.com/OWASP/ASVS/blob/master/5.0/en/0x22-V13-Configuration.md
- OWASP Secrets Management Cheat Sheet: secret lifecycle, storage/provisioning/auditing/rotation and handling considerations.
  - https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- GitHub Secret Scanning: scans entire Git history on all branches; remediation guidance.
  - https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning
- GitHub validity checks: provider-backed `active | inactive | unknown` metadata.
  - https://docs.github.com/en/code-security/concepts/secret-security/validity-checks
- GitHub sensitive-data removal: revoke/rotate first; history rewriting has coordination and clone/fork limitations.
  - https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
- GitHub Actions secure use and pull_request_target hardening: least privilege, transformed-secret masking limits, and privileged/untrusted boundaries.
  - https://docs.github.com/en/actions/reference/security/secure-use
  - https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target
- Docker build secrets and build check guidance: avoid secret-bearing ARG/ENV; prefer secret/SSH mounts.
  - https://docs.docker.com/build/building/secrets/
  - https://docs.docker.com/reference/build-checks/secrets-used-in-arg-or-env/
- Kubernetes Secret good practices: Base64 is not encryption, etcd encryption at rest, least-privilege RBAC.
  - https://kubernetes.io/docs/concepts/security/secrets-good-practices/
- Terraform sensitive data / ephemeral / write-only arguments.
  - https://developer.hashicorp.com/terraform/language/manage-sensitive-data
  - https://developer.hashicorp.com/terraform/language/manage-sensitive-data/write-only

## Research evidence

- Soltaniani & Ghafari, *Learning to detect hardcoded secrets* (2026): contextual features materially affect performance; false positives remain common and human review remains necessary.
  - https://link.springer.com/article/10.1007/s10664-026-10929-w
- Huang et al., *Checked-In Secret Detection: Strings Are All You Need* (2026): regex-only limitations and context-aware detection evidence.
  - https://arxiv.org/abs/2608.04523
- *Credential Leakage in LLM Agent Skills: A Large-Scale Empirical Study* / SkillLeakBench (2026): agent-skill credential leakage, instruction+code analysis, and stdout/debug exposure.
  - https://arxiv.org/abs/2604.03070
  - https://sites.google.com/view/agent-skills-privacy

## Portability basis

The semantic package follows the open Agent Skills model (`SKILL.md` plus optional scripts/references/assets). Host metadata is optional/adapted at the edge.

- https://agentskills.io/
- https://developers.openai.com/api/docs/guides/tools-skills
- https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
- https://cursor.com/docs/skills
- https://github.com/anthropics/skills

## Freshness rule

Provider token formats, validity APIs, host discovery paths, CI semantics, Terraform/provider capabilities, and product feature availability change. Re-check primary documentation when an exact current provider/host behavior is material to the review. Bundled regexes are supporting detectors, not authoritative provider specifications.
