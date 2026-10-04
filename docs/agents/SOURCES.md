# Design and Host Sources

Reviewed on 2026-10-01. These sources are **design evidence and inspiration**, not runtime dependencies. RhapsodIA keeps portable semantic contracts in its own Skills/agent-system contract and does not import vendor harnesses, named models, or third-party orchestration runtimes.

## Original dynamic-workflow reference

- Dynamic Workflows in Claude Code: How They Work: https://claudefa.st/blog/guide/development/dynamic-workflows
  - motivates isolated contexts for long/wide/self-grading-prone work;
  - describes `agent`, pipeline, parallel/barrier behavior, structured outputs, worktree isolation, budgets, resumability/cache, and six reusable patterns;
  - distinguishes tasks that benefit from dynamic workflows from simple tasks where one agent is preferable;
  - directly informed the original `adaptive-workflow-orchestration` and `Rhapsodia Analyst` design.

RhapsodIA retains those principles while expressing them as host-neutral strategy, isolation, dependency, budget, and evidence contracts rather than Claude-specific JavaScript/runtime semantics.

## Reliable-convergence and test-oracle references

- Shopify Engineering, Helix: https://shopify.engineering/helix
  - small ordered checkpoints;
  - strict behavior, perceptual, adversarial-review, and human gates;
  - failed required gates return to repair and are not bypassed;
  - accepted feedback/evidence can improve later checkpoints;
  - inspired `workflow-plan/v2` gated convergence and the distinction between candidate, gate evidence, and promotion.
- Shopify Engineering, Building an agentic harness that outlasts the model: https://shopify.engineering/building-an-agentic-harness-that-outlasts-the-model
  - executable test oracle for findings;
  - independent/cross-model verification;
  - deterministic scripts for structured critical mechanics;
  - influenced `test-oracle-engineering` and the Rhapsodia Verifier separation.
- Anthropic Engineering, Building effective agents: https://www.anthropic.com/engineering/building-effective-agents
  - simple composable workflows, orchestrator-workers, parallelization, evaluator-optimizer, finite stopping conditions, and environment ground truth;
  - supports RhapsodIA's least-complex-strategy rule.
- Anthropic Engineering, Demystifying evals for AI agents: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
  - reinforces multi-turn environment-based evaluation and executable graders/tests.
- OpenAI, Evaluate agent workflows: https://developers.openai.com/api/docs/guides/agent-evals
  - trace-based workflow evaluation and graders;
  - reinforces separation between workflow traces, tool/handoff behavior, and evaluation evidence.
- OpenAI, Safety in building agents: https://developers.openai.com/api/docs/guides/agent-builder-safety
  - supports structured-data boundaries, approvals for consequential tools, guardrails, and eval/trace review.

## VS Code

- Custom agents: https://code.visualstudio.com/docs/agent-customization/custom-agents
  - workspace custom agents can use `.agent.md` profiles;
  - profiles can declare explicit `tools` scopes;
  - `agents` can restrict which subagents are available from a parent custom agent;
  - `user-invocable: false` can keep a profile available as a subagent without exposing it as a normal picker choice;
  - subagents operate in separate contexts subject to the active host harness.
- Agent Skills: https://code.visualstudio.com/docs/agent-customization/agent-skills
  - project skills may be discovered from host-supported skill roots.
- Custom instructions: https://code.visualstudio.com/docs/agent-customization/custom-instructions
  - intentionally not used as the RhapsodIA semantic core because global workspace instructions broaden scope.

## GitHub Copilot

- Custom agent configuration: https://docs.github.com/en/copilot/reference/custom-agents-configuration
- Custom agents/sub-agent orchestration: https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/custom-agents
- IDE subagents: https://docs.github.com/en/copilot/how-tos/copilot-in-your-ide/use-copilot-agents/use-subagents

These sources justify the current VS Code/Copilot adapter mechanics only. Other hosts consume the portable Skill and `agent-system-contract/v2` semantics through host-specific adapters/capabilities; this package does not claim the `.agent.md` format is universal.

## Design implications used by RhapsodIA

1. `Rhapsodia Supervisor` remains read-only and owns orchestration/promotion state.
2. `Rhapsodia Analyst` remains read/search-only for isolated analysis and adversarial review.
3. `Rhapsodia Verifier` is separate from Magia: it may write verification-only artifacts and execute bounded test oracles, but never production repairs or acceptance-criteria changes.
4. Nomia/Mago/Magia remain the only canonical domain owners; gated convergence is nested inside one already-resolved Magia phase.
5. `adaptive-workflow-orchestration` preserves the original dynamic-workflow patterns and adds v2 gated convergence without removing v1.
6. `test-oracle-engineering` owns executable proof contracts; `perceptual-validation` owns optional visual/perceptual evidence. Neither changes domain ownership.
7. Required gates are non-overridable. Repair creates a new candidate identity and affected gates rerun.
8. Parallelism is optional; serial fallback is preferred to installing an external orchestration runtime.
9. Host/model names are adapters/evidence only, never semantic core dependencies.

## Evidence boundary

Keep these claims separate:

- structural package validation;
- documented host capability;
- executed local validator/test evidence;
- observed host/runtime behavior;
- behavioral model eval evidence;
- perceptual/human review evidence.

A structurally portable package does not prove runtime parity across editors/models. Planned scenario files are not measured behavioral evidence until executed by an appropriate harness.

## Shopify agentic workflow evidence (2025–2026)

These public sources informed the reference-grounded convergence refinements. They are evidence inputs, not runtime dependencies.

- Shopify Engineering, **Helix: The internal tool powering our Shopify app's native migration** (2026): https://shopify.engineering/helix
- Shopify Engineering, **Building an agentic harness that outlasts the model** (2026): https://shopify.engineering/building-an-agentic-harness-that-outlasts-the-model
- Shopify Engineering, **How River takes security work from a fix to merge** (2026): https://shopify.engineering/river-vulnerability-remediation
- Shopify Engineering, **ShopGym: Realistic, reproducible sandboxes for shopping agents** (2026): https://shopify.engineering/shopgym
- Shopify Engineering, **Introducing Roast: Structured AI workflows made easy** (2025): https://shopify.engineering/introducing-roast

The reusable lessons are small checkpoints, source-as-spec, oracle-before-candidate, fresh execution contexts, current-state revalidation, deterministic enforcement, explicit evidence memory, and policy-bounded autonomy. RhapsodIA does not depend on Shopify's models, mobile stack, proprietary tools, or exact gate taxonomy.
