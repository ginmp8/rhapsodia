from __future__ import annotations

import argparse
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
    "scripts/validate_search_contract.py",
    "scripts/validate_search_state.py",
    "scripts/select_survivors.py",
    "scripts/plan_recombination.py",
    "evals/activation-scenarios.json",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    root = Path(args.target).resolve()
    errors = [f"missing:{p}" for p in REQUIRED if not (root / p).is_file()]
    skill = root / "SKILL.md"
    if skill.is_file():
        text = skill.read_text(encoding="utf-8")
        if not re.search(r"(?m)^name:\s*skill-evolution\s*$", text):
            errors.append("frontmatter:name")
        for path in re.findall(r"\]\(([^)]+)\)", text):
            if "://" not in path and not path.startswith("#") and not (root / path).exists():
                errors.append(f"broken-link:{path}")
    if errors:
        print("FAIL")
        for error in sorted(set(errors)):
            print(error)
        return 2
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
