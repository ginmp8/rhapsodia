# Research basis and bounded traceability

## Corpus and epistemic limits

Human-team transactive memory explains the coordination of distributed knowledge. The mechanism is an analogy for multi-agent expertise discovery, not measured evidence of performance for language model agents. Published sources:

- **S-1** Wegner (1987), *Transactive Memory: A Contemporary Analysis of the Group Mind*, https://doi.org/10.1007/978-1-4612-4634-3_9: conceptual description of distributed recall and knowing who knows what.
- **S-2** Liang, Moreland & Argote (1995), *Group Versus Individual Training and Group Performance*, https://doi.org/10.1177/0146167295214009: team experiment about coordination/knowledge of expertise and assembly performance.
- **S-3** Lewis (2003), *Measuring Transactive Memory Systems in the Field*, https://doi.org/10.1037/0021-9010.88.4.587: specialization, credibility and coordination dimensions.

## Finding -> requirement -> change / evaluation

| Finding | Disposition | Requirement | Candidate implementation | Validation |
|---|---|---|---|---|
| F-1 (S-1/S-3): teams benefit from knowing who has a relevant specialty | implement (as engineering hypothesis) | R-1: bounded capability discovery without entire catalog | new Skill metadata, native-first routing, lightweight directory | skill metadata tests and planned host scenarios |
| F-2 (S-3): expertise has distinct credibility/coordination aspects | implement (as design analogy) | R-2: source identity and explicit owner/permission verification | script SHA-256 evidence, SKILL workflow guards, agent instructions | directory and authority-negative tests |
| F-3 (S-2): group coordination results cannot be directly applied to LLMs | implement (limitation) | R-3: do not claim untested agent-level performance | limits in Skill and release docs | static evidence/claim review; runtime `not-run` |
| F-4 (S-4): original agent install copies profiles but no `docs/` | implement | R-4: required routing instructions must reside in distributable Skill and agent entries | standalone skill bundle, plugin catalog inclusion, installer copy/check | isolated target installation tests |
| F-5 (S-4/S-5): newer baseline has additional metamorphic changes absent from 0.12.1 | implement | R-5: preserve baseline and only merge bounded TMS functionality | additive skill/agent routing, no replacing existing skills | entire tree hash-diff, unchanged existing Skills |
| F-6 (S-4): canonical roles and session gates already defined | already-covered | R-6: no permission escalation or lifecycle rewrites | existing agents/validator retained, additions only | agent contract and session tests |

This is bounded requirements accounting, not a claim of exhaustive scientific knowledge or successful real-host activation. Scenario tests are explicitly structural; source quality and intended behavioral transfer are reviewed separately. No evaluator was weakened to produce a pass.
