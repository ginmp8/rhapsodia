# Untrusted Target Execution

Agent Skills may contain executable `scripts/` and other code. Treat target-owned code as potentially unsafe until source trust is resolved; static inspection of a skill is not permission to run its scripts.

Before executing target-owned commands when source trust is not already established:

```text
<PYTHON> scripts/assess_target_trust.py --target <TARGET_SKILL_PATH> --source-class trusted-owned|trusted-local|external-untrusted|unknown
```

Policies:

- `trusted`: normal harness execution rules still apply;
- `inspect-only`: do not execute target-owned code;
- `sandbox-required`: target code may run only behind an available isolation boundary with no application/third-party secrets, restricted or disabled network by default, and evaluator-only assets outside the candidate-visible surface.

Use capability-based isolation; Docker is not required by the portable core. If the host cannot provide the boundary required by the declared policy, mark the target-owned gate `blocked`/`not-run` rather than running it unsafely.

Never place real secrets in candidate-visible files, prompts, manifests, logs, or test fixtures merely to satisfy a target command.
