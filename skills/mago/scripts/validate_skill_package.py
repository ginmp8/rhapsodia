#!/usr/bin/env python3
"""Validate MAGO skill package integrity before distribution."""

from __future__ import annotations

import argparse
import contextlib
import inspect
import io
import json
import os
import re
import runpy
import signal
import subprocess
import sys
import tempfile
import unittest
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Package validation and nested test subprocesses must not contaminate the target.
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True

TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".template"}
REQUIRED_FRONTMATTER_KEYS = ("name", "description")
REQUIRED_DIRS = ("agents", "assets/templates", "references", "references/modes", "scripts")
REQUIRED_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/canonical-paths.md",
    "references/common-planning.md",
    "references/concurrent-planning.md",
    "references/evidence-contract.md",
    "references/operating-rules.md",
    "references/validation-and-packaging.md",
    "references/activation-routing.md",
    "references/mutation-transaction-and-resume.md",
    "references/security-risk-contract.md",
    "references/installation-and-release.md",
    "references/priority-contract.md",
    "references/priority-contract.json",
    "references/ecosystem-handoff-contract.md",
    "references/ecosystem-handoff-contract.json",
    "references/ecosystem-compatibility.json",
    "references/ecosystem-compatibility.md",
    "VERSION",
    "release.json",
    "requirements.txt",
    "CHANGELOG.md",
    "scripts/validate_activation_scenarios.py",
    "scripts/validate_artifact.py",
    "scripts/validate_boundary.py",
    "scripts/validate_evidence_contract.py",
    "scripts/validate_package.py",
    "scripts/validate_triggered_artifact.py",
    "scripts/validate_security_risk.py",
    "scripts/validate_plan_quality.py",
    "scripts/validate_clarification_readiness.py",
    "scripts/mutation_transaction.py",
    "scripts/sdd_adapter.py",
    "scripts/validate_release_metadata.py",
    "scripts/validate_priority_contract.py",
    "scripts/validate_contract_semantics.py",
    "scripts/ecosystem_handoff.py",
    "scripts/validate_ecosystem_handoff_contract.py",
    "scripts/validate_ecosystem_compatibility.py",
    "scripts/run_ecosystem_flow_harness.py",
    "scripts/validate_runtime_dependencies.py",
    "scripts/validate_repo_board.py",
    "scripts/validate_concurrent_board.py",
    "scripts/validate_planning_execution_handoff.py",
    "scripts/validate_generated_view_contract.py",
    "scripts/create_planning_identity.py",
    "scripts/render_registry_views.py",
    "scripts/concurrent_model.py",
    "scripts/validate_skill_package.py",
    "scripts/write_artifact_scaffold.py",
    "assets/templates/cycle.yaml.template",
    "assets/templates/spec-registry-entry.yaml.template",
    "assets/templates/manifest.yaml.template",
    "assets/templates/tasks.md.template",
    "examples/activation-scenarios.json",
    "evidence/sdd-evidence-scenarios.json",
    "evidence/lifecycle-contract-scenarios.json",
    "scripts/run_sdd_evidence_harness.py",
    "scripts/validate_distribution.py",
    "scripts/run_test_suite.py",
    "scripts/merge_test_reports.py",
    "scripts/merge_evidence_reports.py",
    "tests/test_concurrency_model.py",
    "tests/test_package_validation.py",
    "tests/test_priority_contract.py",
    "tests/test_contract_semantics.py",
    "tests/test_ecosystem_handoff.py",
    "tests/test_ecosystem_compatibility.py",
    "tests/test_distribution_validation_v3.py",
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
    "complexity-reduction",
    "reconcile",
)
PLACEHOLDER_PATTERNS = (
    re.compile(r"\[" + "TO" + "DO", re.IGNORECASE),
    re.compile(r"\b" + "TO" + "DO" + r"\s*:", re.IGNORECASE),
    re.compile("FIX" + "ME", re.IGNORECASE),
    re.compile("replace" + " with actual", re.IGNORECASE),
    re.compile("this is a " + "placeholder", re.IGNORECASE),
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
    executed_tests: int = 0

    def fail(self, message: str) -> None:
        self.status = "fail"
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_gate_command(root: Path, command: list[str], label: str, result: ValidationResult, timeout: int = 60) -> bool:
    # File-backed output avoids nested validator/test subprocesses blocking on full pipes.
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as stdout_file, tempfile.TemporaryFile(
        mode="w+", encoding="utf-8"
    ) as stderr_file:
        process = subprocess.Popen(
            command,
            cwd=str(root),
            text=True,
            stdout=stdout_file,
            stderr=stderr_file,
            start_new_session=True,
        )
        try:
            return_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            result.fail(f"{label} gate timed out after {timeout}s")
            return False
        stdout_file.seek(0)
        stderr_file.seek(0)
        stdout = stdout_file.read()
        stderr = stderr_file.read()
    if return_code != 0:
        detail = (stderr or stdout).strip()
        result.fail(f"{label} gate failed: {detail[-1600:]}")
        return False
    return True




def run_python_gate(root: Path, script_path: Path, args: list[str], label: str, result: ValidationResult) -> bool:
    stdout = io.StringIO()
    stderr = io.StringIO()
    old_argv = sys.argv[:]
    added_path = str(script_path.parent)
    sys.path.insert(0, added_path)
    try:
        sys.argv = [str(script_path), *args]
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            namespace = runpy.run_path(str(script_path), run_name=f"__mago_gate_{script_path.stem}__")
            main_fn = namespace.get("main")
            if not callable(main_fn):
                result.fail(f"{label} gate has no callable main()")
                return False
            return_code = main_fn(args) if len(inspect.signature(main_fn).parameters) else main_fn()
    except SystemExit as exc:
        return_code = exc.code if isinstance(exc.code, int) else 1
    except Exception as exc:
        result.fail(f"{label} gate raised {type(exc).__name__}: {exc}")
        return False
    finally:
        sys.argv = old_argv
        if sys.path and sys.path[0] == added_path:
            sys.path.pop(0)
    if return_code not in (None, 0):
        detail = (stderr.getvalue() or stdout.getvalue()).strip()
        result.fail(f"{label} gate failed: {detail[-1600:]}")
        return False
    return True


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
        if not run_python_gate(
            root, script_path, [str(root), "--json-output", str(report_path)],
            "activation scenario validator", result,
        ):
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

def validate_goldens(root: Path, result: ValidationResult) -> None:
    scripts = root / "scripts"
    golden_root = root / "examples" / "golden"
    run_python_gate(
        root, scripts / "validate_technical_design.py",
        [str(golden_root / "governed-traceability" / "technical-design.md")],
        "governed technical-design golden", result,
    )
    run_python_gate(
        root, scripts / "validate_change_delta.py",
        [str(golden_root / "change-delta" / "change-delta.md")],
        "change-delta golden", result,
    )
    run_python_gate(
        root, scripts / "validate_sdd_adapter_report.py",
        [str(golden_root / "interoperability" / "adapter-report.json.fixture")],
        "adapter-report golden", result,
    )
    run_python_gate(
        root, scripts / "validate_security_risk.py",
        [str(golden_root / "security-v2" / "security-and-risk-considerations.md"), "--require-v2"],
        "security v2 relational golden", result,
    )
    run_python_gate(
        root, scripts / "validate_plan_quality.py",
        [str(golden_root / "governed-quality")],
        "governed plan-quality golden", result,
    )
    run_python_gate(
        root, scripts / "validate_plan_quality.py",
        [str(golden_root / "governed-quality-v2"), "--require-v2"],
        "governed plan-quality v2 golden", result,
    )
    run_python_gate(
        root, scripts / "validate_clarification_readiness.py",
        [str(golden_root / "clarification-v2" / "notes.md"), "--require-v2", "--handoff"],
        "clarification readiness v2 golden", result,
    )
    with tempfile.TemporaryDirectory(prefix="mago-adapter-roundtrip-") as adapter_tmp:
        adapter_root = Path(adapter_tmp)
        for target_format, target_version in (
            ("spec-kit", "spec-kit-file-contract-1"),
            ("openspec", "openspec-file-contract-1"),
            ("kiro", "kiro-file-contract-1"),
        ):
            output = adapter_root / target_format
            report = adapter_root / f"{target_format}-report.json"
            if run_python_gate(
                root, scripts / "sdd_adapter.py",
                [
                    "round-trip",
                    "--package", str(golden_root / "interoperability" / "package"),
                    "--format", target_format,
                    "--source-version", "mago-2026.07",
                    "--target-version", target_version,
                    "--output", str(output),
                    "--report", str(report),
                ],
                f"{target_format} executable round trip", result,
            ):
                run_python_gate(
                    root, scripts / "validate_sdd_adapter_report.py",
                    [str(report)],
                    f"{target_format} round-trip report", result,
                )
    with tempfile.TemporaryDirectory(prefix="mago-golden-") as tmp:
        projection = Path(tmp) / "traceability.json"
        if run_python_gate(
            root, scripts / "render_traceability.py",
            [str(golden_root / "governed-traceability"), "--output", str(projection)],
            "traceability golden render", result,
        ):
            run_python_gate(
                root, scripts / "validate_traceability.py",
                [str(projection), "--profile", "governed"],
                "traceability golden validation", result,
            )
        reconciliation = Path(tmp) / "planning-reconciliation.md"
        if run_python_gate(
            root, scripts / "reconcile_planning.py",
            ["--plan", str(golden_root / "reconciliation" / "plan.json.fixture"),
             "--evidence", str(golden_root / "reconciliation" / "magia-evidence.json.fixture"),
             "--output", str(reconciliation)],
            "reconciliation golden", result,
        ) and not reconciliation.is_file():
            result.fail("reconciliation golden did not produce its declared output")

def validate_release_controls(root: Path, result: ValidationResult) -> None:
    run_python_gate(
        root, root / "scripts" / "validate_runtime_dependencies.py", [str(root)],
        "runtime dependencies", result,
    )
    run_python_gate(
        root, root / "scripts" / "validate_release_metadata.py", [str(root)],
        "release metadata", result,
    )


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


def validate_semantic_contracts(root: Path, result: ValidationResult) -> None:
    run_python_gate(
        root, root / "scripts" / "validate_priority_contract.py", ["--target", str(root)],
        "ecosystem priority contract", result,
    )
    run_python_gate(
        root, root / "scripts" / "validate_contract_semantics.py", ["--target", str(root)],
        "ecosystem contract semantics", result,
    )
    run_python_gate(root, root / "scripts" / "validate_ecosystem_handoff_contract.py", ["--target", str(root)], "ecosystem handoff contract", result)
    run_python_gate(root, root / "scripts" / "validate_ecosystem_compatibility.py", ["--target", str(root)], "ecosystem compatibility", result)
    # Handoff and generated-view contracts are exercised by the full unittest suite.
    # Run the boundary contract directly because it is not duplicated by that suite.
    run_python_gate(
        root, root / "scripts" / "validate_boundary.py", [str(root)],
        "boundary contract", result,
    )


def compile_scripts(root: Path, result: ValidationResult) -> None:
    for path in sorted((root / "scripts").glob("*.py")):
        try:
            source = read_text(path)
            compile(source, str(path), "exec")
            result.compiled_scripts += 1
        except SyntaxError as exc:
            result.fail(f"python syntax validation failed for {path.relative_to(root).as_posix()}: {exc}")


def validate_concurrency_tests(root: Path, result: ValidationResult, test_report: Path | None = None) -> None:
    # A hash-bound merged report allows bounded test shards without weakening coverage.
    if test_report is not None:
        try:
            report = json.loads(test_report.read_text(encoding="utf-8"))
        except Exception as exc:
            result.fail(f"merged test suite report could not be read: {exc}")
            return
        if report.get("kind") != "mago-merged-test-report" or report.get("status") != "pass":
            result.fail(f"merged test suite report is not a passing Mago report: {report.get('errors', [])}")
            return
        from merge_test_reports import current_manifest
        _, expected_digest = current_manifest(root)
        if report.get("suite_digest") != expected_digest:
            result.fail("merged test suite report does not match current test-file hashes")
            return
        result.executed_tests = int(report.get("test_count", 0))
        if result.executed_tests < 69:
            result.fail(f"merged test suite report contains only {result.executed_tests} tests")
        return
    with tempfile.TemporaryDirectory(prefix="mago-tests-") as tmp:
        report_path = Path(tmp) / "test-suite.json"
        command = [sys.executable, "-B", str(root / "scripts" / "run_test_suite.py"),
                   "--target", str(root), "--jobs", "1", "--timeout", "180",
                   "--minimum-tests", "69", "--output", str(report_path)]
        if not run_gate_command(root, command, "isolated test suite", result, timeout=600):
            return
        report = json.loads(report_path.read_text(encoding="utf-8"))
        result.executed_tests = int(report.get("test_count", 0))


def validate_no_caches(root: Path, result: ValidationResult) -> None:
    forbidden = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules", ".venv", "venv"}
    for path in root.rglob("*"):
        if path.name in forbidden:
            result.fail(f"forbidden generated directory present: {path.relative_to(root).as_posix()}")


def run(root: Path, test_report: Path | None = None) -> ValidationResult:
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
    compile_scripts(root, result)
    validate_activation_metrics(root, result)
    validate_goldens(root, result)
    validate_evidence_controls(root, result)
    validate_release_controls(root, result)
    validate_planning_template_boundaries(root, result)
    validate_semantic_contracts(root, result)
    # Tests execute last because their nested process probes can contaminate later
    # subprocess orchestration on some runtimes even after all test cases pass.
    validate_concurrency_tests(root, result, test_report)
    validate_no_caches(root, result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate MAGO skill package integrity before packaging.")
    parser.add_argument("target", nargs="?", default=str(Path(__file__).resolve().parents[1]), help="MAGO skill root. Defaults to this script's skill root.")
    parser.add_argument("--json-output", help="Optional path to write a JSON validation report.")
    parser.add_argument("--test-report", help="Optional hash-bound merged test report from merge_test_reports.py.")
    args = parser.parse_args(argv)

    target = Path(args.target).resolve()
    result = run(target, Path(args.test_report).resolve() if args.test_report else None)
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
    print(f"executed_tests: {result.executed_tests}")
    for warning in result.warnings:
        print(f"warning: {warning}")
    for error in result.errors:
        print(f"error: {error}")
    return 0 if result.status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
