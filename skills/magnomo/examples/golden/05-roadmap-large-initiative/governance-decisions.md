# Governance Decisions

## Entries

### 2026-04-24 - Prioritize saved-query controls before dashboard preview

- Status: accepted
- Decision: Move `saved-query-sharing-controls` ahead of `dashboard-role-preview`.
- Context: Workspace administration controls need a first Mago-ready candidate while dashboard access inheritance still needs discovery.
- Reason: Saved-query controls have clearer MVP boundaries and unblock the workspace administration beta.
- Alternatives: Define both features together; keep dashboard role preview first.
- Impact: Dashboard role preview remains exploratory until the saved-query model is accepted.
- Decision Maker: product-platform-lead
- Links: roadmap.yaml; feature-map.yaml
- Supersedes: none



Governance note: this file records delivery governance decisions only, not architecture decisions.
