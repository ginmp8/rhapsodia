# Security Review Prompt Examples

Use these prompts to calibrate activation and output expectations.

## Secret handling

"Audit this skill package for hardcoded secrets, private keys, connection strings, and sensitive logging. Use SGR-2.0 classifications, never print a complete secret, and map each finding to evidence, risk, recommendation, and validation."

## Script security

"Review the scripts and validators in this package for shell injection, unsafe subprocess usage, path traversal, archive extraction risks, and unsafe packaging behavior. Do not execute target scripts."

## Dependency risk

"Inspect the dependency manifests and lockfiles for supply-chain risks, unpinned versions, install hooks, unusual registries, license flags, and missing vulnerability evidence. Do not install dependencies."

## LLM/agent governance

"Review the agents and skill instructions for authority boundaries, tool permissions, policy enforcement, audit trails, human approval, fallback, stop conditions, and handoff risk."

## Responsible AI

"Evaluate responsible-ai risks for this agent workflow. Focus on the actual domain, affected users, accessibility, privacy, fairness, explainability, opt-out, and human override."

## Threat model

"Create a lightweight threat model for this skill package, covering assets, trust boundaries, actors, abuse cases, controls, residual risks, and validation probes."

## Non-activation

"Improve this skill's activation wording, scenario coverage, and packaging maturity." Use a general skill-hardening or harness workflow unless the user explicitly asks for security or governance risk review.

## Agentic security

> Review this agent workflow for goal hijack, tool misuse, memory/context poisoning, delegated authority, cascading failures, and runtime-control effectiveness. Separate declared/static controls from behavioral/runtime evidence.

## MCP profile

> Review this MCP client/server integration using the MCP profile. Check token audience/passthrough, confused-deputy boundaries, redirect/state/PKCE where applicable, metadata fetch safety, stdio-vs-HTTP distinctions, and tool/resource/prompt trust.

## Framework mapping

> Map the evidenced findings to current OWASP/MITRE/NIST controls where useful, but keep SGR severity independent and do not make a compliance claim without jurisdiction, role, provision, effective date/version, and authoritative evidence.
