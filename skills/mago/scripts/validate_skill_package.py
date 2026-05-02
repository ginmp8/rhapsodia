#!/usr/bin/env python3
"""Validate MAGO skill package integrity before distribution."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".template"}
REQUIRED_FRONTMATTER_KEYS = ("name", "description")
REQUIRED_DIRS = ("agents", "assets/templates", "references", "references/modes", "scripts")
REQUIRED_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/canonical-paths.md",
    "references/common-planning.md",
    "references/evidence-contract.md",
    "references/operating-rules.md",
    "references/validation-and-packaging.md",
    "references/activation-routing.md",
    "scripts/validate_activation_scenarios.py",
    "scripts/validate_artifact.py",
    "scripts/validate_boundary.py",
    "scripts/validate_evidence_contract.py",
    "scripts/validate_package.py",
    "scripts/validate_repo_board.py",
    "scripts/validate_skill_package.py",
    "scripts/write_artifact_scaffold.py",
    "assets/templates/manifest.yaml.template",
    "assets/templates/tasks.md.template",
    "examples/activation-scenarios.json",
)
MODE_REFERENCES = (
    "adapt",
    "define-product",
    "define-tasks",
    "define",
    "discovery",
    "order",
    "prepare-define",
    "refine-product",
    "refine-tasks",
    "refine",
    "reshape-tasks",
    "technical-design",
)
PLACEHOLDER_PATTERNS = (
    re.compile(r"\[" + "TO" + "DO", re.IGNORECASE),
    re.compile(r"\b" + "TO" + "DO" + r"\s*:", re.IGNORECASE),
    re.compile("FIX" + "ME", re.IGNORECASE),
    re.compile("replace" + " with actual", re.IGNORECASE),
    re.compile(r"this is a placeholder", re.IGNORECASE),
)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
INLINE_PATH_RE = re.compile(r"`([^`]+\.(?:md|py|sh|yaml|yml|json|template|txt))`")


@dataclass
class ValidationResult:
    status: str = "pass"
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checked_files: int = 0
    compiled_scripts: int = 0

    def fail(self, message: str) -> None:
        self.status = "fail"
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    data: dict[str, str] = {}
    for raw_line in text[4:end].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def normalize_ref(raw: str) -> str | None:
    ref = raw.strip().split("#", 1)[0].strip()
    if not ref or "://" in ref or ref.startswith("mailto:"):
        return None
    if any(ch.isspace() for ch in ref):
        return None
    return ref


def extract_refs(skill_text: str) -> list[str]:
    refs: set[str] = set()
    for match in MARKDOWN_LINK_RE.finditer(skill_text):
        ref = normalize_ref(match.group(1))
        if ref:
            refs.add(ref)
    for match in INLINE_PATH_RE.finditer(skill_text):
        ref = normalize_ref(match.group(1))
        if ref:
            refs.add(ref)
    return sorted(refs)


def iter_text_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix.lower() in TEXT_SUFFIXES
    )


def validate_frontmatter(root: Path, result: ValidationResult) -> None:
    skill_md = root / "SKILL.md"
    text = read_text(skill_md)
    frontmatter = parse_frontmatter(text)
    keys = tuple(frontmatter.keys())
    if keys != REQUIRED_FRONTMATTER_KEYS:
        result.fail(f"SKILL.md frontmatter keys must be exactly {REQUIRED_FRONTMATTER_KEYS}, got {keys}")
        return
    if frontmatter["name"] != "mago":
        result.fail(f"SKILL.md name must be mago, got {frontmatter['name']}")
    if frontmatter["description"] != frontmatter["description"].lower():
        result.fail("SKILL.md description must be lowercase")
    if len(frontmatter["description"].split()) < 25:
        result.fail("SKILL.md description must be specific enough for activation, expected at least 25 words")


def validate_required_paths(root: Path, result: ValidationResult) -> None:
    for rel in REQUIRED_DIRS:
        if not (root / rel).is_dir():
            result.fail(f"missing required directory: {rel}")
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            result.fail(f"missing required file: {rel}")
    for mode in MODE_REFERENCES:
        rel = f"references/modes/{mode}.md"
        if not (root / rel).is_file():
            result.fail(f"missing mode reference: {rel}")


def validate_skill_links(root: Path, result: ValidationResult) -> None:
    text = read_text(root / "SKILL.md")
    for ref in extract_refs(text):
        candidate = (root / ref).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            result.fail(f"SKILL.md reference leaves skill root: {ref}")
            continue
        if not candidate.exists():
            result.fail(f"SKILL.md reference does not exist: {ref}")


def validate_placeholders(root: Path, result: ValidationResult) -> None:
    for path in iter_text_files(root):
        rel = path.relative_to(root).as_posix()
        if rel.startswith("assets/templates/"):
            continue
        text = read_text(path)
        result.checked_files += 1
        for number, line in enumerate(text.splitlines(), start=1):
            if "re.compile" in line:
                continue
            if any(pattern.search(line) for pattern in PLACEHOLDER_PATTERNS):
                result.fail(f"{rel}:{number}: unresolved scaffold marker: {line.strip()[:120]}")


def validate_agents(root: Path, result: ValidationResult) -> None:
    text = read_text(root / "agents/openai.yaml")
    required_terms = ("interface:", "display_name:", "short_description:", "default_prompt:", "allow_implicit_invocation:")
    for term in required_terms:
        if term not in text:
            result.fail(f"agents/openai.yaml missing {term}")
    if "implement" in text.lower() and "do not" not in text.lower():
        result.warn("agents/openai.yaml mentions implementation without an explicit boundary")


def validate_scenarios(root: Path, result: ValidationResult) -> None:
    path = root / "examples/activation-scenarios.json"
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        result.fail(f"examples/activation-scenarios.json is invalid JSON: {exc}")
        return
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) < 4:
        result.fail("examples/activation-scenarios.json must contain at least four scenarios")
        return
    required = {"id", "case_type", "prompt", "expected_activation", "expected_mode", "expected_boundary"}
    allowed_case_types = {"should_activate", "should_not_activate", "ambiguous", "edge_case", "regression", "adversarial"}
    case_type_counts = {case_type: 0 for case_type in allowed_case_types}
    seen_ids: set[str] = set()
    has_refusal = False
    for index, scenario in enumerate(scenarios, start=1):
        if not isinstance(scenario, dict):
            result.fail(f"scenario {index} must be an object")
            continue
        missing = required - set(scenario)
        if missing:
            result.fail(f"scenario {index} missing keys: {sorted(missing)}")
        case_type = scenario.get("case_type")
        if case_type not in allowed_case_types:
            result.fail(f"scenario {index} has unsupported case_type: {case_type!r}")
        else:
            case_type_counts[case_type] += 1
        scenario_id = scenario.get("id")
        if not isinstance(scenario_id, str) or not scenario_id:
            result.fail(f"scenario {index} has invalid id")
        elif scenario_id in seen_ids:
            result.fail(f"duplicate scenario id: {scenario_id}")
        else:
            seen_ids.add(scenario_id)
        if scenario.get("expected_activation") is False:
            has_refusal = True
    if not has_refusal:
        result.fail("activation scenarios must include at least one non-activation boundary case")
    minimum_case_counts = {"should_activate": 5, "should_not_activate": 5, "ambiguous": 5, "edge_case": 3, "regression": 2, "adversarial": 2}
    for case_type, minimum in minimum_case_counts.items():
        if case_type_counts.get(case_type, 0) < minimum:
            result.fail(f"activation scenarios need at least {minimum} {case_type} cases, found {case_type_counts.get(case_type, 0)}")



def validate_activation_metrics(root: Path, result: ValidationResult) -> None:
    script_path = root / "scripts" / "validate_activation_scenarios.py"
    with tempfile.TemporaryDirectory(prefix="mago-activation-") as tmp:
        report_path = Path(tmp) / "activation-validation.json"
        completed = subprocess.run(
            [sys.executable, str(script_path), str(root), "--json-output", str(report_path)],
            cwd=str(root),
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout).strip().splitlines()[-1:]
            result.fail(f"activation scenario validator failed to run: {detail[0] if detail else completed.returncode}")
            return
        try:
            report = json.loads(read_text(report_path))
        except Exception as exc:  # pragma: no cover - defensive package gate
            result.fail(f"activation scenario report could not be read: {exc}")
            return
    if report.get("status") != "pass":
        for error in report.get("errors", []):
            result.fail(f"activation scenario gate failed: {error}")
    metrics = report.get("metrics", {})
    if metrics.get("activation_accuracy") != 1.0 or metrics.get("mode_accuracy") != 1.0:
        result.fail(f"activation scenario metrics below 1.0: {metrics}")
    if metrics.get("measurement_kind") != "deterministic_static_oracle":
        result.fail(f"activation scenario measurement kind is not explicit: {metrics}")

def validate_evidence_controls(root: Path, result: ValidationResult) -> None:
    script_path = root / "scripts" / "validate_evidence_contract.py"
    text = read_text(script_path)
    if "does not prove implementation correctness" not in text:
        result.fail("validate_evidence_contract.py must state the limits of deterministic evidence validation")
    reference_text = read_text(root / "references" / "evidence-contract.md")
    required_terms = ("Evidence Classes", "Required Traceability", "Runtime Evidence Boundary", "Mechanical Validation")
    for term in required_terms:
        if term not in reference_text:
            result.fail(f"references/evidence-contract.md missing required section: {term}")

def validate_planning_template_boundaries(root: Path, result: ValidationResult) -> None:
    notes_template = root / "assets" / "templates" / "notes.md.template"
    text = read_text(notes_template)
    forbidden = (
        "## Execution Log",
        "planning or execution",
        "during planning or execution",
    )
    for term in forbidden:
        if term in text:
            result.fail(f"notes.md.template must remain planning-only and must not contain `{term}`")

def compile_scripts(root: Path, result: ValidationResult) -> None:
    for path in sorted((root / "scripts").glob("*.py")):
        try:
            source = read_text(path)
            compile(source, str(path), "exec")
            result.compiled_scripts += 1
        except SyntaxError as exc:
            result.fail(f"python syntax validation failed for {path.relative_to(root).as_posix()}: {exc}")


def validate_no_caches(root: Path, result: ValidationResult) -> None:
    forbidden = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules", ".venv", "venv"}
    for path in root.rglob("*"):
        if path.name in forbidden:
            result.fail(f"forbidden generated directory present: {path.relative_to(root).as_posix()}")


def run(root: Path) -> ValidationResult:
    result = ValidationResult()
    if not root.exists() or not root.is_dir():
        result.fail(f"target is not a directory: {root}")
        return result
    if not (root / "SKILL.md").is_file():
        result.fail("missing SKILL.md")
        return result
    validate_frontmatter(root, result)
    validate_required_paths(root, result)
    validate_skill_links(root, result)
    validate_placeholders(root, result)
    validate_agents(root, result)
    validate_scenarios(root, result)
    validate_activation_metrics(root, result)
    validate_evidence_controls(root, result)
    validate_planning_template_boundaries(root, result)
    compile_scripts(root, result)
    validate_no_caches(root, result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate MAGO skill package integrity before packaging.")
    parser.add_argument("target", nargs="?", default=str(Path(__file__).resolve().parents[1]), help="MAGO skill root. Defaults to this script's skill root.")
    parser.add_argument("--json-output", help="Optional path to write a JSON validation report.")
    args = parser.parse_args(argv)

    target = Path(args.target).resolve()
    result = run(target)
    payload: dict[str, Any] = asdict(result)
    payload["target"] = str(target)

    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {out}")

    print(f"status: {result.status}")
    print(f"checked_files: {result.checked_files}")
    print(f"compiled_scripts: {result.compiled_scripts}")
    for warning in result.warnings:
        print(f"warning: {warning}")
    for error in result.errors:
        print(f"error: {error}")
    return 0 if result.status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
