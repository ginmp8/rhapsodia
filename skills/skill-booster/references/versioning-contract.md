# Skill Versioning Contract

## Source of truth

Every **created, redesigned, optimized, or repackaged** skill must include a root `VERSION` with exactly one SemVer 2.0.0 value, such as `3.0.0`, plus a root `CHANGELOG.md` containing exactly one entry for that value under `## [3.0.0]` (optionally followed by ` - YYYY-MM-DD`). A trailing newline is allowed. `RELEASE_NOTES.md` is optional for ordinary releases, but breaking changes require consumer-facing migration/release guidance. Keep any existing `release.json` version aligned with `VERSION`.

Use `VERSION` as the single package release identity. Do not inject nonstandard `version` frontmatter into portable `SKILL.md`. Schema, tool/contract, evaluator, receipt, build, environment, commit and archive-digest identifiers are different identity domains; do not substitute them for package version or bump them merely to satisfy this requirement.

## Version decision

1. Before editing, identify and preserve the previous published version and immutable baseline (root `VERSION` if present; otherwise verified release/tag/package evidence). Never infer historical releases from the size of a diff.
2. **New skill:** default to `0.1.0` until a stable compatibility promise is actually adopted, unless the user/project specifies an authoritative initial version.
3. **Existing skill with no tracked version:** recover authoritative release history if available. If no trustworthy previous version can be established, initialize an explicit *first tracked* version (default `0.1.0`), label it as a tracking adoption in the changelog/report, and disclose unknown earlier version history. Do not silently treat it as a patch of an invented baseline.
4. **Existing versioned skill:** classify changes by the affected consumer contract, including activation, instructions, capabilities, input/output, permissions, runtime, schemas, and integrations. For stable versions, PATCH = compatible correction, MINOR = compatible addition/deprecation, MAJOR = incompatible change. Pre-1.0 behavior follows any existing project policy; otherwise compatible correction -> patch and additions/incompatibilities -> minor with migration notes for incompatibilities. When evidence is insufficient, state the release decision is provisional; do not claim compatibility.
5. Create a new version **before republishing modified package bytes**. Never overwrite an immutable previously released version with different bytes. If there is no release, report `no-release` rather than manufacturing a bump; a distinct build must use distinct build/artifact identity.
6. Add release notes describing consumer-visible effects, compatibility, migration (when required), and checks actually run. Do not erase or rewrite previous changelog entries. For existing unversioned skills, do not fabricate earlier entries.

If the `version-release-governance` skill is available, use its version classification and release-decision validators when compatibility or release policy merits it; **do not require that skill to be installed**. This reference plus the bundled validator are the standalone minimum.

## Hard gate and limits

Run `<PYTHON> scripts/validate_skill_version.py --target <candidate-skill>` before delivery. For updates, also supply `--baseline <immutable-extracted-prior-skill>` to detect unchanged or regressed release versions. When the baseline is unversioned, the validator reports first-tracked adoption and cannot establish previous-release compatibility; preserve that uncertainty in the report.

Missing/malformed `VERSION`, missing/mismatched current changelog entry, or mismatched optional release metadata block validated delivery. With a versioned prior baseline, changed package bytes without a strictly higher SemVer precedence block final promotion. The bundled validator **does not classify consumer compatibility or prove that a chosen bump is sufficiently large**; use impact evidence and review for that semantic decision. It also does not prove a published release existed without an identified baseline.
