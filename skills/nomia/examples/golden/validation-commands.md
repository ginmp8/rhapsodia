# Validation Commands

Run the canonical golden-example gate from the repository root. Replace `<skill-root>` with the root folder of this skill package, for example `skills/nomia`, `.github/skills/nomia`, or an extracted `nomia` package directory.

```bash
python <skill-root>/scripts/validate_golden_examples.py --skill-root <skill-root>
```

The runner executes the expanded command set below and returns nonzero if any golden example fails validation.

## Expanded Command Contract

```bash
python <skill-root>/scripts/validate_ops.py <skill-root>/examples/golden/01-delivery-intake-github-issue/ops.yaml
python <skill-root>/scripts/validate_ops.py <skill-root>/examples/golden/02-delivery-triage-stakeholders/ops.yaml
python <skill-root>/scripts/validate_ops.py <skill-root>/examples/golden/03-replanned-demand-preserved-history/ops.yaml
python <skill-root>/scripts/validate_portfolio.py --portfolio-yaml <skill-root>/examples/golden/04-portfolio-multiple-specs/portfolio.yaml --portfolio-md <skill-root>/examples/golden/04-portfolio-multiple-specs/portfolio.md
python <skill-root>/scripts/validate_roadmap.py --roadmap <skill-root>/examples/golden/05-roadmap-large-initiative/roadmap.yaml --feature-map <skill-root>/examples/golden/05-roadmap-large-initiative/feature-map.yaml
python <skill-root>/scripts/validate_artifact.py <skill-root>/examples/golden/05-roadmap-large-initiative/governance-decisions.md
python <skill-root>/scripts/validate_roadmap.py --roadmap <skill-root>/examples/golden/06-roadmap-to-spec-handoff-mago/roadmap.yaml --feature-map <skill-root>/examples/golden/06-roadmap-to-spec-handoff-mago/feature-map.yaml
python <skill-root>/scripts/validate_contracts.py --roadmap <skill-root>/examples/golden/06-roadmap-to-spec-handoff-mago/roadmap.yaml --feature-map <skill-root>/examples/golden/06-roadmap-to-spec-handoff-mago/feature-map.yaml
python <skill-root>/scripts/validate_contracts.py --feature-map <skill-root>/examples/golden/06-roadmap-to-spec-handoff-mago/feature-map.yaml --execution-evidence <skill-root>/examples/golden/07-feature-report-after-delivery/input-magia-execution-evidence.yaml
python <skill-root>/scripts/validate_reporting.py --mode feature-report --feature-report <skill-root>/examples/golden/07-feature-report-after-delivery/feature-report.md --internal-notes <skill-root>/examples/golden/07-feature-report-after-delivery/internal-notes.md
python <skill-root>/scripts/validate_reporting.py --mode release-notes --release-notes <skill-root>/examples/golden/08-release-notes-stakeholders/release-notes.md --internal-notes <skill-root>/examples/golden/08-release-notes-stakeholders/internal-notes.md
python <skill-root>/scripts/validate_artifact.py <skill-root>/examples/golden/09-rfc-proposal-roadmap-handoff/rfc-proposals.md
python <skill-root>/scripts/validate_artifact.py <skill-root>/examples/golden/10-governance-decision-roadmap-decision/governance-decisions.md
```

Expected result: every command exits `0`. Example 01 intentionally emits warnings for unknown intake fields. The canonical runner may print those warnings and still pass because the fixture is designed to preserve unknowns rather than invent missing facts.
