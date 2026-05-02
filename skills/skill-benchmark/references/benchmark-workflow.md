# Benchmark Workflow Reference

Use for command execution, evidence handling, path choices, comparison, and final responses.

## Command sequence

For a filesystem target:

1. Inspect the tree and read target `SKILL.md`.
2. Generate static report:

   ```bash
   node scripts/generate_benchmark_report.js --target <target-skill-folder> --out <benchmark-output-root>
   ```

3. If scenario results JSON exists, validate before metrics:

   ```bash
   python3 -S scripts/validate_scenario_results.py --results <scenario-results-json>
   ```

4. Generate with validated results:

   ```bash
   node scripts/generate_benchmark_report.js --target <target-skill-folder> --out <benchmark-output-root> --results <scenario-results-json>
   ```

5. Validate report:

   ```bash
   python3 -S scripts/validate_benchmark_report.py --report <generated-report-file>
   ```

6. Read the report and add qualitative findings only where evidence supports them.

Use absolute script paths when outside the skill folder. Use `--out` so evidence stays away from protected target packages.

## Path ownership

- Generated reports belong in the caller repo or explicit output dir, not inside the benchmarked skill by default.
- Do not write into target fixtures, expected outputs, secrets, credentials, or user-declared read-only paths.
- The canonical report path string is an output location, not a bundled file required by this skill.
- If files cannot be written, return report content and intended path.

## Evidence hierarchy

1. Current target files and command output.
2. User-supplied scenario results, prior reports, review notes, issue links.
3. Target-local references, examples, validators, templates, scripts.
4. Qualitative judgment, labeled as judgment.

## Static vs behavioral evidence

- Static evidence supports structure, frontmatter quality, output contract, resource integration, and validation coverage.
- Static evidence does not prove activation precision, recall, robustness, output conformance, or rework rate.
- Behavioral evidence is measured only from executed prompts or user-supplied execution results.
- Planned suites are useful but not measured evidence.

Resource integration must classify role, not count files. `references/` carry guidance, schemas, rubrics, or policy; `assets/templates/` carry reusable skeletons. A useful integrated template is not a duplicate of a reference. If deleting a useful resource improves a static score, treat that as evaluator weakness or missing integration evidence.

## Required report checks

A complete report must include all `references/report-template.md` sections; target name, inspected source, score, verdict, and gate status; automated findings separated from qualitative findings; concrete scenario prompts across required categories; metrics marked not measured without execution evidence; validated scenario JSON before measured metrics; risks and prioritized improvements; no unresolved scaffold markers, fake examples, or fabricated metrics.

## Comparison rules

Keep versions separate: identify target and baseline sources; state files/reports for each; compute deltas only from comparable measures; do not merge results unless the same frozen suite was executed.

## Final response

Include target/source path, report path or content, score/verdict, failed gates, residual risks, commands run, and whether behavioral metrics were measured, supplied, or planned only.
