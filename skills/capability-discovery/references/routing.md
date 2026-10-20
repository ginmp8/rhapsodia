# Capability discovery and routing

## Purpose, load condition and decision impact

- **Purpose:** Find existing competencies using current native host inventory and optional locally source-pinned candidate lookup without duplicating every Skill's instructions.
- **Load when:** Specialist ownership is ambiguous, multiple nearby Skills could match, no native match is evident, or the caller must explain a handoff boundary.
- **Decision impact:** Separates competence from availability and authority; directs ambiguous cases to source verification and partial scans to `unresolved`, not absence.

## Principles

Human transactive-memory research describes specialization, credibility and coordination; the transfer to AI/agents is a design hypothesis. Specialization is Skill/agent *scope*, credibility is current source provenance plus applicable evidence (not a rating), and coordination is the existing owner/delegation protocol. No part of this analogy establishes an extra agent role or permission.

## Example distinctions

- **Execution request** -> Magia can own authorized execution; a specialized security-review Skill can provide bounded advisory method but cannot approve changes or rewrite Magia acceptance.
- **Planning request** -> Mago owns technical planning; a specialized design Skill may help within Mago's contract and cannot become a substitute business owner.
- **Direct one-off explanation** -> Adhoc may execute the most relevant Skill in-process; finding a native Supervisor or Verifier profile does not authorize custom agent invocation.
- **External installed Skill not present in Rhapsodia source** -> Host-native discovery may select it after checking non-use boundary; a repository source directory cannot disprove its availability.
- **Source metadata only** -> Treat as a candidate until host loading, tool capability, permissions and source freshness are confirmed.

## Decision guardrails

1. Require the normal Runtime Harness/Local Graph gate before repository/task search, subject to exact independent user opt-outs; capability-discovery is not a substitute for environment discovery.
2. Verify the actual project/skill/agent roots and record scanned scope. `--root` uses conventional workspace roots only; explicitly passed additional directories must be approved and must not be symlinked.
3. Ask whether each relevant candidate actually owns the requested *outcome* or merely supplies reusable expertise; use selected `SKILL.md` non-use boundaries rather than token overlap alone.
4. Check authority at the consuming agent and native host, not from source metadata. Preserve canonical lifecycle ownership, single writer, independent evidence and typed handoff restrictions.
5. For required unresolved capability, verify native and bounded permitted sources before `blocked`; if scan is partial, say `unresolved`. Optional support can be omitted with `not-run` when the task remains legitimate and possible.
6. Return only concise source-pinned evidence and any material uncertainty; do not persist a parallel catalog or rewrite the Graph. Local Graph may retain verified locators as reusable knowledge after owner-approved workflows, not static availability claims.

## Installation boundary

Native Cursor/Claude/Copilot plugins install/discover the Skill through their own declared `skills/` component. Codex/portable plugins likewise expose Skills, not necessarily custom agents. The standalone VS Code/Copilot installer (`scripts/install_agents.py`) installs this full Skill alongside its eight profiles by default; `--agents-only` intentionally leaves native discovery as fallback. These are structural distribution claims; actual host-side activation remains unverified until exercised.

## Relevant human research and limitation

- Wegner (1987), *Transactive Memory: A Contemporary Analysis of the Group Mind*: https://doi.org/10.1007/978-1-4612-4634-3_9.
- Liang, Moreland & Argote (1995), *Group Versus Individual Training and Group Performance*: https://doi.org/10.1177/0146167295214009.
- Lewis (2003), *Measuring Transactive Memory Systems in the Field*: https://doi.org/10.1037/0021-9010.88.4.587.

No controlled cross-host model benchmark is claimed. Static candidate identity, semantic selection, native Skill activation and downstream task success must be evaluated separately.
