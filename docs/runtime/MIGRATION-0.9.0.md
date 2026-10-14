# Upgrade from RhapsodIA 0.8.0 to 0.9.0

Install the full 0.9.0 source distribution together: 55 skills, seven canonical native agents, and synchronized marketplace metadata. Preserve any independently customized host instruction blocks; configuration remains opt-in.

## Existing state and ownership

- Domain artifacts, runtime-harness 1.2.0 state, operational-context 1.0.0 records, and Nomia/Mago/Magia/Verifier ownership are unchanged. Do not migrate, rewrite, or delete canonical domain records.
- Refresh only disposable runtime state when installation/path/identity changes, using the existing 0.8.0 guidance if applicable. Avoid reusing stale proofs or promoting cache/pointer references into authority.
- `skill-opt.token-efficiency` v1 imports are optional. A missing provider must degrade to an explicit unavailable/skipped advisory, not block other creation, optimization or benchmarking work.

## Research workspaces

The Deep Research Suite 0.2.0 has stricter source/claim readiness, field-required defaults, guarded resume and fail-closed reporting. Existing `outline.yaml`/`fields.yaml` and flat/nested result JSON remain accepted structurally, but previously saved results may need **targeted revalidation**, especially when fields omit `required: false`, evidence is incomplete, or resume stamps are missing. Do not auto-stamp unverified live sources, rewrite results silently, or present partial reports as complete. Validate each workspace and affected result before reuse.

## Skill lifecycle

New and newly optimized skills require root `VERSION` (SemVer) and a matching `CHANGELOG.md` current-version entry. Legacy unchanged skills are not silently bulk-versioned. `Reverse Engineering` is first explicitly tracked as 0.1.0. The Golden Source interface remains `skill-opt.token-efficiency` v1; no consumer may write its owner contract or lower independent acceptance gates.

## Host portability

Keep canonical `agents/` and `skills/` in place. Legacy Copilot/VS Code, Cursor, Claude, and Codex/OpenAI use the generated host adapters; a host manifest is not proof of a tested native installation. CI definitions include release metadata and regression suites but are not substitute evidence for live Windows/macOS/IDE testing.

## Rollback

Stop writers, restore the exact full 0.8.0 distribution, and regenerate only disposable operational caches with incompatible identities. Never roll back by editing canonical data or forcing newer workspaces through older research validation unreviewed. Retain backups of original research results before deliberate schema/content migrations. No remote tag or deployment is asserted.
