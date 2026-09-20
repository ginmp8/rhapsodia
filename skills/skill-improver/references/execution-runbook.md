# Execution Runbook

Use for CLI execution details, autonomous adapters, evidence snapshots, packaging, cancellation, and rollback.

## Defaults

- Work from a preserved baseline or isolated working copy.
- Use one bounded manual candidate or max three autonomous iterations unless the user explicitly sets another finite budget.
- Block evaluator scripts, scenarios, expected outputs, generated evidence, reports used as fixtures, `.git`, caches, package artifacts, credentials, and secrets.
- Treat saturated scores as gates and add a non-saturated auxiliary metric before claiming improvement.
- Keep source snapshots and run state outside the target skill package.
- Freeze the final passing candidate before packaging.

## Runtime capability check

Before mutation, record whether the host provides:

- filesystem read/write;
- Python 3.10+ or equivalent script execution;
- command execution;
- network/research when current external facts are required;
- independent evaluator/subagent support;
- artifact delivery/persistence.

Missing capabilities downgrade only the checks that depend on them. Never silently convert `not-run` into `pass`.

## Skill path resolution

Resolve exactly one target root whose root contains `SKILL.md`. Do not treat a nested multi-skill repository root as a target skill.

For autonomous runs, the target must live in a Git working tree because rejected candidates are reverted through Git. Manual-patch mode may use an equivalent immutable snapshot instead.

## Material source snapshot

When external inputs affect the patch or decision:

```text
<PYTHON> scripts/evidence_snapshot.py capture \
  --root <SOURCE_ROOT> \
  --path <PATH_1> \
  --path <PATH_2> \
  --snapshot-dir <WORK>/source-bytes \
  --manifest <WORK>/source-manifest.json
```

Verify before final acceptance:

```text
<PYTHON> scripts/evidence_snapshot.py verify \
  --manifest <WORK>/source-manifest.json
```

The autonomous runner can do this automatically with `--source-root` and repeated `--source-lock-path`.

## Hypothesis discovery

If no bounded hypothesis exists, or the current score is saturated/ambiguous, use `skill-hypothesis-discovery` or a compatible supplied backlog before mutation. Do not random-search patches.

A good backlog may conclude `no mutation recommended` or `gather evidence`; respect that result.

## Autonomous runner: Codex adapter

Backward-compatible Codex execution:

```text
<PYTHON> scripts/skill_improver_loop.py \
  --target <TARGET> \
  --evaluator skill-benchmark \
  --hypothesis-backlog <BACKLOG.json> \
  --max-iterations 3 \
  --min-delta 1.0 \
  --agent-adapter codex \
  --codex-mode full-auto
```

`--codex-mode yolo` requires `--sandbox-acknowledged` and must only be used inside an externally hardened disposable environment.

## Autonomous runner: generic command adapter

For another agent CLI, provide an argv template:

```text
<PYTHON> scripts/skill_improver_loop.py \
  --target <TARGET> \
  --evaluator command \
  --eval-command '<EVALUATOR COMMAND>' \
  --agent-adapter command \
  --agent-command-template '<AGENT_CLI> run --cwd {cwd} --target {target} --prompt {prompt}' \
  --max-iterations 3
```

The template is tokenized by `shlex` and executed without a shell. It must contain `{prompt}` and may contain `{cwd}` and `{target}`. If the external CLI cannot safely receive the prompt/path as normal argv, use the host's native action mechanism rather than forcing this adapter.

## Custom evaluator

The command should emit JSON containing at least `score`:

```text
<PYTHON> scripts/skill_improver_loop.py \
  --target <TARGET> \
  --evaluator command \
  --eval-command '<PYTHON> <SKILL_IMPROVER_ROOT>/examples/eval_skill.py --target .' \
  --benchmark-lock-path <SKILL_IMPROVER_ROOT>/examples/eval_skill.py \
  --required-gate packaging \
  --max-iterations 3
```

