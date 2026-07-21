#!/usr/bin/env python3
"""Validate all nomia golden examples with the canonical local validators."""

from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import json
import sys
sys.dont_write_bytecode = True
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass
class CommandSpec:
    name: str
    module: str
    args: list[str]
    allow_warnings: bool = False

    def as_command(self, skill_root: Path) -> list[str]:
        return [sys.executable, "-S", str(skill_root / "scripts" / f"{self.module}.py"), *self.args]


@dataclass
class CommandResult:
    name: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def status(self) -> str:
        return "pass" if self.returncode == 0 else "fail"


@dataclass
class ValidationResult:
    target: str
    status: str
    commands: list[CommandResult]


def ensure_import_paths(skill_root: Path) -> None:
    scripts = str(skill_root / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    venv_site = Path(sys.executable).resolve().parents[1] / "lib" / version / "site-packages"
    if venv_site.exists() and str(venv_site) not in sys.path:
        sys.path.append(str(venv_site))


def specs(skill_root: Path) -> list[CommandSpec]:
    golden = skill_root / "examples" / "golden"
    return [
        CommandSpec("golden-01-ops", "validate_ops", [str(golden / "01-delivery-intake-github-issue" / "ops.yaml")], allow_warnings=True),
        CommandSpec("golden-02-ops", "validate_ops", [str(golden / "02-delivery-triage-stakeholders" / "ops.yaml")]),
        CommandSpec("golden-03-ops", "validate_ops", [str(golden / "03-replanned-demand-preserved-history" / "ops.yaml")]),
        CommandSpec(
            "golden-04-portfolio",
            "validate_portfolio",
            [
                "--portfolio-yaml",
                str(golden / "04-portfolio-multiple-specs" / "portfolio.yaml"),
                "--portfolio-md",
                str(golden / "04-portfolio-multiple-specs" / "portfolio.md"),
                "--as-of",
                "2026-04-24",
            ],
        ),
        CommandSpec(
            "golden-05-roadmap",
            "validate_roadmap",
            [
                "--roadmap",
                str(golden / "05-roadmap-large-initiative" / "roadmap.yaml"),
                "--feature-map",
                str(golden / "05-roadmap-large-initiative" / "feature-map.yaml"),
            ],
        ),
        CommandSpec("golden-05-governance-decision", "validate_artifact", [str(golden / "05-roadmap-large-initiative" / "governance-decisions.md")]),
        CommandSpec(
            "golden-06-roadmap",
            "validate_roadmap",
            [
                "--roadmap",
                str(golden / "06-roadmap-to-spec-handoff-mago" / "roadmap.yaml"),
                "--feature-map",
                str(golden / "06-roadmap-to-spec-handoff-mago" / "feature-map.yaml"),
            ],
        ),
        CommandSpec(
            "golden-06-contracts",
            "validate_contracts",
            [
                "--roadmap",
                str(golden / "06-roadmap-to-spec-handoff-mago" / "roadmap.yaml"),
                "--feature-map",
                str(golden / "06-roadmap-to-spec-handoff-mago" / "feature-map.yaml"),
            ],
        ),
        CommandSpec(
            "golden-07-execution-contracts",
            "validate_contracts",
            [
                "--feature-map",
                str(golden / "06-roadmap-to-spec-handoff-mago" / "feature-map.yaml"),
                "--execution-evidence",
                str(golden / "07-feature-report-after-delivery" / "input-magia-execution-evidence.yaml"),
            ],
        ),
        CommandSpec(
            "golden-07-feature-report",
            "validate_reporting",
            [
                "--mode",
                "feature-report",
                "--feature-report",
                str(golden / "07-feature-report-after-delivery" / "feature-report.md"),
                "--internal-notes",
                str(golden / "07-feature-report-after-delivery" / "internal-notes.md"),
            ],
        ),
        CommandSpec(
            "golden-08-release-notes",
            "validate_reporting",
            [
                "--mode",
                "release-notes",
                "--release-notes",
                str(golden / "08-release-notes-stakeholders" / "release-notes.md"),
                "--internal-notes",
                str(golden / "08-release-notes-stakeholders" / "internal-notes.md"),
            ],
        ),
        CommandSpec("golden-09-rfc", "validate_artifact", [str(golden / "09-rfc-proposal-roadmap-handoff" / "rfc-proposals.md")]),
        CommandSpec("golden-10-governance-decision", "validate_artifact", [str(golden / "10-governance-decision-roadmap-decision" / "governance-decisions.md")]),
        CommandSpec("golden-11-adapted-ops", "validate_ops", [str(golden / "11-governance-adapt-legacy" / "ops.yaml"), "--require-canonical"]),
        CommandSpec("golden-12-human-artifact", "validate_human_artifacts", [str(golden / "12-canonical-projection-metadata" / "status.md")]),
        CommandSpec("golden-12-projection-metadata", "validate_projection_metadata", [str(golden / "12-canonical-projection-metadata" / "status.md")]),
    ]


def run_spec(spec: CommandSpec, skill_root: Path) -> CommandResult:
    ensure_import_paths(skill_root)
    module = importlib.import_module(spec.module)
    main_func: Callable[[list[str]], int] = getattr(module, "main")
    out = io.StringIO()
    err = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main_func(spec.args)
    except SystemExit as exc:
        code = int(exc.code) if isinstance(exc.code, int) else 1
    except Exception as exc:  # pragma: no cover - defensive CLI guard
        code = 1
        err.write(f"{type(exc).__name__}: {exc}\n")
    stdout = out.getvalue().strip()
    stderr = err.getvalue().strip()
    if code == 0 and not spec.allow_warnings and any(line.startswith("WARNING:") for line in stdout.splitlines()):
        code = 1
        stderr = (stderr + "\n" if stderr else "") + "unexpected warning output is not allowlisted"
    return CommandResult(
        name=spec.name,
        command=spec.as_command(skill_root),
        returncode=code,
        stdout=stdout,
        stderr=stderr,
    )


def validate(skill_root: Path) -> ValidationResult:
    root = skill_root.resolve()
    commands = [run_spec(spec, root) for spec in specs(root)]
    status = "pass" if all(item.returncode == 0 for item in commands) else "fail"
    return ValidationResult(target=str(root), status=status, commands=commands)


def to_jsonable(result: ValidationResult) -> dict[str, Any]:
    return {
        "target": result.target,
        "status": result.status,
        "commands": [asdict(command) | {"status": command.status} for command in result.commands],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate every nomia golden example with bundled validators.")
    parser.add_argument("--skill-root", default=str(Path(__file__).resolve().parents[1]), help="Path to the nomia skill root.")
    parser.add_argument("--json-output", help="Optional path for machine-readable validation output.")
    args = parser.parse_args(argv)

    result = validate(Path(args.skill_root))
    payload = to_jsonable(result)
    if args.json_output:
        output = Path(args.json_output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"status: {result.status}")
    print(f"target: {result.target}")
    for command in result.commands:
        print(f"{command.status}: {command.name}")
        if command.stdout:
            for line in command.stdout.splitlines():
                print(f"  stdout: {line}")
        if command.stderr:
            for line in command.stderr.splitlines():
                print(f"  stderr: {line}")
    return 0 if result.status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
