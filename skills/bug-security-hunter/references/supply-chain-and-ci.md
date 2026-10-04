# Supply Chain and CI Review

Use this reference when the target changes dependencies, build/release automation, CI/CD, source controls, generated artifacts, package publishing, OCI images, provenance/attestations, or privileged automation.

Keep the model provider-neutral. GitHub Actions, Azure Pipelines, GitLab CI, Jenkins, package registries, OCI registries, and other systems are concrete adapters to the same trust questions.

## Causal model

Map:

`source revision -> review/merge controls -> build inputs -> privileged build/release identity -> produced artifact -> provenance/attestation -> distribution/deployment`

For each transition identify:

- who or what can modify the input;
- whether untrusted contribution-controlled bytes can execute;
- credential/token authority available at that point;
- mutable versus immutable dependency/artifact identity;
- branch/tag/history controls and bypasses;
- builder isolation and reproducibility/provenance evidence;
- artifact signing/attestation/verification where present;
- rollback/revocation path after compromise.

## Source Track questions

- Is the reviewed revision identity immutable and the same revision that is built/released?
- Are protected branches/tags/history controls sufficient for the stated threat model?
- Can a bypass actor or automation mutate source without equivalent review?
- Is source provenance or equivalent auditable evidence available when the claim depends on how the revision was created?

## Build-track questions

- Which builder produced the artifact and from which exact inputs?
- Can a contributor-controlled script run with release or repository-write credentials?
- Can build dependencies/actions/images change without a reviewed source change?
- Do privileged credentials follow least privilege and remain scoped to the job that needs them?
- Does provenance bind artifact digest, builder/process, source revision, and relevant inputs strongly enough for the stated verification claim?
- Is provenance actually verified, or merely generated and ignored?

## High-value hypotheses

- untrusted pull-request or branch code executes in a privileged workflow context;
- workflow/release token can write source, tags, packages, deployments, or security results beyond job need;
- mutable action, image, package, script, or remote installer changes after review;
- branch/tag protection can be bypassed by actors not covered by review controls;
- artifact deployed is not bound to the reviewed revision;
- generated provenance/attestation refers to different bytes or is never verified;
- secret appears in build log, artifact, cache, layer, SBOM/provenance, or test output;
- dependency pinning exists but no safe update mechanism exists, turning immutability into silent staleness.

## Dependency identity

Prefer immutable identity where the ecosystem supports it, but do not reduce supply-chain review to "pin everything". Also inspect the update strategy: update ownership, vulnerability response, lockfile/integrity semantics, registry/source trust, transitive dependencies, generated artifacts, and whether the pinned identity itself was trusted when selected.

## Severity

A privileged untrusted-code execution path with credible repository/release compromise potential is normally `BLOCKER`. Excessive token authority, mutable release dependencies, missing artifact/revision binding, or unverified provenance are severity-ranked from actual reachability and blast radius; a framework checklist score alone does not set review severity.

## Research basis

Architecture follows SLSA 1.2 Source/Build tracks and provenance concepts, with practical review hotspots informed by OpenSSF Scorecard checks such as Dangerous-Workflow, Token-Permissions, Pinned-Dependencies, and branch protection.
