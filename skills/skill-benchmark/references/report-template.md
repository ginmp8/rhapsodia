# Skill Benchmark Report Template

Use this section order. Generated reports should live outside the benchmarked skill.

1. **Executive summary** — target, source, date, report path, score, maturity, verdict, evidence state.
2. **Scorecard** — eight weighted static dimensions totaling 100.
3. **Gate evaluation** — Agent Skills conformance plus pass/warn/review/fail evidence/action.
4. **Static structure inventory** — inspected tree/counts, missing refs, adapter/portable-core status.
5. **Benchmark health** — suite role/distribution, reference/grader health, isolation, contamination, saturation, strong-claim eligibility when supplied.
6. **Behavioral metrics** — result/status/notes; repeated-trial uncertainty and `claim_classification` for v3 comparisons; explicit `not measured` otherwise.
7. **Efficiency metrics** — tokens, latency, tool calls, cost when supplied; never silently combined with capability.
8. **Skill behavior coverage** — constraint coverage/adherence when supplied, otherwise `not measured`.
9. **Scenario suite** — should activate, should not activate, ambiguous, edge cases; label diagnostic-balanced versus production-representative.
10. **Control arms and comparability** — baseline, parent, without-skill, optional length-control, runtime/evaluator/suite identities.
11. **Evidence-based findings** — strengths, weaknesses, missing evidence.
12. **Top prioritized improvements** — priority, impact, effort, owner action.
13. **Risks if used as-is** — severity, impact, mitigation.
14. **Suggested improved description** — only when evidence supports a change; otherwise retain current description.
15. **Suggested ideal file structure** — portable core first; host adapters optional.
16. **Verdict** — `approve`, `approve with reservations`, or `reject` under rubric rules.
17. **Benchmark metadata** — method, source evidence state, target/evaluator/suite/runtime identities, scenario provenance, health/coverage evidence status, requested hosts, structural portability, generator identity/date.

A report validator must reject missing required identity metadata or unresolved scaffold markers. A live-unfrozen source may support a bounded single-run static assessment but cannot support a strict version delta. Structural multi-host support must not be described as behavioral portability without executed runtime evidence.
