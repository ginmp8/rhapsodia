from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

TOP100_REQUIRED = {
    "activation-boundary": ("## Mission and activation boundary", "Do not use"),
    "mode-router": ("## Search modes",),
    "quick-start": ("## Quick-start workflow",),
    "critical-invariants": ("## Critical invariants",),
    "direct-resource-map": ("## Direct resource map",),
    "mutation-boundary": ("target-byte mutation",),
    "promotion-boundary": ("final promotion owner",),
    "hard-gate-precedence": ("Hard-gate failure cannot be compensated",),
    "lineage-integrity": ("candidate ids are never reused and lineage is acyclic",),
    "holdout-exposure": ("Holdout exposure changes evidence status",),
    "negative-evidence": ("Preserve negative/rejected evidence",),
}

REQUIRED = [
    "SKILL.md",
    "references/search-model.md",
    "references/candidate-and-lineage-contract.md",
    "references/recombination-contract.md",
    "references/selection-and-pareto.md",
    "references/evaluation-and-promotion.md",
    "references/state-integrity-and-resume.md",
    "references/host-portability.md",
    "references/evidence-aware-profile.md",
    "assets/templates/search-contract.json.template",
    "assets/templates/search-state.json.template",
    "assets/templates/search-report.md.template",
    "assets/templates/candidate-evaluation.json.template",
    "assets/templates/search-contract-evidence-aware.json.template",
    "assets/templates/search-state-evidence-aware.json.template",
    "assets/templates/candidate-evaluation-evidence-aware.json.template",
    "contracts/integration-manifest.json",
    "scripts/_common.py",
    "scripts/validate_search_contract.py",
    "scripts/validate_search_state.py",
    "scripts/validate_candidate_request.py",
    "scripts/validate_candidate_evaluation.py",
    "scripts/select_survivors.py",
    "scripts/plan_recombination.py",
    "scripts/checkpoint_search_state.py",
    "scripts/_evidence_common.py",
    "scripts/validate_evidence_aware_search_contract.py",
    "scripts/validate_evidence_aware_search_state.py",
    "scripts/validate_evidence_aware_candidate_request.py",
    "scripts/validate_evidence_aware_candidate_evaluation.py",
    "scripts/select_survivors_evidence_aware.py",
    "scripts/checkpoint_search_state_evidence_aware.py",
    "evals/activation-scenarios.json",
]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot-load:{path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _validate_integration_manifest(root: Path, manifest: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["integration-manifest:invalid"]
    if manifest.get("manifest_version") != 1:
        errors.append("integration-manifest:manifest_version")
    if manifest.get("skill") != "skill-evolution":
        errors.append("integration-manifest:skill")

    exports = manifest.get("exports")
    if not isinstance(exports, list):
        return errors + ["integration-manifest:exports"]
    expected_exports = {
        "skill-opt.evolution-search-contract": 4,
        "skill-opt.candidate-request": 2,
        "skill-opt.search-state": 4,
        "skill-opt.candidate-evaluation": 2,
        "skill-opt.evolution-evidence-profile": 1,
    }
    seen_exports: dict[str, int] = {}
    for i, item in enumerate(exports):
        if not isinstance(item, dict):
            errors.append(f"integration-manifest:exports[{i}]")
            continue
        contract_id = item.get("contract_id")
        version = item.get("version")
        if isinstance(contract_id, str):
            seen_exports[contract_id] = version
        paths = item.get("surface_paths")
        if not isinstance(paths, list) or not paths:
            errors.append(f"integration-manifest:{contract_id or i}:surface_paths")
            continue
        for rel in paths:
            if not isinstance(rel, str) or not rel.strip():
                errors.append(f"integration-manifest:{contract_id or i}:surface_path_invalid")
            elif not (root / rel).is_file():
                errors.append(f"integration-manifest:{contract_id or i}:missing_surface:{rel}")
    for contract_id, version in expected_exports.items():
        if seen_exports.get(contract_id) != version:
            errors.append(f"integration-manifest:export:{contract_id}:v{version}")

    imports = manifest.get("imports")
    if not isinstance(imports, list):
        errors.append("integration-manifest:imports")
    else:
        generation = [i for i in imports if isinstance(i, dict) and i.get("contract_id") == "skill-opt.candidate-generation-receipt"]
        if len(generation) != 1 or 3 not in generation[0].get("accepted_versions", []):
            errors.append("integration-manifest:import:skill-opt.candidate-generation-receipt:v3")
    return errors



def _validate_context_loading(root: Path, skill_text: str) -> list[str]:
    errors: list[str] = []
    lines = skill_text.splitlines()
    top100 = "\n".join(lines[:100])

    if len(lines) > 100:
        for code, anchors in TOP100_REQUIRED.items():
            if not all(anchor in top100 for anchor in anchors):
                errors.append(f"context:top100:{code}")

    direct_links = set(re.findall(r"\]\((references/[^)#]+\.md)\)", skill_text))
    for rel in REQUIRED:
        if rel.startswith("references/") and rel.endswith(".md") and rel not in direct_links:
            errors.append(f"context:indirect-required-reference:{rel}")

    for ref in sorted((root / "references").glob("*.md")):
        ref_lines = ref.read_text(encoding="utf-8").splitlines()
        if len(ref_lines) <= 100:
            continue
        first40 = "\n".join(ref_lines[:40])
        for label in ("**Purpose:**", "**Load when:**", "**Decision impact:**", "## Contents"):
            if label not in first40:
                errors.append(f"context:long-reference-preview:{ref.name}:{label.strip('*# :').lower().replace(' ', '-')}")
        h2 = [
            line[3:].strip()
            for line in ref_lines
            if line.startswith("## ") and line[3:].strip() not in {"At a Glance", "Contents"}
        ]
        if "## Contents" in first40:
            contents = {line[2:].strip() for line in ref_lines[:40] if line.startswith("- ")}
            for heading in h2:
                if heading not in contents:
                    errors.append(f"context:contents-drift:{ref.name}:{heading}")
    return errors


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
        if "contract v4" not in text.lower() and "v4 search contract" not in text.lower():
            errors.append("skill:missing_v4_contract_guidance")
        for path in re.findall(r"\]\(([^)]+)\)", text):
            if "://" not in path and not path.startswith("#") and not (root / path).exists():
                errors.append(f"broken-link:{path}")
        errors.extend(_validate_context_loading(root, text))

    for rel in ("assets/templates/search-contract.json.template", "assets/templates/search-state.json.template", "assets/templates/candidate-evaluation.json.template", "assets/templates/search-contract-evidence-aware.json.template", "assets/templates/search-state-evidence-aware.json.template", "assets/templates/candidate-evaluation-evidence-aware.json.template", "contracts/integration-manifest.json", "evals/activation-scenarios.json"):
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
            candidate_evaluation = json.loads((root / "assets/templates/candidate-evaluation.json.template").read_text(encoding="utf-8"))
            evidence_contract = json.loads((root / "assets/templates/search-contract-evidence-aware.json.template").read_text(encoding="utf-8"))
            evidence_state = json.loads((root / "assets/templates/search-state-evidence-aware.json.template").read_text(encoding="utf-8"))
            evidence_evaluation = json.loads((root / "assets/templates/candidate-evaluation-evidence-aware.json.template").read_text(encoding="utf-8"))
            integration_manifest = json.loads((root / "contracts/integration-manifest.json").read_text(encoding="utf-8"))
            contract_mod = _load("skill_evolution_contract_validator", scripts / "validate_search_contract.py")
            state_mod = _load("skill_evolution_state_validator", scripts / "validate_search_state.py")
            evaluation_mod = _load("skill_evolution_candidate_evaluation_validator", scripts / "validate_candidate_evaluation.py")
            evidence_contract_mod = _load("skill_evolution_evidence_contract_validator", scripts / "validate_evidence_aware_search_contract.py")
            evidence_state_mod = _load("skill_evolution_evidence_state_validator", scripts / "validate_evidence_aware_search_state.py")
            evidence_evaluation_mod = _load("skill_evolution_evidence_candidate_evaluation_validator", scripts / "validate_evidence_aware_candidate_evaluation.py")
            for error in contract_mod.validate(contract):
                errors.append(f"contract-template:{error}")
            for error in state_mod.validate(contract, state):
                errors.append(f"state-template:{error}")
            for error in evaluation_mod.validate(contract, candidate_evaluation):
                errors.append(f"candidate-evaluation-template:{error}")
            for error in contract_mod.validate(evidence_contract):
                errors.append(f"evidence-aware-canonical-contract-template:{error}")
            for error in state_mod.validate(evidence_contract, evidence_state):
                errors.append(f"evidence-aware-canonical-state-template:{error}")
            for error in evaluation_mod.validate(evidence_contract, evidence_evaluation):
                errors.append(f"evidence-aware-canonical-evaluation-template:{error}")
            for error in evidence_contract_mod.validate(evidence_contract):
                errors.append(f"evidence-aware-contract-template:{error}")
            for error in evidence_state_mod.validate(evidence_contract, evidence_state):
                errors.append(f"evidence-aware-state-template:{error}")
            for error in evidence_evaluation_mod.validate(evidence_contract, evidence_evaluation):
                errors.append(f"evidence-aware-evaluation-template:{error}")
            errors.extend(_validate_integration_manifest(root, integration_manifest))
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
