# Sources and proof of need

Research boundary: the user-supplied RhapsodIA 0.7.0 efficiency report, 2026-10-08. Original
ZIP SHA-256: `47c340cfacebc47b1e91f820ef775112264bf1a6fbc0dc8a09f7ee12602e13f2`.
The report recommends derived task context/evidence indexes, measured delegation, stable
prefixes, explicit provenance and conservative deterministic caches rather than a new
workflow owner. This package implements that bounded capability, not universal memory.

Primary documentation consulted for the design (accessed 2026-10-08):

- [Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): retrieve relevant material just in time; preserve critical state outside transcripts.
- [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching): stable prefix and provider-reported cache counters; no assumed billing equivalence.
- [Bazel remote caching](https://bazel.build/remote/caching): action identity depends on inputs, command and environment; incomplete dependencies invalidate safe reuse.
- [Microsoft incremental builds](https://learn.microsoft.com/visualstudio/msbuild/incremental-builds): retain native incremental mechanisms rather than replacing them indiscriminately.
- [OpenTelemetry GenAI attributes](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/): distinguish input/output/cache measurements; content-free telemetry is the local default.

Engineering choices, not external facts: reference-only action hits; all tests bypass;
8192-byte context default; 10% advisory fanout margin; one-hour pointer exchange; 300-second
lease ceiling. These are conservative bounded policies subject to measured owner-approved
revision. No documentation claims that these values optimize every workload.

## Long-context evidence informing optional selection guidance (accessed 2026-10-18)

- [Liu et al., TACL 2024](https://aclanthology.org/2024.tacl-1.9/): in evaluated models/tasks, retrieving information from the middle of long contexts can be less reliable.
- [Modarressi et al., ICML 2025 / NoLiMa](https://proceedings.mlr.press/v267/modarressi25a.html): semantically indirect matches remain difficult as contexts grow.
- [Wan et al., NAACL 2025](https://aclanthology.org/2025.naacl-long.442/): long-form summary faithfulness can vary by source position.
- [Cuconasu et al., EMNLP 2025](https://aclanthology.org/2025.emnlp-main.1422/): passage reordering heuristics do not universally improve RAG outcomes.

These sources motivate selective, source-located coverage checks, **not** a guaranteed
ordering rule, a validated performance increase, or a requirement to scan every byte.
