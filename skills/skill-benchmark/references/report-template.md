# Skill Benchmark Report Template

Use this section order. Generated reports should live outside the benchmarked skill.

1. **Executive summary** — target, source, date, report path, score, maturity, verdict, evidence state.
2. **Scorecard** — eight weighted dimensions totaling 100.
3. **Gate evaluation** — pass/warn/review/fail with evidence/action.
4. **Static structure inventory** — inspected tree/counts, missing refs, adapter/portable-core status.
5. **Behavioral metrics** — result, status, notes; explicit `not measured` where applicable.
6. **Scenario suite** — should activate, should not activate, ambiguous, edge cases.
7. **Evidence-based findings** — strengths, weaknesses, missing evidence.
8. **Top prioritized improvements** — priority, impact, effort, owner action.
9. **Risks if used as-is** — severity, impact, mitigation.
10. **Suggested improved description** — only when evidence supports a change; otherwise retain current description.
11. **Suggested ideal file structure** — portable core first; host adapters optional.
12. **Verdict** — `approve`, `approve with reservations`, or `reject` under rubric rules.
13. **Benchmark metadata** — method, source evidence state, target tree SHA-256, evaluator SHA-256, scenario suite SHA-256, scenario provenance, requested hosts, portable-core result, generator identity/date.

A report validator must reject missing identity metadata or unresolved scaffold markers. A live-unfrozen source may still support a bounded single-run static assessment but must produce a warning and cannot support a strict version-delta claim.
