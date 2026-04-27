# Benchmark Workflow Reference

Use this reference for command execution, evidence handling, path decisions, and finalization when producing a skill benchmark report.

## Filesystem command sequence

When the target skill is available as a folder, prefer this deterministic sequence:

1. Inspect the target package tree and read the target `SKILL.md`.
2. Generate a static report with the bundled generator:

   ```bash
   node scripts/generate_benchmark_report.js --target <target-skill-folder> --out <benchmark-output-root>
   ```

3. If behavioral scenario results are available as json, validate the result schema before calculating measured metrics:

   ```bash
   python3 -S scripts/validate_scenario_results.py --results <scenario-results-json>
   ```

4. Pass validated behavioral scenario results to the generator:

   ```bash
   node scripts/generate_benchmark_report.js --target <target-skill-folder> --out <benchmark-output-root> --results <scenario-results-json>
   ```

5. Validate the generated report:

   ```bash
   python3 -S scripts/validate_benchmark_report.py --report <generated-report-file>
   ```

6. Read the generated report and enrich it with qualitative findings only where evidence supports the claim.

Use absolute paths when invoking scripts from outside the skill folder. Use `--out` to keep generated evidence away from a protected target package.

## Path ownership rules

- Generated benchmark reports belong in the calling repository or explicit output directory, not inside the benchmarked skill package by default.
- Do not write benchmark reports into target fixtures, expected output folders, secrets folders, credential folders, or paths declared read-only by the user.
- Do not treat the canonical report path string as a required file inside this skill package; it is an output location created during benchmark runs.
- If the environment cannot write files, return the report content and state the intended path.

## Evidence hierarchy

Use evidence in this order:

1. Current target package files and command output from the active run.
2. User-supplied scenario results, previous benchmark reports, review notes, or issue links.
3. Target-local references, examples, validators, templates, and scripts.
4. Qualitative judgment, clearly labeled as judgment rather than measured evidence.

## Static versus behavioral evidence

Static evidence may support package structure, frontmatter quality, output contracts, resource integration, and validation coverage. Static evidence does not prove activation precision, recall, robustness, output conformance, or rework rate.

Resource integration evidence must distinguish role, not just count files. `references/` usually carry guidance, schemas, rubrics, or policies. `assets/templates/` carry reusable output skeletons that may be copied, filled, or rendered. A useful integrated template is not a duplicate of a reference merely because both describe the same artifact. If a static score would improve by deleting a useful resource, treat that as evaluator weakness or missing integration evidence, not as package improvement.

Behavioral evidence is measured only when prompts were executed or the user supplied execution results. Planned scenario suites are useful, but they are not measured evidence.

## Required generated report checks

A complete benchmark report must:

- include all sections required by `references/report-template.md`;
- state target name, inspected source, score, verdict, and gate status;
- separate automated static findings from qualitative findings;
- contain concrete scenario prompts across the required categories;
- mark metrics as not measured when no execution evidence exists;
- validate supplied scenario result json before treating any behavioral metric as measured;
- include risks and prioritized improvements;
- avoid unresolved scaffold markers, fake examples, and fabricated metrics.

## Comparison benchmark rules

When comparing versions, keep evidence separated:

- identify target and baseline sources independently;
- state which files and reports came from each version;
- compute deltas only from comparable measures;
- do not merge scenario results across versions unless the same frozen suite was executed.

## Final response evidence

When responding outside the generated report, include:

- target skill and source path;
- report path or report content;
- score and verdict;
- failed gates and residual risks;
- commands executed;
- whether behavioral metrics were measured, supplied, or only planned.
