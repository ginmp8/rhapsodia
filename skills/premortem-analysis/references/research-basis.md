# Research basis and evidentiary limits

## Purpose and load condition

Load when describing why this method works, deciding its limitations, or auditing research-backed design requirements. The packaged corpus is a bounded, source-linked record, **not** a systematic review or a frozen copy of journal full texts. See `evidence/traceability.json` (directly linked in `SKILL.md`).

## Sources and supported conclusions

| Source ID | Primary source | Directly supported point | Evidence access limit |
|---|---|---|---|
| S-01 | [Mitchell, Russo and Pennington (1989)](https://doi.org/10.1002/bdm.3960020103) | Imagining future events as settled changes the structure of explanations | Publisher abstract |
| S-02 | [Gary Klein (2007)](https://hbr.org/2007/09/performing-a-project-premortem) | Premortem deliberately treats a proposed project as failed to elicit concerns | Publisher summary |
| S-03 | [AHRQ Premortem Tool](https://www.ahrq.gov/hai/tools/mvp/modules/cusp/premortem-tool.html) | Independent ideation, sharing, prioritization, intervention planning | Government procedure page |
| S-04 | [Gallop, Willy and Bischoff (2016)](https://doi.org/10.1080/19488289.2016.1240118) | In the reported comparison, premortem teams identified better-quality risks than brainstorming teams | Publisher abstract only |
| S-05 | [Gandhi, Duke and Schweitzer (2022)](https://doi.org/10.5465/AMBPP.2022.12186abstract) | Conference abstract reports external/uncontrollable attribution bias in premortems | Conference abstract only; page may restrict access |
| S-06 | [Roose, Lehman and Veinott (2023)](https://doi.org/10.1177/21695067231193680) | Ten game teams generated many concerns/mitigations, but few reduced design complexity | Publisher abstract |
| S-07 | [Wippold et al. (2025)](https://doi.org/10.1186/s43058-025-00768-z) | Structured prospective contextual analysis can complement implementation planning; limitations remain | Open-access article |

Source review date: 2026-10-14 (web access; publication versions as listed). Source metadata was captured into this skill package; the linked external article bytes were **not** archived. Sources may change and journal links can require access. No full-text inference is made from abstract-only records.

## Non-claims and portability of evidence

- No claim that premortem prevents failure by a known percentage or works universally better than alternative methods.
- Klein's often-repeated "30%" refers to explanation/reason identification claims attributed to earlier research; it is **not** a measured 30% project-success uplift.
- Findings on group participation or developer teams do not prove quality in autonomous LLM analyses. Generated multiple personas do not create independent data.
- FMEA, fault trees, red teaming, resilience testing and incident RCA remain independent processes. Premortem precedes or complements them, without replacing their evidence.
- Research-derived decisions are documented as `F-*` findings mapped to `R-*` requirements, `C-*` files, and `E-*` planned/executed evaluations. Mechanical trace closure is not empirical validation of the method.