`<SKILL_IMPROVER_ROOT>` must be replaced with the absolute canonical path of the installed `skill-improver` package. For a concrete package-owned evaluator, use that exact same canonical path in both `--eval-command` and `--benchmark-lock-path`; relative paths are intentionally avoided because command evaluation runs from the target while benchmark locks are resolved from the git root.

Prefer `status`, `gates`, and stable diagnostics in evaluator output.

## Structural change gate

For autonomous/self-improvement acceptance, the runner defaults to `required` when `--change-gate-command` is supplied and to `advisory` when no command is available. Explicitly use `required` when an independent gate is available:

```text
--change-gate-policy required \
--change-gate-command '<COMMAND THAT EMITS JSON>'
```

For manual patches, advisory is acceptable when the user did not request fully autonomous acceptance.

## Graceful cancellation

Start with an explicit stop file or accept the default under the state directory:

```text
<PYTHON> scripts/skill_improver_loop.py \
  --target <TARGET> \
  --evaluator skill-benchmark \
  --max-iterations 3 \
  --stop-file .skill-improver/stop
```

Request cancellation:

```text
<PYTHON> scripts/cancel_skill_improver.py --stop-file .skill-improver/stop
```

Inspect canonical status without creating another session store:

```text
<PYTHON> scripts/skill_improver_status.py --target <TARGET_OR_REPOSITORY>
```

The status helper derives evidence from `.skill-improver/runs.jsonl`, the stop file, and the final report.

The runner stops before the next candidate. Accepted changes remain the last-good state; rejected/in-flight candidates are not presented as complete. By default the runner also stops after the first accepted uncommitted candidate, because continuing would blur the clean baseline. Use `--commit-accepted` only in an isolated experiment branch/worktree when multiple accepted iterations are intentionally chained.

## Diagnostic repair

When a candidate fails an objective gate:

1. run the narrowest failing check;
2. isolate one causal subject;
3. apply the smallest supported fix;
4. rerun the same check;
5. run adjacent checks only after it passes.

Stop after two consecutive non-improving rounds on the same error set unless new evidence appears.

## Final candidate identity

After final validation and before packaging:

```text
<PYTHON> scripts/evidence_snapshot.py hash-tree \
  --root <TARGET>
```

Record `tree_sha256`. Do not edit the candidate after this point without revalidation and a new identity.

## Package and receipt

Validate first, then package the frozen candidate:

```text
<PYTHON> scripts/validate_skill_improver_package.py \
  --target <TARGET>

<PYTHON> scripts/package_skill.py \
  --target <TARGET> \
  --output <OUTPUT_DIR>/skill.zip \
  --receipt <OUTPUT_DIR>/skill.zip.receipt.json
```

The packager:

- canonicalizes destinations before writing;
- rejects output/receipt aliases with the target or protected paths;
- runs the validator against a private candidate copy so validator side effects do not mutate the frozen target;
- stages and CRC-validates the ZIP;
- computes SHA-256 before commit;
- preserves/restores last-good outputs on commit failure where possible;
- writes the optional receipt atomically;
- verifies the committed package hash.

Use repeated `--protected-path` when additional evaluator/source files must never alias the package or receipt destination.

## Self-improvement safeguards

When `skill-improver` improves itself:

- use a separate working copy;
- preserve the installed baseline before edits;
- freeze `evals/`, the deterministic starter evaluator, and the package validator unless evaluator design is explicitly in scope;
- use an external structural/reproducibility evaluator for before/after evidence;
- treat static `100/100` as a gate only;
- block generated reports and source-snapshot evidence from entering the final package;
- re-run validation from outside the candidate mutation surface;
- install/replace only after the candidate is frozen and packaged.

## Reject/revert when

Reject or stop when the evaluator hash changes; a protected path changes; source verification fails; files outside scope change; required gates fail; evaluator output is missing/unparsable; the metric misses the threshold; the structural gate blocks; safety/semantic boundaries weaken; difficult tests are removed; the same repair fails twice without improvement; output destinations alias protected inputs; or validation/package delivery fails.
