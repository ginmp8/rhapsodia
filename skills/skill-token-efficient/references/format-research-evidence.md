# Format Research Evidence and Limits — Snapshot 2026-10-14

## Purpose and scope

Evidence used for format eligibility, not universal behavioral claims. Corpus: local prior research the external research corpus file (report.md), SHA-256 `4a1b404166e65a0d09c2f09b9a7bf414c9519d2482b06b33611e7723e650b1d5`. That file is source context, not a required installed dependency.

## Sources and claims

| ID | Source | Recorded result | Limitation |
|---|---|---|---|
| S-01 | [TOON project benchmark](https://github.com/toon-format/toon) | Reported flat-only totals (`o200k_base`): CSV 64,247; TOON 68,030; compact JSON 104,908. Mixed-structure: compact JSON 260,451; TOON 264,734. | Maintainer-published, shape-specific; different tracks must not be conflated; not independently reproduced here |
| S-02 | [He et al., 2024](https://arxiv.org/abs/2411.10541) | Prompt formatting (plain text/Markdown/JSON/YAML) can materially change task quality with identical contextual content. | Older GPT model generations; not proof for current model/tool execution |
| S-03 | [JTON project and benchmark](https://github.com/gowthamkumar-nandakishore/JTON) | Zen Grid claims token savings on selected tabular datasets, with model-specific comprehension regressions. | Author evidence, evolving format, requires explicit parser; extended JTON syntax is not native JSON for standard parsers |
| S-04 | [OpenAI tiktoken](https://github.com/openai/tiktoken) | Token counts depend on model-specific encoding; portable regex estimator is not a model tokenizer. | Tokenized payload alone does not include all provider message/tool/billing overhead |
| S-05 | Frozen local comparison in the bounded 2026-10-14 research corpus | 27 structurally checked renderings of three contracts (Markdown, JSON, YAML, XML, HTML etc.) passed; only UTF-8 bytes were measured locally. | Structural comparison is not behavioral equivalence; published source S-01 is independent from this local test |

## Finding to requirement to implementation mapping

| Finding | Disposition / requirement | Implementation | Evaluation |
|---|---|---|---|
| F-01: No universal lowest-token format | Implement: eligibility by material, corpus, parser | `references/format-selection.md`; `scripts/recommend_format.py` | Frozen format role tests |
| F-02: Tabular keys dominate repeated cost | Implement: consider reversible CSV/TSV/TOON/JTON | `references/format-selection.md`; selector | Flat/schema/decoder tests |
| F-03: Complex structures can favor JSON | Implement: compact JSON default for mixed typed data | Policy; selector | Nested/tool-schema tests |
| F-04: Tokenizers and overhead vary | Implement: retain existing pinned tokenizer and expand format hint/overhead guidance | Existing [refactor audit](../scripts/refactor_audit.py)/[runtime economics](../scripts/runtime_economics.py); policy | Existing scenario validator; explicit evidence labels |
| F-05: Format changes affect agent success | Already-covered: existing behavioral/runtime gates remain independent | Existing `references/behavioral-equivalence.md`; policy | Existing 34-scenario coverage; behavioral runtime not run |
| F-06: Duplicate knowledge creates peer drift | Implement: one provider-owned integration contract v1 | `contracts/integration-manifest.json`; schema; `references/integration-protocol.md` | Integration contract routing tests |
| F-07: Maintain normative skill format and safety | Implement: preserve Markdown entrypoint, native tool schema, typed conversion guards | Policy; selector | Incompatible/authority tests |
| F-08: New data-format benchmarks are not model-runtime evidence | Implement: source provenance and fixed evidence classes | This reference; CLI `evidence` response | Response evidence tests |

## When to refresh

Refresh after material tokenizer/model changes, new model-format evidence, a producer protocol change, or a validated contradiction. Record exact source revision/date, tokenizer, datasets, uncertainty and caller impact. A new research claim cannot override preservation, safety, or native schema gates without a separate accepted change and executed evidence.
