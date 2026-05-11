# Upstream Source and Adaptation Notes

This skill is inspired by GitHub's `awesome-copilot` Context Architect agent. The upstream agent describes a planning-oriented role for codebase changes that identifies relevant files, dependency graphs, ripple effects, existing patterns, implementation sequence, and tests before editing.

Adaptations in this skill package:

- Generalized the agent into a ChatGPT skill with an activation description, workflow decision tree, output contract, stop conditions, and validation resources.
- Added dependency-tracing heuristics for multiple ecosystems.
- Added risk, validation, PR-splitting, and implementation-after-approval rules.
- Added package validation, activation scenarios, and a context-map skeleton generator.

Attribution:

- Source: `github/awesome-copilot`; the upstream Context Architect agent file in the repository agents directory.
- License observed at source repository: MIT License, Copyright GitHub, Inc.
