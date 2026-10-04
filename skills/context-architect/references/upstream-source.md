# Upstream Source and Adaptation Notes

This skill was initially inspired by GitHub's `awesome-copilot` Context Architect agent. The upstream agent describes a planning-oriented role for codebase changes that identifies relevant files, dependency graphs, ripple effects, existing patterns, implementation sequence, and tests before editing.

## Adaptations in this package

- Generalized the agent into a portable Agent Skills workflow with activation boundaries, modes, output contract, stop conditions, and validation resources.
- Added multi-ecosystem dependency tracing, explicit provenance labels, freshness/snapshot controls, and bounded closure.
- Added typed directional relation vocabulary and capability-based evidence source classes rather than binding the workflow to one code-intelligence product.
- Added change-set reverse-impact and bounded multi-hop rules informed by graph-guided code-localization and build-graph practices.
- Added context-selection evaluation with frozen-gold precision/recall/F1, budget, unsupported-selection, and no-gold/abstention semantics.
- Added selective extended-tier data-flow and dependency-version evidence branches; these are optional capabilities, not runtime dependencies.
- Added risk, validation, PR-splitting, implementation-after-approval, portability, and deterministic packaging helpers.

## Research inspirations for the 2.1 context-map contract

The following sources informed the design but create **no runtime coupling**:

- ContextBench (arXiv:2602.05892): process-level context precision/recall/F1 and efficiency.
- Agent Retrieval Bench (arXiv:2607.24882): edit-to-ripple retrieval, budget-aware context yield, and no-gold cases.
- LocAgent (arXiv:2503.09089): directed heterogeneous relation graphs and multi-hop localization.
- SCIP Code Intelligence Protocol: language-agnostic definitions/references/implementations and semantic precision spectrum.
- Nx affected/project graph and Bazel `rdeps`/`allrdeps`: changed-file impact and bounded reverse dependency traversal.
- CodeQL data-flow guidance: selective global/interprocedural flow due cost/precision trade-offs.
- CrossCoder (arXiv:2609.09987): cross-repository dependency/version context and multi-hop evidence.

These are design evidence, not mandatory tools. The core remains host-neutral and capability-based.

## Attribution

- Source: `github/awesome-copilot`; upstream Context Architect agent in the repository `agents` directory.
- License observed at source repository: MIT License, Copyright GitHub, Inc.
