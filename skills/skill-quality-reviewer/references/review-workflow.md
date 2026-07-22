# Review Workflow

## 1. Establish the target

Record:

- root skill path or archive;
- intended capability and owner role;
- requested mode and output language;
- files supplied, files omitted, and protected paths;
- known failures, prior reviews, or expected behavior.

Do not begin semantic scoring until the root is unambiguous.

## 2. Build the package map

Inventory the control plane and support surfaces:

| Surface | Questions |
|---|---|
| `SKILL.md` | Can the skill activate, route, execute, stop, and produce its declared output? |
| `agents/openai.yaml` | Does user-facing metadata match the actual capability? |
| `references/` | Are detailed rules reachable, current, non-contradictory, and loaded only when needed? |
| `scripts/` | Are deterministic helpers integrated, runnable, and aligned with the instructions? |
| `assets/` | Are assets used in outputs rather than hidden reasoning? |
| `examples/` | Do examples calibrate difficult decisions rather than repeat obvious instructions? |
| `evals/` | Do scenarios cover activation, non-activation, ambiguity, and edge behavior? |
| validators/package tools | Do they validate the properties used in readiness claims? |

## 3. Reconstruct the behavioral contract

Write a compact model:

- **Role:** what operational responsibility the skill owns.
- **Activation:** prompts and artifacts that should trigger it.
- **Boundaries:** adjacent requests it must reject or hand off.
- **Inputs:** minimum evidence needed to proceed.
- **Modes:** variants of the same role and their routing rules.
- **Workflow:** ordered state transitions from intake to closure.
- **Outputs:** required sections, formats, evidence, and verdicts.
- **Validation:** checks required before readiness or packaging claims.
- **Stop conditions:** situations where proceeding would invent facts or produce an invalid result.

Use this model as the source for invariants and findings.

## 4. Define invariants

At minimum, evaluate these invariants:

1. A common valid request can activate the skill without extra hidden context.
2. A common adjacent request does not incorrectly activate the skill.
3. Every mode has a reachable entry, executable path, output, and closure rule.
4. Every required resource exists and is loadable at the point it is needed.
5. The same concept has one compatible meaning across files.
6. Validators do not claim to prove properties they do not inspect.
7. Planned scenarios are not reported as executed results.
8. Packaging rules cannot include generated noise or omit required files.
9. The output contract can be satisfied from the required inputs.
10. The correction input can be executed without access to the original review conversation.

Add domain-specific invariants when the target declares stronger behavior.

## 5. Run two evidence passes

### Structural pass

Use deterministic inspection for parseability, links, placeholders, syntax, inventory, eval categories, metadata, and package noise. Treat heuristics such as candidate orphan files or missing optional sections as review leads, not automatic defects.

### Semantic pass

Trace behavior and challenge optimistic assumptions:

- wrong mode selected for a common prompt;
- instructions require evidence never requested or produced;
- later steps contradict earlier authority or scope;
- a resource is named but never loaded;
- a validator checks structure while the report claims behavioral quality;
- an output template omits a mandatory field;
- a stop condition makes a core mode impossible;
- examples teach behavior that frontmatter cannot activate;
- cleanup or token reduction removes a required contract;
- package instructions reference tools not bundled or available.

## 6. Test defect hypotheses

For each high-value hypothesis record:

- trigger or condition;
- expected correct behavior;
- suspected failure;
- evidence needed;
- observed evidence;
- decision: confirmed, rejected, needs verification, or out of scope.

Do not combine unrelated hypotheses into one finding.

## 7. Score after findings

Score only after the evidence pass. For each dimension:

- cite the strongest supporting evidence;
- state deductions and their reason;
- avoid double-counting one defect across many dimensions;
- apply gate overrides after the weighted total;
- label the result as static judgment unless an evaluator was executed.

## 8. Build remediation input

Include only confirmed findings and explicitly selected likely findings in required fixes. Put questions and speculative improvements in separate sections. Preserve exact paths, non-goals, validation commands, and acceptance criteria.

## 9. Closure criteria

A review is complete for the stated scope when:

- every supplied file was inspected or explicitly excluded;
- every blocker/major hypothesis is confirmed, rejected, or named as a decision-relevant gap;
- structural and semantic evidence are separated;
- findings meet the finding quality bar;
- the scorecard shows evidence and gate effects;
- the verdict follows the findings;
- the correction input is self-contained and validated or its validation gap is stated.
