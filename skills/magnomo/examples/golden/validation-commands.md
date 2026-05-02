# Validation Commands

Run the canonical golden-example gate from the repository root:

```bash
python .github/skills/magnomo/scripts/validate_golden_examples.py --skill-root .github/skills/magnomo
```

The runner executes the expanded command set below and returns nonzero if any golden example fails validation.

## Expanded Command Contract

```bash
python .github/skills/magnomo/scripts/validate_ops.py .github/skills/magnomo/examples/golden/01-delivery-intake-github-issue/ops.yaml
python .github/skills/magnomo/scripts/validate_ops.py .github/skills/magnomo/examples/golden/02-delivery-triage-stakeholders/ops.yaml
python .github/skills/magnomo/scripts/validate_ops.py .github/skills/magnomo/examples/golden/03-replanned-demand-preserved-history/ops.yaml
python .github/skills/magnomo/scripts/validate_portfolio.py --portfolio-yaml .github/skills/magnomo/examples/golden/04-portfolio-multiple-specs/portfolio.yaml --portfolio-md .github/skills/magnomo/examples/golden/04-portfolio-multiple-specs/portfolio.md
python .github/skills/magnomo/scripts/validate_roadmap.py --roadmap .github/skills/magnomo/examples/golden/05-roadmap-large-initiative/roadmap.yaml --feature-map .github/skills/magnomo/examples/golden/05-roadmap-large-initiative/feature-map.yaml
python .github/skills/magnomo/scripts/validate_artifact.py .github/skills/magnomo/examples/golden/05-roadmap-large-initiative/governance-decisions.md
python .github/skills/magnomo/scripts/validate_roadmap.py --roadmap .github/skills/magnomo/examples/golden/06-roadmap-to-spec-handoff-mago/roadmap.yaml --feature-map .github/skills/magnomo/examples/golden/06-roadmap-to-spec-handoff-mago/feature-map.yaml
python .github/skills/magnomo/scripts/validate_contracts.py --roadmap .github/skills/magnomo/examples/golden/06-roadmap-to-spec-handoff-mago/roadmap.yaml --feature-map .github/skills/magnomo/examples/golden/06-roadmap-to-spec-handoff-mago/feature-map.yaml
python .github/skills/magnomo/scripts/validate_contracts.py --feature-map .github/skills/magnomo/examples/golden/06-roadmap-to-spec-handoff-mago/feature-map.yaml --execution-evidence .github/skills/magnomo/examples/golden/07-feature-report-after-delivery/input-magia-execution-evidence.yaml
python .github/skills/magnomo/scripts/validate_reporting.py --mode feature-report --feature-report .github/skills/magnomo/examples/golden/07-feature-report-after-delivery/feature-report.md --internal-notes .github/skills/magnomo/examples/golden/07-feature-report-after-delivery/internal-notes.md
python .github/skills/magnomo/scripts/validate_reporting.py --mode release-notes --release-notes .github/skills/magnomo/examples/golden/08-release-notes-stakeholders/release-notes.md --internal-notes .github/skills/magnomo/examples/golden/08-release-notes-stakeholders/internal-notes.md
python .github/skills/magnomo/scripts/validate_artifact.py .github/skills/magnomo/examples/golden/09-rfc-proposal-roadmap-handoff/rfc-proposals.md
python .github/skills/magnomo/scripts/validate_artifact.py .github/skills/magnomo/examples/golden/10-governance-decision-roadmap-decision/governance-decisions.md
```

Expected result: every command exits `0`. Example 01 intentionally emits warnings for unknown intake fields. The canonical runner may print those warnings and still pass because the fixture is designed to preserve unknowns rather than invent missing facts.
