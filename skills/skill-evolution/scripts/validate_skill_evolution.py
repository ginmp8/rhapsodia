from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

REQUIRED = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/search-model.md",
    "references/candidate-and-lineage-contract.md",
    "references/recombination-contract.md",
    "references/selection-and-pareto.md",
    "references/evaluation-and-promotion.md",
    "references/state-integrity-and-resume.md",
    "references/host-portability.md",
    "assets/templates/search-contract.json.template",
    "assets/templates/search-state.json.template",
    "assets/templates/search-report.md.template",
    "scripts/_common.py",
    "scripts/validate_search_contract.py",
    "scripts/validate_search_state.py",
    "scripts/validate_candidate_request.py",
    "scripts/select_survivors.py",
    "scripts/plan_recombination.py",
    "scripts/checkpoint_search_state.py",
    "evals/activation-scenarios.json",
]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot-load:{path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--json-output")
    args = parser.parse_args()
    root = Path(args.target).resolve()
    scripts = root / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))

    errors = [f"missing:{p}" for p in REQUIRED if not (root / p).is_file()]
    skill = root / "SKILL.md"
    if skill.is_file():
        text = skill.read_text(encoding="utf-8")
        if not re.search(r"(?m)^name:\s*skill-evolution\s*$", text):
            errors.append("frontmatter:name")
        if "contract v2" not in text.lower() and "v2 search contract" not in text.lower():
            errors.append("skill:missing_v2_contract_guidance")
        for path in re.findall(r"\]\(([^)]+)\)", text):
            if "://" not in path and not path.startswith("#") and not (root / path).exists():
                errors.append(f"broken-link:{path}")

    for rel in ("assets/templates/search-contract.json.template", "assets/templates/search-state.json.template", "evals/activation-scenarios.json"):
        path = root / rel
        if path.is_file():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"invalid-json:{rel}:{exc.lineno}")

    if not errors:
        try:
            contract = json.loads((root / "assets/templates/search-contract.json.template").read_text(encoding="utf-8"))
            state = json.loads((root / "assets/templates/search-state.json.template").read_text(encoding="utf-8"))
            contract_mod = _load("skill_evolution_contract_validator", scripts / "validate_search_contract.py")
            state_mod = _load("skill_evolution_state_validator", scripts / "validate_search_state.py")
            for error in contract_mod.validate(contract):
                errors.append(f"contract-template:{error}")
            for error in state_mod.validate(contract, state):
                errors.append(f"state-template:{error}")
        except Exception as exc:  # structural validator must report, not crash
            errors.append(f"template-validation:{exc.__class__.__name__}:{exc}")

    result = {
        "status": "pass" if not errors else "fail",
        "errors": sorted(set(errors)),
        "diagnostics": [
            {"code": e.replace(":", "."), "subject": e.split(":", 1)[0], "evidence": e}
            for e in sorted(set(errors))
        ],
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        Path(args.json_output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
