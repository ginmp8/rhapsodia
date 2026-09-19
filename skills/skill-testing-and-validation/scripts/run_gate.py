#!/usr/bin/env python3
"""Execute one validation gate and emit a deterministic machine-readable receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from classify_failure import classify  # noqa: E402
from discover_commands import GATES, discover  # noqa: E402
from environment_fingerprint import fingerprint  # noqa: E402


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def excerpt(text: str, limit: int = 4000) -> str:
    return text[:limit]


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def load_argv(raw: str) -> list[str]:
    value = json.loads(raw)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise ValueError("--argv-json must be a non-empty JSON array of non-empty strings")
    return value


def display(argv: list[str]) -> str:
    return shlex.join(argv)


def make_receipt(
    target: Path,
    gate: str,
    argv: list[str] | None,
    execute: bool,
    timeout: int,
) -> tuple[dict[str, Any], int]:
    root = target.resolve()
    discovered = discover(root)
    source = "explicit-argv" if argv else "discovery"
    selected = discovered.get("selected", {}).get(gate)
    if argv is None and selected:
        argv = list(selected.get("argv") or [])
    command_info = {
        "argv": argv or [],
        "display": display(argv) if argv else None,
        "source": source if source == "explicit-argv" else (selected or {}).get("source"),
        "rank": None if source == "explicit-argv" else (selected or {}).get("rank"),
    }
    executable_name = Path(argv[0]).name if argv else ""
    relevant_tools = [executable_name] if executable_name in {"node", "npm", "dotnet", "go", "cargo", "java", "mvn", "gradle", "make", "bash"} else []
    env = fingerprint(root, relevant_tools)
    base: dict[str, Any] = {
        "receipt_version": 1,
        "target": str(root),
        "gate": gate,
        "working_directory": str(root),
        "environment": env,
        "command": command_info,
        "status": "not-run",
        "classification": "unknown",
        "classification_detail": None,
        "exit_code": None,
        "result": {"stdout_excerpt": "", "stderr_excerpt": "", "stdout_sha256": sha256_text(""), "stderr_sha256": sha256_text("")},
    }
    if not argv:
        base["result"]["diagnostic"] = {"code": "command/not-selected", "subject": gate, "evidence": {"discovery": discovered}}
        return base, 0
    if not execute:
        base["classification"] = gate
        base["result"]["diagnostic"] = {"code": "execution/not-requested", "subject": gate, "evidence": {"command": command_info}}
        return base, 0
    try:
        proc = subprocess.run(argv, cwd=root, text=True, capture_output=True, timeout=timeout)
        combined = "\n".join(part for part in (proc.stdout, proc.stderr) if part)
        detail = classify(combined, gate=gate, exit_code=proc.returncode)
        status = "pass" if proc.returncode == 0 else ("blocked" if detail["category"] == "environment" else "fail")
        base.update(
            {
                "status": status,
                "classification": gate if proc.returncode == 0 else detail["category"],
                "classification_detail": detail,
                "exit_code": proc.returncode,
                "result": {
                    "stdout_excerpt": excerpt(proc.stdout),
                    "stderr_excerpt": excerpt(proc.stderr),
                    "stdout_sha256": sha256_text(proc.stdout),
                    "stderr_sha256": sha256_text(proc.stderr),
                },
            }
        )
        return base, 0 if status == "pass" else (2 if status == "blocked" else 1)
    except FileNotFoundError as exc:
        text = str(exc)
        detail = classify("command not found: " + text, gate=gate, exit_code=None)
        base.update(
            {
                "status": "blocked",
                "classification": "environment",
                "classification_detail": detail,
                "exit_code": None,
                "result": {
                    "stdout_excerpt": "",
                    "stderr_excerpt": excerpt(text),
                    "stdout_sha256": sha256_text(""),
                    "stderr_sha256": sha256_text(text),
                    "diagnostic": {"code": "environment/command-missing", "subject": argv[0], "evidence": {"error": text}},
                },
            }
        )
        return base, 2
    except PermissionError as exc:
        text = str(exc)
        detail = classify("Permission denied: " + text, gate=gate, exit_code=None)
        base.update(
            {
                "status": "blocked",
                "classification": "environment",
                "classification_detail": detail,
                "exit_code": None,
                "result": {
                    "stdout_excerpt": "",
                    "stderr_excerpt": excerpt(text),
                    "stdout_sha256": sha256_text(""),
                    "stderr_sha256": sha256_text(text),
                    "diagnostic": {"code": "environment/permission", "subject": argv[0], "evidence": {"error": text}},
                },
            }
        )
        return base, 2
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        detail = classify("timed out\n" + stdout + "\n" + stderr, gate=gate, exit_code=None)
        base.update(
            {
                "status": "blocked",
                "classification": "environment",
                "classification_detail": detail,
                "exit_code": None,
                "result": {
                    "stdout_excerpt": excerpt(stdout),
                    "stderr_excerpt": excerpt(stderr),
                    "stdout_sha256": sha256_text(stdout),
                    "stderr_sha256": sha256_text(stderr),
                    "diagnostic": {"code": "environment/timeout", "subject": gate, "evidence": {"timeout_seconds": timeout}},
                },
            }
        )
        return base, 2


def main() -> int:
    ap = argparse.ArgumentParser(description="Execute one build/test/lint/validator/package gate and emit a receipt.")
    ap.add_argument("--target", required=True)
    ap.add_argument("--gate", required=True, choices=GATES)
    ap.add_argument("--argv-json", help="Explicit argv as a JSON array; overrides discovery")
    ap.add_argument("--execute", action="store_true", help="Actually execute the gate. Without this flag status is not-run.")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--receipt", help="Optional JSON receipt path, written atomically")
    ap.add_argument("--format", choices=["json", "text"], default="json")
    args = ap.parse_args()
    try:
        argv = load_argv(args.argv_json) if args.argv_json else None
        receipt, process_code = make_receipt(Path(args.target), args.gate, argv, args.execute, args.timeout)
    except (ValueError, json.JSONDecodeError) as exc:
        receipt = {
            "receipt_version": 1,
            "target": str(Path(args.target).resolve()),
            "gate": args.gate,
            "working_directory": str(Path(args.target).resolve()),
            "environment": fingerprint(Path(args.target), []),
            "command": {"argv": [], "display": None, "source": "invalid-input", "rank": None},
            "status": "blocked",
            "classification": "configuration",
            "classification_detail": None,
            "exit_code": None,
            "result": {"diagnostic": {"code": "configuration/invalid-argv", "subject": "--argv-json", "evidence": {"error": str(exc)}}},
        }
        process_code = 2
    if args.receipt:
        write_json_atomic(Path(args.receipt), receipt)
    if args.format == "json":
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(f"{args.gate}: {receipt['status']} classification={receipt['classification']} exit_code={receipt['exit_code']}")
        if receipt.get("command", {}).get("display"):
            print(f"command: {receipt['command']['display']}")
    return process_code


if __name__ == "__main__":
    raise SystemExit(main())
