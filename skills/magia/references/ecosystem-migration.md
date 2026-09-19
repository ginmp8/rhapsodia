# Ecosystem migration: 1.9.4 -> 1.10.0

This is a coordinated exact-version minor release. Nomia, Mago, and Magia remain separately installable and independently executable; no package imports or reads a peer package at runtime.

## Compatibility

- Handoff schema remains `3.0.0`; payload directions and authority do not change.
- Priority schema remains `2.0.0`; `business_priority` remains Nomia-owned and `technical_criticality`/`execution_sequence` remain Mago-owned.
- Existing valid v3 handoff envelopes remain semantically valid after their `ecosystem_release`/`source_version` are produced by the 1.10.0 package set.
- Mixed package releases remain rejected before mutation.
- Ledger document schema remains `1.0.0`; 1.10.0 adds explicit last-known-good/recovery mechanics without transferring authority.

## Upgrade

Stage all three 1.10.0 candidates, validate each package, validate byte-equivalent shared contracts, run the frozen cross-skill suite, run the independent ecosystem change gate, then promote all three as one release decision.

## Rollback

If promotion or cross-skill validation fails, restore the complete prior validated 1.9.4 set. Do not retain a mixed live set. Handoff evidence remains evidence; rollback never rewrites business, planning, or execution authority.
