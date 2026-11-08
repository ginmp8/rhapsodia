---
name: grill-me
description: "Explicit alias for Grilling. Use when the user says 'grill me' or explicitly invokes this command to challenge an idea, decision or plan. It delegates to grilling; it is not a separate interview method."
---

# Grill Me — explicit alias

This skill is an invocation alias, **not** an independent interview workflow.

1. **Native invocation:** when the host can invoke an installed named skill, activate **grilling** with the user's original question and constraints, preserving its decision frontier, round budget and termination.
2. **Instruction reuse:** when invocation is absent but available skills can be read, load Grilling's instructions through host-native discovery and apply them in this conversation. Reading instructions is not a delegated invocation.
3. **Inline semantic fallback:** when neither is available, conduct the *same Grilling contract*: identify the goal and assumptions; ask up to five dependency-ready questions per round with a recommended answer and reason; wait for user decisions; recompute the frontier; summarize confirmed, deferred and unresolved choices. Use at most three rounds by default, or a finite user-approved extension.
4. Never claim that a skill tool, subagent or another host executed when only the inline fallback ran. Missing skill-invocation APIs do not block an ordinary interview.

Do not independently write specs, issue tickets, ADRs or code. For interviews producing canonical technical documentation, the user can explicitly choose **grill-with-docs** instead.
