from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_review_report import validate  # noqa: E402


def _valid_report() -> str:
    correction = """```markdown
## Objective
X
## Writable Scope
X
## Read-only / Protected Scope
X
## Preserve
X
## Non-goals
X
## Legacy and Compatibility Constraints
X
## Required Fixes
X
## Validation Sequence
X
## Completion Report
X
```"""
    return f"""# Skill Quality Review
## Executive Summary
- Mode: `full-review`
- Verdict: READY
## Scope and Evidence
### Reviewed
X
## Review Profile
- Review layers: package integrity | operational quality
- Spec baseline: not-applicable
- Host profiles: portable
- Model-judge calibration: uncalibrated
- Behavioral trial policy: not-required
## Evidence Coverage and Confidence
| Layer | Status | Evidence | Claim ceiling |
|---|---|---|---|
| Structural/package | complete | x | structural |
| Semantic | complete | x | semantic |
| Behavioral | not-run | x | none |
| Runtime | not-run | x | none |
| Host-semantic | not-run | x | portable-only |
- Confidence: medium
## Review Evidence Manifest
- Manifest status: observed
- Target identity: abc
- Reviewer identity: def
- Evaluator/scenario identity: ghi
- Source/spec identity: jkl
## Reconstructed Skill Contract
X
## Canonical Source Map
X
## Behavioral Invariants
X
## Legacy and Compatibility Assessment
X
## Scorecard
X
## Findings
No material findings exist in the inspected scope.
## Rejected Hypotheses and Positive Signals
X
## Validation Gaps
X
## Prioritized Remediation Plan
X
## Correction Input
{correction}
## Final Verdict
- Verdict: READY
"""


def test_valid_report_with_evidence_profile_passes():
    result = validate(_valid_report())
    assert result["valid"], result["errors"]


def test_missing_review_evidence_manifest_fails():
    text = _valid_report().replace(
        "## Review Evidence Manifest\n- Manifest status: observed\n- Target identity: abc\n- Reviewer identity: def\n- Evaluator/scenario identity: ghi\n- Source/spec identity: jkl\n",
        "",
    )
    result = validate(text)
    assert not result["valid"]
    assert any("Review Evidence Manifest" in error for error in result["errors"])
