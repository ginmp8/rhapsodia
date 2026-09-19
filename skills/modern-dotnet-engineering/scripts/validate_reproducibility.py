#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

REQUIRED_GROUPS = {
    "activation",
    "non-activation",
    "ambiguous",
    "core",
    "edge",
    "regression",
    "adversarial",
    "holdout",
}
REQUIRED_MODES = {
    "quick-guidance",
    "code-review",
    "architecture-design",
    "implementation-plan",
    "production-gate",
}
REQUIRED_SKILL_MARKERS = [
    "## Activation contract",
    "## Mode router",
    "## Evidence vocabulary",
    "## Stop conditions",
    "references/36-review-evidence-and-reproducibility.md",
    "evals/scenarios.json",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--json", dest="json_path")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    checks: list[dict] = []

    def add(code: str, status: str, subject: str, evidence: dict | None = None, supported_fixes: list[str] | None = None) -> None:
        checks.append({
            "code": code,
            "status": status,
            "subject": subject,
            "evidence": evidence or {},
            "supported_fixes": supported_fixes or [],
        })

    skill = root / "SKILL.md"
    if not skill.exists():
        add("skill/missing", "fail", "SKILL.md", {}, ["restore SKILL.md"])
        text = ""
    else:
        text = skill.read_text(encoding="utf-8")
        add("skill/present", "pass", "SKILL.md", {"sha256": sha256(skill)})

    for marker in REQUIRED_SKILL_MARKERS:
        if marker in text:
            add("skill/marker-present", "pass", marker)
        else:
            add("skill/marker-missing", "fail", marker, {}, [f"add {marker} to SKILL.md"])

    ref = root / "references" / "36-review-evidence-and-reproducibility.md"
    if ref.exists():
        rtext = ref.read_text(encoding="utf-8")
        required_terms = ["executed", "observed", "supplied", "inferred", "planned", "blocked", "critical", "high", "medium", "low", "informational"]
        missing = [x for x in required_terms if f"`{x}`" not in rtext]
        add(
            "reference/evidence-contract",
            "pass" if not missing else "fail",
            str(ref.relative_to(root)),
            {"missing_terms": missing, "sha256": sha256(ref)},
            ["restore stable evidence/severity vocabulary"] if missing else [],
        )
    else:
        add("reference/evidence-contract", "fail", str(ref.relative_to(root)), {}, ["add the evidence/reproducibility reference"])

    scenarios_path = root / "evals" / "scenarios.json"
    scenario_data = None
    if scenarios_path.exists():
        try:
            scenario_data = json.loads(scenarios_path.read_text(encoding="utf-8"))
            add("scenarios/json-valid", "pass", str(scenarios_path.relative_to(root)), {"sha256": sha256(scenarios_path)})
        except Exception as exc:
            add("scenarios/json-valid", "fail", str(scenarios_path.relative_to(root)), {"error": str(exc)}, ["repair JSON syntax"])
    else:
        add("scenarios/missing", "fail", str(scenarios_path.relative_to(root)), {}, ["add evals/scenarios.json"])

    if isinstance(scenario_data, dict):
        scenarios = scenario_data.get("scenarios")
        if not isinstance(scenarios, list) or not scenarios:
            add("scenarios/list", "fail", "scenarios", {}, ["provide a non-empty scenarios list"])
        else:
            ids: set[str] = set()
            groups: set[str] = set()
            invalid_modes: list[str] = []
            errors: list[str] = []
            for index, scenario in enumerate(scenarios):
                if not isinstance(scenario, dict):
                    errors.append(f"index {index}: scenario is not an object")
                    continue
                sid = scenario.get("id")
                group = scenario.get("group")
                prompt = scenario.get("prompt")
                expected = scenario.get("expected")
                if not isinstance(sid, str) or not sid:
                    errors.append(f"index {index}: missing id")
                elif sid in ids:
                    errors.append(f"duplicate id: {sid}")
                else:
                    ids.add(sid)
                if group not in REQUIRED_GROUPS:
                    errors.append(f"{sid or index}: invalid group {group!r}")
                else:
                    groups.add(group)
                if not isinstance(prompt, str) or not prompt.strip():
                    errors.append(f"{sid or index}: missing prompt")
                if not isinstance(expected, dict) or not isinstance(expected.get("activation"), bool):
                    errors.append(f"{sid or index}: expected.activation must be boolean")
                elif expected.get("activation"):
                    mode = expected.get("primary_mode")
                    if mode not in REQUIRED_MODES:
                        invalid_modes.append(f"{sid or index}: {mode!r}")
                    gates = expected.get("hard_gates")
                    if not isinstance(gates, list) or not gates:
                        errors.append(f"{sid or index}: expected.hard_gates must be non-empty")
            missing_groups = sorted(REQUIRED_GROUPS - groups)
            add(
                "scenarios/contract",
                "pass" if not errors and not invalid_modes and not missing_groups else "fail",
                "evals/scenarios.json",
                {
                    "count": len(scenarios),
                    "groups": sorted(groups),
                    "missing_groups": missing_groups,
                    "invalid_modes": invalid_modes,
                    "errors": errors,
                },
                ["repair scenario ids/groups/expected contract"] if errors or invalid_modes or missing_groups else [],
            )

    baseline_validator = root / "scripts" / "validate_skill_content.py"
    add(
        "validator/legacy-present",
        "pass" if baseline_validator.exists() else "fail",
        "scripts/validate_skill_content.py",
        {"sha256": sha256(baseline_validator)} if baseline_validator.exists() else {},
        ["restore the legacy validator"] if not baseline_validator.exists() else [],
    )

    failures = [c for c in checks if c["status"] == "fail"]
    report = {
        "receipt_version": 1,
        "status": "fail" if failures else "pass",
        "stage": "validation",
        "checks": checks,
        "errors": len(failures),
        "warnings": 0,
        "metrics": {
            "check_count": len(checks),
            "scenario_count": len(scenario_data.get("scenarios", [])) if isinstance(scenario_data, dict) else 0,
        },
        "hashes": {
            "skill_sha256": sha256(skill) if skill.exists() else None,
            "scenario_sha256": sha256(scenarios_path) if scenarios_path.exists() else None,
        },
        "recovery": [],
    }

    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json_path:
        out = Path(args.json_path).resolve()
        protected = {
            skill.resolve() if skill.exists() else root / "SKILL.md",
            ref.resolve() if ref.exists() else root / "references" / "36-review-evidence-and-reproducibility.md",
            scenarios_path.resolve() if scenarios_path.exists() else root / "evals" / "scenarios.json",
            baseline_validator.resolve() if baseline_validator.exists() else root / "scripts" / "validate_skill_content.py",
            Path(__file__).resolve(),
        }
        if out in protected or out.is_dir():
            sys.stderr.write(f"refusing unsafe receipt path: {out}\n")
            sys.stderr.flush()
            return 2
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_name(out.name + ".tmp")
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(out)
    sys.stdout.write(payload)
    sys.stdout.flush()
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
