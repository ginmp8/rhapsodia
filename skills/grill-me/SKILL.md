---
name: grill-me
description: "Explicit alias for Grilling. Use when the user says 'grill me' or explicitly invokes this command to challenge an idea, decision or plan. It delegates to grilling; it is not a separate interview method."
---

# Grill Me — explicit alias

This skill is an invocation alias, **not** an independent interview workflow.

1. Load and invoke the installed **grilling** skill through the host's supported skill mechanism; pass the user's original question and constraints unchanged.
2. Let Grilling own the question frontier, round budget, recommendations, synthesis and termination.
3. If the host cannot invoke the bundled Grilling skill, say that the dependency is unavailable; do not falsely claim delegation or improvise an inconsistent second algorithm.

Do not independently write specs, issue tickets, ADRs or code. For interviews producing canonical technical documentation, the user can explicitly choose **grill-with-docs** instead.
