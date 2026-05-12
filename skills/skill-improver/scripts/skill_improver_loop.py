#!/usr/bin/env python3
"""
Hypothesis-driven skill improvement loop.

This runner orchestrates a bounded Codex experiment against a target skill folder:
1. establish a baseline with a frozen evaluator
2. load or discover a falsifiable hypothesis when a backlog is supplied
3. ask Codex to apply a minimal patch
4. re-run the same evaluator
5. run the structural change gate when configured
6. keep the patch only if the metric improves, required gates pass, and the change gate allows acceptance
7. otherwise revert the patch and record the rejected hypothesis

Use yolo only inside an externally hardened disposable environment.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import json
import os
import random
import re
import shlex
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import Any, Optional


DEFAULT_SKILL_BENCHMARK_SCRIPT = Path("./skills/skill-benchmark/scripts/generate_benchmark_report.js")
SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = SKILL_ROOT / "assets" / "templates"
RUN_REPORT_TEMPLATE = "improvement-run-report.md.template"
PATCH_DECISION_TEMPLATE = "patch-decision-record.md.template"

BLOCKER_GATES = {
    "valid skill.md exists",
    "frontmatter has name and description",
    "expected output is clear",
    "no contradictory instructions",
}

HYPOTHESES = [
    {
        "id": "H001",
        "name": "Improve frontmatter trigger specificity",
        "goal": "Improve activation precision and recall by making the description concrete, scoped, and action-oriented.",
        "constraints": [
            "Prefer changing only SKILL.md frontmatter description and a small supporting body note if needed.",
            "Do not exceed 1024 characters in the description.",
            "Include concrete triggers and exclusion boundaries.",
        ],
    },
    {
        "id": "H002",
        "name": "Add negative activation boundaries",
        "goal": "Reduce false activations by clarifying when the skill must not be used.",
        "constraints": [
            "Add non-goals or delegation rules.",
            "Do not weaken positive triggers.",
        ],
    },
    {
        "id": "H010",
        "name": "Add deterministic workflow order",
        "goal": "Improve output conformance by making the workflow sequential and checkable.",
        "constraints": [
            "Add numbered steps only where the current workflow is ambiguous.",
            "Keep SKILL.md compact; move details to references if long.",
        ],
    },
    {
        "id": "H011",
        "name": "Add mode selection matrix",
        "goal": "Improve ambiguous prompt handling for multi-mode skills.",
        "constraints": [
            "Add a compact intent-to-mode table.",
            "Include required inputs, outputs, and validators when applicable.",
        ],
    },
    {
        "id": "H012",
        "name": "Add severity-gated review loop",
        "goal": "Improve reviewer-driven patches by classifying findings as critical, major, or minor before mutation.",
        "constraints": [
            "Fix critical and major findings before cosmetic polish.",
            "Evaluate minor findings for functional value and false-positive risk before editing.",
            "Do not combine unrelated severity classes in one patch unless the fix is inseparable.",
        ],
    },
    {
        "id": "H020",
        "name": "Add output contract",
        "goal": "Improve consistency by defining required final response sections or artifact structure.",
        "constraints": [
            "Add a concise output contract.",
            "Avoid over-constraining tasks that need flexibility.",
        ],
    },
    {
        "id": "H021",
        "name": "Add minimal examples",
        "goal": "Improve quality by adding positive, negative, and ambiguous examples.",
        "constraints": [
            "Use short examples only.",
            "Do not add large transcripts or generic examples.",
        ],
    },
    {
        "id": "H030",
        "name": "Add validation checklist",
        "goal": "Improve reliability by requiring gates before final output.",
        "constraints": [
            "Add a closing checklist with pass/fail gates.",
            "Prefer existing scripts if present.",
        ],
    },
    {
        "id": "H040",
        "name": "Improve context efficiency",
        "goal": "Reduce context load by moving verbose details into references and keeping SKILL.md as control plane.",
        "constraints": [
            "Do not remove important instructions.",
            "Ensure SKILL.md links to moved references.",
        ],
    },
    {
        "id": "H050",
        "name": "Add safety and rollback boundaries",
        "goal": "Improve robustness on unsafe, out-of-scope, incomplete, or conflicting requests.",
        "constraints": [
            "Preserve unknown facts instead of inventing values.",
            "Add stop conditions when prerequisites are missing.",
        ],
    },
    {
        "id": "H052",
        "name": "Add graceful loop cancellation",
        "goal": "Improve long-running loop control by adding an explicit stop-file path that preserves accepted changes.",
        "constraints": [
            "Check cancellation between candidate iterations, not by weakening evaluation gates.",
            "Document how accepted, rejected, and in-flight candidates are handled.",
            "Do not delete accepted target changes during cancellation.",
        ],
    },
]


@dataclasses.dataclass
class EvalResult:
    score: float
    raw: str
    status: str = "unknown"
    gates: dict[str, str] = dataclasses.field(default_factory=dict)
    data: dict[str, Any] = dataclasses.field(default_factory=dict)
    report_path: Optional[str] = None
    evaluator_hash: Optional[str] = None


@dataclasses.dataclass
class IterationResult:
    iteration: int
    hypothesis_id: str
    hypothesis_name: str
    before: float
    after: Optional[float]
    accepted: bool
    reason: str
    changed_files: list[str]
    change_gate_status: str = "not-run"
    change_gate_notes: str = ""


def run(cmd: str | list[str], cwd: Path, timeout: int | None = None, check: bool = False) -> subprocess.CompletedProcess[str]:
    if isinstance(cmd, str):
        shell = True
        display = cmd
    else:
        shell = False
        display = " ".join(shlex.quote(x) for x in cmd)
    print(f"[run] cwd={cwd} cmd={display}", flush=True)
    completed = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=shell,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    if check and completed.returncode != 0:
        raise RuntimeError(f"command failed ({completed.returncode}): {display}\n{completed.stdout}")
    return completed


def find_git_root(path: Path) -> Path:
    completed = run(["git", "rev-parse", "--show-toplevel"], cwd=path, check=True)
    return Path(completed.stdout.strip()).resolve()


def status_path_from_porcelain(line: str) -> str:
    if len(line) < 4:
        return ""
    # Handles normal porcelain entries. Renames are rare for this flow; keep the displayed path.
    return line[3:].strip()


def is_ignored_status_path(rel: str, git_root: Path, ignore_paths: list[Path]) -> bool:
    if not rel:
        return True
    absolute = (git_root / rel).resolve()
    for raw in ignore_paths:
        ignored = raw if raw.is_absolute() else (git_root / raw).resolve()
        if absolute == ignored or str(absolute).startswith(str(ignored) + os.sep):
            return True
    return False


def require_clean_git(git_root: Path, ignore_paths: list[Path] | None = None) -> None:
    ignore_paths = ignore_paths or []
    out = run(["git", "status", "--porcelain"], cwd=git_root, check=True).stdout
    dirty_lines = []
    for line in out.splitlines():
        rel = status_path_from_porcelain(line)
        if not is_ignored_status_path(rel, git_root, ignore_paths):
            dirty_lines.append(line)
    if dirty_lines:
        raise RuntimeError(
            "git working tree is not clean. commit/stash changes before running.\n" + "\n".join(dirty_lines)
        )


def changed_files(git_root: Path, ignore_paths: list[Path] | None = None) -> list[str]:
    ignore_paths = ignore_paths or []
    out = run(["git", "status", "--porcelain"], cwd=git_root, check=True).stdout
    files: list[str] = []
    for line in out.splitlines():
        rel = status_path_from_porcelain(line)
        if rel and not is_ignored_status_path(rel, git_root, ignore_paths):
            files.append(rel)
    return files


def resolve_under(root: Path, value: Path) -> Path:
    return value if value.is_absolute() else (root / value).resolve()


def assert_changed_files_in_scope(files: list[str], git_root: Path, target: Path, extra_allowed: list[Path]) -> None:
    target = target.resolve()
    allowed = [target] + [resolve_under(git_root, p) for p in extra_allowed]
    violations: list[str] = []
    for rel in files:
        absolute = (git_root / rel).resolve()
        if not any(absolute == a or str(absolute).startswith(str(a) + os.sep) for a in allowed):
            violations.append(rel)
    if violations:
        raise RuntimeError("agent modified files outside allowed scope: " + ", ".join(violations))


def assert_no_blocked_paths_changed(files: list[str], git_root: Path, blocked_paths: list[Path]) -> None:
    if not blocked_paths:
        return
    blocked = [resolve_under(git_root, p) for p in blocked_paths]
    violations: list[str] = []
    for rel in files:
        absolute = (git_root / rel).resolve()
        if any(absolute == b or str(absolute).startswith(str(b) + os.sep) for b in blocked):
            violations.append(rel)
    if violations:
        raise RuntimeError("agent modified blocked evaluator or fixture paths: " + ", ".join(violations))


def iter_files_for_hash(path: Path) -> list[Path]:
    if not path.exists():
        return []
    if path.is_file():
        return [path]
    out: list[Path] = []
    for file_path in path.rglob("*"):
        if file_path.is_file() and ".git" not in file_path.parts:
            out.append(file_path)
    return sorted(out)


def hash_evaluator_state(args: argparse.Namespace, git_root: Path) -> str:
    hasher = hashlib.sha256()
    hasher.update(f"evaluator={args.evaluator}\n".encode())
    hasher.update(f"direction={args.direction}\n".encode())
    hasher.update(f"min_delta={args.min_delta}\n".encode())
    hasher.update(f"required_gates={sorted(args.required_gate or [])}\n".encode())
    hasher.update(f"enforce_all_gates={args.enforce_all_gates}\n".encode())
    hasher.update(f"enforce_blocker_gates={args.enforce_blocker_gates}\n".encode())
    hasher.update(f"require_status_pass={args.require_status_pass}\n".encode())

    paths: list[Path] = []
    if args.evaluator == "command":
        hasher.update(f"eval_command={args.eval_command}\n".encode())
    else:
        script = args.skill_benchmark_script or DEFAULT_SKILL_BENCHMARK_SCRIPT
        paths.append(script)
        hasher.update(f"skill_benchmark_script={script}\n".encode())
        hasher.update(f"skill_benchmark_out={args.skill_benchmark_out}\n".encode())
        if args.skill_benchmark_results:
            paths.append(args.skill_benchmark_results)
            hasher.update(f"skill_benchmark_results={args.skill_benchmark_results}\n".encode())

    for raw_path in args.benchmark_lock_path or []:
        paths.append(raw_path)

    for raw_path in paths:
        path = raw_path if raw_path.is_absolute() else (git_root / raw_path).resolve()
        hasher.update(f"path={path}\n".encode())
        if not path.exists():
            hasher.update(b"missing\n")
            continue
        for file_path in iter_files_for_hash(path):
            hasher.update(str(file_path.relative_to(path) if path.is_dir() else file_path.name).encode())
            hasher.update(b"\0")
            hasher.update(hashlib.sha256(file_path.read_bytes()).digest())
    return hasher.hexdigest()


def extract_json_objects(text: str) -> list[str]:
    objects: list[str] = []
    stack = 0
    start: Optional[int] = None
    in_string = False
    escape = False
    for i, ch in enumerate(text):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            if stack == 0:
                start = i
            stack += 1
        elif ch == "}":
            if stack:
                stack -= 1
                if stack == 0 and start is not None:
                    objects.append(text[start : i + 1])
                    start = None
    return objects


def normalize_gate_value(value: Any) -> str:
    if isinstance(value, bool):
        return "pass" if value else "fail"
    return str(value or "unknown").strip().lower()


def parse_eval_output(raw: str, score_regex: str | None) -> EvalResult:
    stripped = raw.strip()
    if stripped:
        candidates = [stripped] + extract_json_objects(stripped)
        for candidate in reversed(candidates):
            try:
                data = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict) and "score" in data:
                gates = {
                    str(k): normalize_gate_value(v)
                    for k, v in (data.get("gates") or {}).items()
                }
                return EvalResult(
                    score=float(data["score"]),
                    raw=raw,
                    status=str(data.get("status", "unknown")).strip().lower(),
                    gates=gates,
                    data=data,
                    report_path=data.get("report_path"),
                )
    if score_regex:
        match = re.search(score_regex, raw)
        if not match:
            raise RuntimeError(f"score regex did not match eval output: {score_regex}")
        group = match.group(1) if match.groups() else match.group(0)
        return EvalResult(score=float(group), raw=raw, status="regex")
    raise RuntimeError("eval output must contain JSON with numeric score, or use --score-regex")


def parse_score_from_report(text: str) -> float:
    patterns = [
        r"Overall score:\s*`?([0-9]+(?:\.[0-9]+)?)/100`?",
        r"\| \*\*Total\*\* \| \*\*100\*\* \| \*\*([0-9]+(?:\.[0-9]+)?)\*\*",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return float(match.group(1))
    raise RuntimeError("could not parse skill-benchmark score from report")


def parse_verdict_from_report(text: str) -> str:
    match = re.search(r"Verdict:\s*`?([^`\n]+)`?", text)
    if match:
        return match.group(1).strip().lower()
    verdict_lines = re.findall(r"^`([^`]+)`\s*$", text, flags=re.MULTILINE)
    for value in verdict_lines:
        if value.strip().lower() in {"approve", "approve with reservations", "reject"}:
            return value.strip().lower()
    return "unknown"


def parse_gates_from_report(text: str) -> dict[str, str]:
    gates: dict[str, str] = {}
    in_table = False
    for line in text.splitlines():
        if line.startswith("| Gate | Status | Evidence | Required action |"):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|") or line.startswith("|---"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) < 2:
                continue
            gate, status = cells[0], cells[1]
            if gate and gate.lower() != "gate":
                gates[gate] = normalize_gate_value(status)
    return gates


def evaluate_with_skill_benchmark(args: argparse.Namespace, target: Path, git_root: Path) -> EvalResult:
    script = args.skill_benchmark_script or DEFAULT_SKILL_BENCHMARK_SCRIPT
    script = script if script.is_absolute() else (git_root / script).resolve()
    if not script.exists():
        raise RuntimeError(f"skill-benchmark script not found: {script}")

    state_dir = (git_root / args.state_dir).resolve() if not args.state_dir.is_absolute() else args.state_dir
    out_dir = args.skill_benchmark_out or (state_dir / "skill-benchmark-reports")
    out_dir = out_dir if out_dir.is_absolute() else (git_root / out_dir).resolve()
    cmd = ["node", str(script), "--target", str(target), "--out", str(out_dir), "--force"]
    if args.skill_benchmark_results:
        results = args.skill_benchmark_results if args.skill_benchmark_results.is_absolute() else (git_root / args.skill_benchmark_results).resolve()
        cmd += ["--results", str(results)]

    completed = run(cmd, cwd=git_root, timeout=args.eval_timeout, check=False)
    if completed.returncode != 0 and not args.allow_eval_failure:
        raise RuntimeError(f"skill-benchmark failed with exit code {completed.returncode}\n{completed.stdout}")
    report_path = completed.stdout.strip().splitlines()[-1].strip() if completed.stdout.strip() else ""
    report = Path(report_path)
    if not report.is_absolute():
        report = (git_root / report).resolve()
    if not report.exists():
        raise RuntimeError(f"skill-benchmark report not found: {report}")
    text = report.read_text(encoding="utf-8")
    score = parse_score_from_report(text)
    verdict = parse_verdict_from_report(text)
    gates = parse_gates_from_report(text)
    status = "fail" if verdict == "reject" else "pass" if verdict in {"approve", "approve with reservations"} else "unknown"
    return EvalResult(
        score=score,
        raw=text,
        status=status,
        gates=gates,
        data={"verdict": verdict, "evaluator": "skill-benchmark"},
        report_path=str(report),
    )


def evaluate(args: argparse.Namespace, target: Path, git_root: Path) -> EvalResult:
    evaluator_hash = hash_evaluator_state(args, git_root) if args.freeze_benchmark else None
    if args.evaluator == "skill-benchmark":
        result = evaluate_with_skill_benchmark(args, target, git_root)
    else:
        if not args.eval_command:
            raise RuntimeError("--eval-command is required when --evaluator command is used")
        completed = run(args.eval_command, cwd=target, timeout=args.eval_timeout, check=False)
        if completed.returncode != 0 and not args.allow_eval_failure:
            raise RuntimeError(f"eval command failed with exit code {completed.returncode}\n{completed.stdout}")
        result = parse_eval_output(completed.stdout, args.score_regex)
    result.evaluator_hash = evaluator_hash
    return result


def gate_passes(value: str) -> bool:
    return normalize_gate_value(value) in {"pass", "passed", "ok", "true"}


def result_passes_required_gates(args: argparse.Namespace, result: EvalResult, baseline: EvalResult | None = None) -> tuple[bool, str]:
    status = (result.status or "unknown").lower()
    if status in {"fail", "failed", "error", "blocked", "reject"}:
        return False, f"evaluator status is {result.status}"
    if args.require_status_pass and status != "pass":
        return False, f"evaluator status is {result.status}, expected pass"

    gates = result.gates or {}
    lower_gates = {name.lower(): value for name, value in gates.items()}

    if args.enforce_blocker_gates:
        for gate_name, gate_value in lower_gates.items():
            if gate_name in BLOCKER_GATES and not gate_passes(gate_value):
                return False, f"blocker gate failed: {gate_name}={gate_value}"

    for required in args.required_gate or []:
        required_lower = required.lower()
        if required_lower not in lower_gates:
            return False, f"required gate missing: {required}"
        if not gate_passes(lower_gates[required_lower]):
            return False, f"required gate failed: {required}={lower_gates[required_lower]}"

    if args.enforce_all_gates:
        failed = [name for name, value in gates.items() if not gate_passes(value)]
        if failed:
            return False, "failed gates: " + ", ".join(failed)

    if args.enforce_no_new_gate_failures and baseline and baseline.gates:
        baseline_failed = {name.lower() for name, value in baseline.gates.items() if not gate_passes(value)}
        result_failed = {name.lower() for name, value in gates.items() if not gate_passes(value)}
        new_failures = sorted(result_failed - baseline_failed)
        if new_failures:
            return False, "new gate failures: " + ", ".join(new_failures)

    return True, "required gates passed"


def normalize_change_gate_status(value: Any) -> str:
    status = str(value or "unknown").strip().lower()
    aliases = {
        "ok": "pass",
        "passed": "pass",
        "warn": "pass-with-warnings",
        "warning": "pass-with-warnings",
        "warnings": "pass-with-warnings",
        "failed": "fail",
        "error": "fail",
        "blocked": "fail",
        "reject": "fail",
    }
    return aliases.get(status, status)


@dataclasses.dataclass
class ChangeGateResult:
    status: str = "not-run"
    raw: str = ""
    data: dict[str, Any] = dataclasses.field(default_factory=dict)
    notes: str = ""


def jsonable_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def summarize_change_gate(data: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ["blocking_regressions", "material_concerns", "accepted_tradeoffs", "notes"]:
        values = jsonable_list(data.get(key))
        if values:
            parts.append(f"{key}=" + "; ".join(values))
    return " | ".join(parts) if parts else "no gate notes"


def run_change_gate(args: argparse.Namespace, target: Path, git_root: Path, files: list[str], hypothesis: dict[str, Any], before: EvalResult, after: EvalResult) -> ChangeGateResult:
    if args.change_gate_policy == "disabled" and not args.change_gate_command:
        return ChangeGateResult(status="not-run", notes="change gate disabled")
    if not args.change_gate_command:
        if args.change_gate_policy == "required":
            return ChangeGateResult(status="fail", notes="change gate policy is required but --change-gate-command was not provided")
        return ChangeGateResult(status="not-run", notes="change gate command not provided")

    env = os.environ.copy()
    env.update(
        {
            "TARGET_SKILL_PATH": str(target),
            "CHANGED_FILES_JSON": json.dumps(files),
            "HYPOTHESIS_ID": str(hypothesis.get("id", "")),
            "HYPOTHESIS_NAME": str(hypothesis.get("name", "")),
            "BEFORE_SCORE": str(before.score),
            "AFTER_SCORE": str(after.score),
            "EVALUATOR_STATUS": str(after.status),
            "EVALUATOR_GATES_JSON": json.dumps(after.gates or {}, sort_keys=True),
        }
    )
    print(f"[change-gate] policy={args.change_gate_policy} cmd={args.change_gate_command}", flush=True)
    completed = subprocess.run(
        args.change_gate_command,
        cwd=str(git_root),
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=args.change_gate_timeout,
        env=env,
    )
    raw = completed.stdout or ""
    if completed.returncode != 0:
        return ChangeGateResult(status="fail", raw=raw, notes=f"change gate command failed with exit code {completed.returncode}")

    data: dict[str, Any] = {}
    candidates = [raw.strip()] + extract_json_objects(raw)
    for candidate in reversed([c for c in candidates if c]):
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            data = parsed
            break
    if not data:
        return ChangeGateResult(status="fail", raw=raw, notes="change gate output did not contain a JSON object")

    status = normalize_change_gate_status(data.get("status"))
    notes = summarize_change_gate(data)
    return ChangeGateResult(status=status, raw=raw, data=data, notes=notes)


def change_gate_allows_acceptance(args: argparse.Namespace, result: ChangeGateResult) -> tuple[bool, str]:
    status = normalize_change_gate_status(result.status)
    if args.change_gate_policy == "disabled":
        return True, "change gate disabled"
    if status == "pass":
        return True, "change gate passed"
    if status == "pass-with-warnings":
        return True, "change gate passed with warnings: " + (result.notes or "warnings recorded")
    if args.change_gate_policy == "advisory":
        return True, "change gate advisory only: " + (result.notes or status)
    return False, "change gate failed: " + (result.notes or status)


def is_improved(before: float, after: float, direction: str, min_delta: float) -> bool:
    if direction == "higher-is-better":
        return after >= before + min_delta
    if direction == "lower-is-better":
        return after <= before - min_delta
    raise ValueError(f"invalid direction: {direction}")



def normalize_hypothesis(raw: dict[str, Any], index: int) -> dict[str, Any]:
    """Normalize a skill-hypothesis-discovery entry into runner fields."""
    hid = str(raw.get("id") or raw.get("hypothesis_id") or f"HB{index:03d}")
    name = str(raw.get("name") or raw.get("title") or raw.get("hypothesis") or raw.get("statement") or hid)
    statement = str(raw.get("statement") or raw.get("hypothesis") or name)
    expected = str(raw.get("expected_effect") or raw.get("goal") or raw.get("mechanism") or statement)
    validation = str(raw.get("validation") or raw.get("validator") or raw.get("evaluator") or "frozen evaluator and required gates")
    evidence_signal = str(raw.get("evidence_signal") or raw.get("evidence") or raw.get("source_signal") or "supplied hypothesis backlog")
    constraints_raw = raw.get("constraints") or raw.get("guardrails") or []
    if isinstance(constraints_raw, str):
        constraints = [constraints_raw]
    elif isinstance(constraints_raw, list):
        constraints = [str(item) for item in constraints_raw]
    else:
        constraints = []
    constraints.extend([
        f"Evidence signal: {evidence_signal}",
        f"Validation method: {validation}",
    ])
    files = raw.get("files") or raw.get("target_files") or []
    if files:
        if isinstance(files, str):
            constraints.append(f"Likely files: {files}")
        elif isinstance(files, list):
            constraints.append("Likely files: " + ", ".join(str(f) for f in files))
    return {
        "id": hid,
        "name": name[:160],
        "goal": expected,
        "constraints": constraints,
        "source": str(raw.get("source") or "hypothesis-backlog"),
        "statement": statement,
        "evidence_signal": evidence_signal,
        "validation": validation,
    }


def load_hypothesis_backlog(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        if str(data.get("recommendation", "")).lower() in {"no-mutation-recommended", "gather-evidence"}:
            raise RuntimeError(f"hypothesis backlog recommends {data.get('recommendation')}; do not force mutation")
        raw_items = data.get("hypotheses") or data.get("backlog") or data.get("top_hypotheses") or []
    elif isinstance(data, list):
        raw_items = data
    else:
        raise RuntimeError("hypothesis backlog must be a JSON object or list")
    hypotheses: list[dict[str, Any]] = []
    for idx, item in enumerate(raw_items, start=1):
        if not isinstance(item, dict):
            continue
        recommendation = str(item.get("recommendation", "")).lower()
        if recommendation in {"reject", "rejected", "defer", "deferred", "gather-evidence", "no-mutation"}:
            continue
        hypotheses.append(normalize_hypothesis(item, idx))
    if not hypotheses:
        raise RuntimeError("hypothesis backlog did not contain any testable hypotheses")
    return hypotheses

def load_rejected_ids(log_path: Path) -> set[str]:
    if not log_path.exists():
        return set()
    rejected: set[str] = set()
    for line in log_path.read_text().splitlines():
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if data.get("accepted") is False:
            rejected.add(str(data.get("hypothesis_id")))
    return rejected


def choose_hypothesis(iteration: int, rejected_ids: set[str], strategy: str, hypotheses: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    pool = hypotheses or HYPOTHESES
    candidates = [h for h in pool if h["id"] not in rejected_ids]
    if not candidates:
        candidates = pool[:]
    if strategy == "random":
        return random.choice(candidates)
    return candidates[(iteration - 1) % len(candidates)]


def build_codex_prompt(args: argparse.Namespace, target: Path, baseline: EvalResult, hypothesis: dict[str, Any]) -> str:
    constraints = "\n".join(f"- {c}" for c in hypothesis.get("constraints", []))
    blocked = "\n".join(f"- {p}" for p in (args.blocked_path or [])) or "- Do not modify evaluator files, benchmark fixtures, scoring scripts, lockfiles, git configuration, or secrets."
    return textwrap.dedent(
        f"""
        You are running a bounded skill-improvement experiment.

        Target skill path: {target}
        Current best score: {baseline.score}
        Evaluator: {args.evaluator}
        Optimization direction: {args.direction}
        Minimum accepted delta: {args.min_delta}

        Hypothesis {hypothesis['id']}: {hypothesis['name']}
        Expected mechanism: {hypothesis['goal']}
        Source: {hypothesis.get('source', 'built-in-catalog')}
        Evidence signal: {hypothesis.get('evidence_signal', 'not specified')}
        Validation: {hypothesis.get('validation', 'frozen evaluator')}

        Hypothesis constraints:
        {constraints}

        Blocked paths and evaluator protections:
        {blocked}

        Hard rules:
        - Modify only files under the target skill path unless the runner explicitly allows another path.
        - Do not modify the eval command, eval fixtures, scoring scripts, benchmark reports used as fixtures, git configuration, or secrets.
        - Keep the patch minimal and reversible.
        - Preserve valid YAML frontmatter in SKILL.md.
        - Prefer concrete skill instructions over generic advice.
        - Do not remove hard tests or weaken criteria to raise the score.
        - Do not claim the skill improved; the external runner will evaluate.
        - Stop after making the smallest plausible patch for this hypothesis.

        After editing, provide a concise summary of the change and the expected reason it may improve the metric.
        """
    ).strip()


def codex_command(args: argparse.Namespace, prompt: str, git_root: Path) -> list[str]:
    cmd = [args.codex_bin, "exec", "--cd", str(git_root)]
    if args.codex_model:
        cmd += ["--model", args.codex_model]
    if args.codex_mode == "full-auto":
        cmd.append("--full-auto")
    elif args.codex_mode == "yolo":
        if not args.sandbox_acknowledged:
            raise RuntimeError("--codex-mode yolo requires --sandbox-acknowledged")
        cmd.append("--dangerously-bypass-approvals-and-sandbox")
    elif args.codex_mode == "read-only":
        pass
    else:
        raise ValueError(f"invalid codex mode: {args.codex_mode}")
    if args.codex_json:
        cmd.append("--json")
    cmd.append(prompt)
    return cmd


def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


def resolve_stop_file(raw_stop_file: Optional[Path], state_dir: Path, git_root: Path) -> Path:
    if raw_stop_file:
        return raw_stop_file if raw_stop_file.is_absolute() else (git_root / raw_stop_file).resolve()
    return state_dir / "stop"


def stop_requested(stop_file: Path) -> bool:
    return stop_file.exists()


def read_stop_reason(stop_file: Path) -> str:
    if not stop_file.exists():
        return ""
    try:
        reason = stop_file.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return "stop file present"
    return reason or "stop file present"


def revert_changes(git_root: Path) -> None:
    run(["git", "reset", "--hard", "HEAD"], cwd=git_root, check=True)
    run(["git", "clean", "-fd"], cwd=git_root, check=True)


def maybe_commit(args: argparse.Namespace, git_root: Path, hypothesis: dict[str, Any], score: float) -> None:
    if not args.commit_accepted:
        return
    run(["git", "add", "--", str(args.target)], cwd=git_root, check=True)
    message = f"improve skill via {hypothesis['id']}: {hypothesis['name']} (score {score})"
    run(["git", "commit", "-m", message], cwd=git_root, check=True)


def template_path(template_name: str) -> Path:
    return TEMPLATE_DIR / template_name


def render_template(template_name: str, values: dict[str, Any]) -> str:
    path = template_path(template_name)
    if not path.exists():
        raise FileNotFoundError(f"template not found: {path}")
    rendered = path.read_text(encoding="utf-8")
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", str(value))
    return rendered


def bullet_list(items: list[str] | tuple[str, ...]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def inline_list(items: list[str] | tuple[str, ...]) -> str:
    return ", ".join(str(item) for item in items) if items else "none"


def decision_records_dir(report_path: Path) -> Path:
    return report_path.parent / "patch-decisions"


def write_patch_decision_records(
    args: argparse.Namespace,
    baseline: EvalResult,
    best: EvalResult,
    iterations: list[IterationResult],
    report_path: Path,
) -> list[str]:
    output_dir = decision_records_dir(report_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    benchmark_lock = best.evaluator_hash or baseline.evaluator_hash or "not captured"
    for item in iterations:
        safe_id = re.sub(r"[^a-zA-Z0-9_.-]+", "-", item.hypothesis_id).strip("-") or "hypothesis"
        record_path = output_dir / f"iteration-{item.iteration:03d}-{safe_id}.md"
        body = render_template(
            PATCH_DECISION_TEMPLATE,
            {
                "hypothesis_id": item.hypothesis_id,
                "target_skill": str(args.target),
                "mode": "automated-loop" if not args.dry_run else "dry-run",
                "evaluator": args.evaluator,
                "benchmark_lock": benchmark_lock,
                "safety_mode": args.codex_mode,
                "hypothesis_source": getattr(args, "hypothesis_source_label", "built-in-catalog"),
                "hypothesis_evidence_signal": "see selected hypothesis/backlog evidence in run log",
                "hypothesis_statement": f"{item.hypothesis_id} - {item.hypothesis_name}",
                "allowed_paths": inline_list([str(args.target), *[str(p) for p in args.extra_allowed_path]]),
                "blocked_paths": inline_list([str(p) for p in (args.blocked_path or [])]),
                "files_changed": inline_list(item.changed_files),
                "baseline_score": baseline.score,
                "baseline_status": baseline.status,
                "baseline_notes": inline_list(baseline.data.get("notes", []) if isinstance(baseline.data, dict) else []),
                "candidate_score": "not evaluated" if item.after is None else item.after,
                "candidate_status": "accepted" if item.accepted else "rejected",
                "candidate_notes": item.reason,
                "hypothesis_source": getattr(args, "hypothesis_source_label", "built-in-catalog"),
            "hypothesis_candidates_generated": getattr(args, "hypothesis_candidates_generated", "not captured"),
            "hypothesis_selected": inline_list([f"{item.hypothesis_id}: {item.hypothesis_name}" for item in iterations]) if iterations else "none",
            "hypothesis_deferred": "see backlog or run log; rejected tested hypotheses listed below",
            "hypothesis_discovery_notes": getattr(args, "hypothesis_discovery_notes", "not run; using built-in catalog"),
            "change_gate_policy": args.change_gate_policy,
                "change_gate_status": item.change_gate_status,
                "change_gate_notes": item.change_gate_notes or "not run",
                "accepted_or_rejected": "accepted" if item.accepted else "rejected",
                "decision_reason": item.reason,
                "rollback_action": "kept patch" if item.accepted else "reverted patch or no mutation retained",
                "commands_executed": "see parent run log and command stdout",
                "residual_risks": "Behavioral scenario quality is measured only when scenario outputs are supplied or executed.",
            },
        )
        record_path.write_text(body, encoding="utf-8")
        written.append(str(record_path))
    return written


def write_report(args: argparse.Namespace, git_root: Path, baseline: EvalResult, best: EvalResult, iterations: list[IterationResult], report_path: Path) -> None:
    accepted = [item for item in iterations if item.accepted]
    rejected = [item for item in iterations if not item.accepted]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    patch_records = write_patch_decision_records(args, baseline, best, iterations, report_path)
    accepted_lines = [
        f"- `{item.hypothesis_id}` {item.hypothesis_name}: {item.before} -> {item.after}; files: {inline_list(item.changed_files)}"
        for item in accepted
    ]
    rejected_lines = [
        f"- `{item.hypothesis_id}` {item.hypothesis_name}: {item.reason}; candidate score: {item.after}"
        for item in rejected
    ]
    rendered = render_template(
        RUN_REPORT_TEMPLATE,
        {
            "target_skill": str(args.target),
            "target_path": str(args.target),
            "baseline_static_score": baseline.score,
            "baseline_harness_score": best.score,
            "baseline_verdict": baseline.data.get("verdict", baseline.status) if isinstance(baseline.data, dict) else baseline.status,
            "baseline_blockers": inline_list([name for name, value in baseline.gates.items() if not gate_passes(value)]),
            "supplied_context_summary": f"Evaluator `{args.evaluator}` with frozen benchmark set to `{args.freeze_benchmark}`; change gate policy `{args.change_gate_policy}`; stop file `{getattr(args, 'stop_file', 'not configured')}`.",
            "target_package_summary": f"Target was evaluated from `{args.target}`; report path `{best.report_path or 'not captured'}`.",
            "additional_research_summary": "hypothesis discovery/backlog loaded when configured; otherwise built-in catalog fallback",
            "decision_supported": "accept, reject, revert, package, or continue bounded improvement based on measured gates.",
            "behavior_under_test": "baseline-first skill improvement with one hypothesis per iteration and explicit accept/reject evidence.",
            "evaluators": f"primary evaluator: {args.evaluator}; required gates: {inline_list(args.required_gate or [])}",
            "metrics": f"baseline score {baseline.score}; best score {best.score}; delta {best.score - baseline.score}",
            "gates": inline_list([f"{name}={value}" for name, value in best.gates.items()]),
            "hypothesis_source": getattr(args, "hypothesis_source_label", "built-in-catalog"),
            "hypothesis_candidates_generated": getattr(args, "hypothesis_candidates_generated", "not captured"),
            "hypothesis_selected": inline_list([f"{item.hypothesis_id}: {item.hypothesis_name}" for item in iterations]) if iterations else "none",
            "hypothesis_deferred": "see backlog or run log; rejected tested hypotheses listed below",
            "hypothesis_discovery_notes": getattr(args, "hypothesis_discovery_notes", "not run; using built-in catalog"),
            "change_gate_policy": args.change_gate_policy,
            "change_gate_summary": inline_list([f"iteration {item.iteration}: {item.change_gate_status} - {item.change_gate_notes or item.reason}" for item in iterations]) if iterations else "not run",
            "improvement_hypotheses": bullet_list(accepted_lines + rejected_lines),
            "skill_md_changes": "see changed-files evidence from accepted patch records",
            "reference_changes": "see changed-files evidence from accepted patch records",
            "script_changes": "see changed-files evidence from accepted patch records",
            "template_asset_changes": f"patch decision records rendered from `{PATCH_DECISION_TEMPLATE}`; run report rendered from `{RUN_REPORT_TEMPLATE}`.",
            "scenario_changes": "none unless listed in accepted patch records",
            "validation_changes": "none unless listed in accepted patch records",
            "packaging_changes": "package step is external to this run report unless invoked separately",
            "commands_executed": f"Evaluator mode `{args.evaluator}`; patch records: {inline_list(patch_records)}",
            "before_after_comparison": f"baseline {baseline.score}; final {best.score}; delta {best.score - baseline.score}",
            "residual_risks": "Behavioral scenario rates are not measured unless captured scenario outputs are supplied; yolo mode remains unsafe outside a disposable sandbox.",
            "package_path": "not packaged by this runner unless a separate package command is executed",
            "package_validator_result": "not run by this report writer",
            "packaged_file_count": "not applicable",
            "rollback_path": "git reset/clean for rejected patches; accepted patches require VCS or external backup rollback",
            "measured_evidence": f"baseline score {baseline.score}; final score {best.score}; iterations {len(iterations)}; accepted {len(accepted)}; rejected {len(rejected)}",
            "unmeasured_evidence": "activation/output metrics remain planned unless scenario execution results are supplied.",
        },
    )
    report_path.write_text(rendered, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run hypothesis-driven skill improvement with Codex.")
    parser.add_argument("--target", required=True, type=Path, help="Target skill folder.")
    parser.add_argument("--evaluator", choices=["command", "skill-benchmark"], default="command", help="Metric source. Use skill-benchmark for the bundled benchmark adapter.")
    parser.add_argument("--eval-command", help="Command run inside target folder when --evaluator command is used. Prefer JSON output with score.")
    parser.add_argument("--skill-benchmark-script", type=Path, help="Path to generate_benchmark_report.js. Defaults to the installed skill-benchmark script.")
    parser.add_argument("--skill-benchmark-results", type=Path, help="Optional fixed behavioral results JSON passed to skill-benchmark.")
    parser.add_argument("--skill-benchmark-out", type=Path, help="Output directory for generated skill-benchmark reports.")
    parser.add_argument("--direction", choices=["higher-is-better", "lower-is-better"], default="higher-is-better")
    parser.add_argument("--min-delta", type=float, default=0.1)
    parser.add_argument("--max-iterations", type=int, default=10, help="0 means infinite when --infinite is also set.")
    parser.add_argument("--infinite", action="store_true", help="Allow an unbounded loop. Requires explicit use.")
    parser.add_argument("--patience", type=int, default=5, help="Stop after this many consecutive rejected hypotheses.")
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--eval-timeout", type=int, default=600)
    parser.add_argument("--allow-eval-failure", action="store_true")
    parser.add_argument("--score-regex", help="Regex to extract score when command eval output is not JSON. First group is used.")
    parser.add_argument("--require-status-pass", action="store_true", help="Reject candidate unless evaluator status is exactly pass.")
    parser.add_argument("--required-gate", action="append", default=[], help="Gate name that must be present and pass. Can be repeated.")
    parser.add_argument("--change-gate-policy", choices=["disabled", "advisory", "required"], default="disabled", help="Structural change gate policy. Use required for autonomous acceptance when --change-gate-command is available.")
    parser.add_argument("--change-gate-command", help="Optional command run from the git root after candidate evaluation. It should print JSON with status pass, pass-with-warnings, or fail.")
    parser.add_argument("--change-gate-timeout", type=int, default=300)
    parser.add_argument("--enforce-all-gates", action="store_true", help="Reject candidate when any reported gate fails.")
    parser.add_argument("--enforce-blocker-gates", action="store_true", default=True, help="Reject candidate when benchmark blocker gates fail. Enabled by default.")
    parser.add_argument("--no-enforce-blocker-gates", dest="enforce_blocker_gates", action="store_false")
    parser.add_argument("--enforce-no-new-gate-failures", action="store_true", default=True, help="Reject candidate if it introduces new gate failures relative to baseline. Enabled by default.")
    parser.add_argument("--allow-new-gate-failures", dest="enforce_no_new_gate_failures", action="store_false")
    parser.add_argument("--freeze-benchmark", action="store_true", default=True, help="Hash evaluator inputs and reject if they change during the run. Enabled by default.")
    parser.add_argument("--no-freeze-benchmark", dest="freeze_benchmark", action="store_false")
    parser.add_argument("--benchmark-lock-path", action="append", type=Path, default=[], help="Additional evaluator fixture path to hash/freeze. Can be repeated.")
    parser.add_argument("--blocked-path", action="append", type=Path, default=[], help="Path Codex must not modify, even if inside allowed scope. Can be repeated.")
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--codex-model")
    parser.add_argument("--codex-mode", choices=["read-only", "full-auto", "yolo"], default="full-auto")
    parser.add_argument("--codex-json", action="store_true")
    parser.add_argument("--sandbox-acknowledged", action="store_true", help="Required for yolo mode.")
    parser.add_argument("--hypothesis-backlog", type=Path, help="Optional JSON backlog from skill-hypothesis-discovery or compatible source. Tested hypotheses are selected from this backlog before the built-in catalog.")
    parser.add_argument("--strategy", choices=["round-robin", "random"], default="round-robin")
    parser.add_argument("--state-dir", type=Path, default=Path(".skill-improver"))
    parser.add_argument("--stop-file", type=Path, help="File whose presence requests a graceful stop before the next candidate iteration. Defaults to state-dir/stop.")
    parser.add_argument("--extra-allowed-path", action="append", type=Path, default=[])
    parser.add_argument("--commit-accepted", action="store_true", help="Commit accepted patches.")
    parser.add_argument("--report-path", type=Path, help="Optional Markdown run report path. Defaults to state-dir/improvement-report.md.")
    parser.add_argument("--dry-run", action="store_true", help="Build prompts and evaluate but do not invoke Codex.")
    args = parser.parse_args()

    target = args.target.resolve()
    if not target.exists():
        raise SystemExit(f"target does not exist: {target}")
    skill_md = target / "SKILL.md"
    if not skill_md.exists():
        raise SystemExit(f"target does not look like a skill; missing SKILL.md: {skill_md}")
    if args.infinite and args.max_iterations != 0:
        print("[warn] --infinite set but --max-iterations is non-zero; max-iterations still limits the run")
    if args.max_iterations == 0 and not args.infinite:
        raise SystemExit("--max-iterations 0 requires --infinite")
    if args.codex_mode == "yolo" and not args.sandbox_acknowledged:
        raise SystemExit("--codex-mode yolo requires --sandbox-acknowledged")
    if args.change_gate_policy == "required" and not args.change_gate_command:
        raise SystemExit("--change-gate-policy required requires --change-gate-command")

    hypothesis_pool = None
    args.hypothesis_source_label = "built-in-catalog"
    args.hypothesis_candidates_generated = len(HYPOTHESES)
    args.hypothesis_discovery_notes = "not run; using built-in catalog"
    if args.hypothesis_backlog:
        backlog_path = args.hypothesis_backlog.resolve()
        hypothesis_pool = load_hypothesis_backlog(backlog_path)
        args.hypothesis_source_label = f"backlog:{backlog_path}"
        args.hypothesis_candidates_generated = len(hypothesis_pool)
        args.hypothesis_discovery_notes = "loaded evidence-backed hypothesis backlog; discovery recommendations are not measured improvements until tested"

    git_root = find_git_root(target)
    require_clean_git(git_root)
    state_dir = (git_root / args.state_dir).resolve() if not args.state_dir.is_absolute() else args.state_dir
    log_path = state_dir / "runs.jsonl"
    stop_file = resolve_stop_file(args.stop_file, state_dir, git_root)
    args.stop_file = stop_file
    report_path = args.report_path or (state_dir / "improvement-report.md")
    report_path = report_path if report_path.is_absolute() else (git_root / report_path).resolve()

    baseline = evaluate(args, target, git_root)
    baseline_gate_ok, baseline_gate_reason = result_passes_required_gates(args, baseline, None)
    best = baseline
    benchmark_hash = baseline.evaluator_hash
    print(f"[baseline] score={baseline.score} status={baseline.status} gates={baseline_gate_reason}", flush=True)
    if args.freeze_benchmark:
        print(f"[benchmark] frozen hash={benchmark_hash}", flush=True)

    rejected_in_row = 0
    iteration = 0
    results: list[IterationResult] = []

    while True:
        if stop_requested(args.stop_file):
            print(f"[stop] graceful stop requested by {args.stop_file}: {read_stop_reason(args.stop_file)}", flush=True)
            break
        iteration += 1
        if args.max_iterations and iteration > args.max_iterations:
            break
        if rejected_in_row >= args.patience:
            print(f"[stop] patience reached: {args.patience}", flush=True)
            break

        require_clean_git(git_root, [state_dir])
        rejected_ids = load_rejected_ids(log_path)
        hypothesis = choose_hypothesis(iteration, rejected_ids, args.strategy, hypothesis_pool)
        prompt = build_codex_prompt(args, target, best, hypothesis)

        print(f"[iteration {iteration}] hypothesis={hypothesis['id']} {hypothesis['name']}", flush=True)
        if args.dry_run:
            print(prompt)
            after = best
            accepted = False
            reason = "dry run"
            files = []
            change_gate = ChangeGateResult(status="not-run", notes="dry run")
        else:
            completed = run(codex_command(args, prompt, git_root), cwd=git_root, timeout=None, check=False)
            if completed.returncode != 0:
                revert_changes(git_root)
                raise RuntimeError(f"codex failed with exit code {completed.returncode}\n{completed.stdout}")
            files = changed_files(git_root, [state_dir])
            assert_changed_files_in_scope(files, git_root, target, args.extra_allowed_path)
            assert_no_blocked_paths_changed(files, git_root, args.blocked_path)
            try:
                after = evaluate(args, target, git_root)
                if args.freeze_benchmark and after.evaluator_hash != benchmark_hash:
                    accepted = False
                    reason = "benchmark changed during run"
                else:
                    gate_ok, gate_reason = result_passes_required_gates(args, after, baseline)
                    improved = is_improved(best.score, after.score, args.direction, args.min_delta)
                    change_gate = run_change_gate(args, target, git_root, files, hypothesis, best, after)
                    change_gate_ok, change_gate_reason = change_gate_allows_acceptance(args, change_gate)
                    accepted = improved and gate_ok and change_gate_ok
                    if accepted:
                        reason = "improved, required evaluator gates passed, and change gate allowed acceptance"
                    elif not improved:
                        reason = "did not improve enough"
                    elif not gate_ok:
                        reason = gate_reason
                    else:
                        reason = change_gate_reason
            except Exception as exc:
                after = None
                accepted = False
                reason = f"evaluation failed: {exc}"
                change_gate = ChangeGateResult(status="not-run", notes="candidate evaluation failed before change gate")

            if accepted and after is not None:
                maybe_commit(args, git_root, hypothesis, after.score)
                best = after
                rejected_in_row = 0
            else:
                revert_changes(git_root)
                rejected_in_row += 1

        before_score = best.score if not accepted else baseline.score
        result = IterationResult(
            iteration=iteration,
            hypothesis_id=hypothesis["id"],
            hypothesis_name=hypothesis["name"],
            before=before_score,
            after=None if after is None else after.score,
            accepted=accepted,
            reason=reason,
            changed_files=files,
            change_gate_status=change_gate.status,
            change_gate_notes=change_gate.notes,
        )
        results.append(result)
        append_jsonl(
            log_path,
            {
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                "iteration": iteration,
                "hypothesis_id": hypothesis["id"],
                "hypothesis_name": hypothesis["name"],
                    "hypothesis_source": hypothesis.get("source", getattr(args, "hypothesis_source_label", "built-in-catalog")),
                    "hypothesis_evidence_signal": hypothesis.get("evidence_signal", "not specified"),
                "baseline_score": baseline.score,
                "best_score": best.score,
                "candidate_score": None if after is None else after.score,
                "accepted": accepted,
                "reason": reason,
                "changed_files": files,
                "candidate_status": None if after is None else after.status,
                "candidate_gates": None if after is None else after.gates,
                "change_gate_status": change_gate.status,
                "change_gate_notes": change_gate.notes,
                "report_path": None if after is None else after.report_path,
            },
        )
        print(f"[decision] accepted={accepted} reason={reason} best={best.score}", flush=True)
        if args.sleep_seconds:
            time.sleep(args.sleep_seconds)

    write_report(args, git_root, baseline, best, results, report_path)
    print(json.dumps({"baseline_score": baseline.score, "best_score": best.score, "iterations": len(results), "report_path": str(report_path)}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        raise SystemExit(130)
