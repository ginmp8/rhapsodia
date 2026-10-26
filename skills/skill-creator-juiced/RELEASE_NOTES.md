# Skill Creator Juiced 0.2.1

## ChatGPT discovery compatibility

Enforce 1-500 Unicode characters in YAML frontmatter `description` fields before package acceptance. Preserve trigger and non-use intent while shortening descriptions. This patch leaves the existing ownership and execution contracts unchanged.

## Validation

Run the native package quality gates and the RhapsodIA-wide description regression suite before release.

---

# Skill Creator Juiced 0.2.0

## Compatibility and behavior

Added an optional Token Efficient v1 advisory import for an already-staged new or redesigned skill. Creator Juiced still owns creation and final acceptance; it never authorizes the provider to mutate its draft through the read-only advice contract. Existing workflows continue when the provider is unavailable, with evidence status made explicit.

## Validation

Static contract, version, package and portability checks are required before promotion; they do not prove identical behavior on each host.

---

# Skill Creator Juiced 0.1.0

## Release identity

This is the first version tracked by a root `VERSION` file in the supplied package. Previous published version history was not available; `0.1.0` does not claim to be a patch of any prior release.

## Changed contract

Any skill created, optimized, or delivered through this package must declare its own root SemVer `VERSION` and matching `CHANGELOG.md` entry. The validators and packager reject missing or inconsistent release identity. For existing versioned skills, supply an immutable prior skill folder with `--baseline` to prevent republishing changed bytes without an advanced version.

## Migration

For a previously unversioned target skill, identify any authoritative published version. If no reliable prior version exists, create a first-tracked `VERSION` (default `0.1.0` for experimental packages), add a matching changelog entry, and disclose uncertain prior history. Keep any existing `release.json` synchronized. Choose the version increment of previously versioned skills from evidenced consumer compatibility, not from the edit size.

## Compatibility and rollback

This change intentionally tightens the delivery gate and can block previously acceptable unversioned packages. It does not change the skill's primary responsibility. Preserve the previous release and its bytes; do not bypass the new gate by overwriting an immutable release. A rollback must use the prior package with its previous validation policy and must not overwrite archives from a different version.

## Validation limits

The bundled validator proves formatting/documentation consistency and monotonic version precedence against a supplied versioned baseline; it does not prove the semantic adequacy of a selected PATCH/MINOR/MAJOR increment or execute host runtime behavior.
