#!/usr/bin/env python3
"""Validate Skill Harness portability across several supported host profiles."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent


def _load_portability_module():
    module_path = SCRIPT_DIR / "skill_harness_portability.py"
    spec = importlib.util.spec_from_file_location("_skill_harness_portability_local", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load sibling portability validator: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_PORTABILITY = _load_portability_module()
PROFILES = _PORTABILITY.PROFILES
validate = _PORTABILITY.validate


def _parse_profiles(raw: str) -> list[str]:
    if raw.strip().lower() == "all":
        return list(PROFILES)
    requested = [item.strip().lower() for item in raw.split(",") if item.strip()]
    unknown = sorted(set(requested) - set(PROFILES))
    if unknown:
        raise ValueError(f"unsupported profiles: {unknown}; allowed={list(PROFILES)}")
    if not requested:
        raise ValueError("at least one profile is required")
    # Preserve caller order while removing duplicates.
    return list(dict.fromkeys(requested))


def validate_matrix(target: Path, profiles: list[str], *, strict: bool) -> dict:
    reports = {profile: validate(target, profile) for profile in profiles}
    failed = [profile for profile, report in reports.items() if report["status"] == "fail"]
    warned = [profile for profile, report in reports.items() if report["status"] == "warn"]
    status = "fail" if failed or (strict and warned) else ("warn" if warned else "pass")
    return {
        "status": status,
        "target": str(target.expanduser().resolve()),
        "strict": strict,
        "requested_profiles": profiles,
        "summary": {
            "profile_count": len(profiles),
            "pass_count": sum(report["status"] == "pass" for report in reports.values()),
            "warn_count": len(warned),
            "fail_count": len(failed),
            "warned_profiles": warned,
            "failed_profiles": failed,
        },
        "profiles": reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the existing portability validator across a host profile matrix.")
    parser.add_argument("--target", required=True)
    parser.add_argument("--profiles", default="all", help="all or comma-separated portable,openai,claude,copilot,cursor")
    parser.add_argument("--strict", action="store_true", help="Treat profile warnings as a failing matrix gate.")
    parser.add_argument("--output")
    args = parser.parse_args()

    try:
        profiles = _parse_profiles(args.profiles)
        report = validate_matrix(Path(args.target), profiles, strict=args.strict)
    except Exception as exc:
        report = {"status": "fail", "stage": "preflight", "error": str(exc)}

    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    sys.stdout.write(payload)
    return 0 if report.get("status") in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
