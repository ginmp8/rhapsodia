# Adapter Development Contract

Use this contract when adding or materially changing a public-format adapter. It preserves Mago authority while making interoperability extensible and reviewable.

## Capability declaration

Every adapter declares:

- stable internal adapter ID;
- external format and explicit supported version or bounded file convention;
- supported operations: import, export, round trip, or read-only inspection;
- required source files;
- optional source files;
- mapped concepts;
- unsupported concepts;
- Mago-only sidecar concepts;
- loss taxonomy and severity;
- validator command;
- offline behavior;
- compatibility and deprecation policy.

Do not use `latest`, unspecified schemas, or marketing claims as compatibility evidence.

## Authority rules

- Imports are evidence until validated and normalized through one Mago mode.
- Exports and sidecars are non-authoritative projections outside `BOARD_ROOT`.
- Round-trip equality is never inferred from file existence or parser success.
- Board identity, profile, provenance, mutation state, authority boundaries, and Magia evidence remain Mago/Magia concepts even when the external format cannot represent them.
- An adapter may report a loss; it may not silently drop it.

## Loss taxonomy

| Severity | Meaning | Acceptance rule |
|---|---|---|
| `none` | semantics preserved | normal validation |
| `informational` | presentation or ordering differs without semantic effect | disclose |
| `material` | planning meaning requires sidecar or manual review | block authoritative import until resolved |
| `blocking` | identity, behavior, authority, compatibility, migration, validation, or evidence would be misrepresented | reject operation |

## Implementation sequence

1. Freeze representative source and canonical package fixtures outside the mutation batch.
2. Write a mapping table before code.
3. Implement the smallest bounded adapter path.
4. Emit checksums, mapped fields, omissions, losses, and unsupported concepts.
5. Validate report structure.
6. Run import, export, external-edit, and round-trip checks.
7. Verify output remains outside canonical paths.
8. Document version support and known losses.
9. Add release notes without claiming complete external compatibility.

## Extension gate

Accept an adapter only when the operation is version-explicit, path-contained, deterministic, offline-capable for local files, loss-complete, non-authoritative, and covered by representative validation. Reject extensions that require weakening registry, identity, profile escalation, provenance, mutation safety, or Nomia/Magia ownership.
