#!/usr/bin/env python3
"""Compute vendor-neutral runtime token/cost components from explicit profiles."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

TOKEN_KEYS = (
    "uncached_input_tokens",
    "cache_write_tokens",
    "cache_read_tokens",
    "output_tokens",
)
RATE_KEYS = ("uncached_input", "cache_write", "cache_read", "output")
RATE_TO_TOKEN = {
    "uncached_input": "uncached_input_tokens",
    "cache_write": "cache_write_tokens",
    "cache_read": "cache_read_tokens",
    "output": "output_tokens",
}


def fail(message: str) -> ValueError:
    return ValueError(message)


def load_profile(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise fail(f"invalid JSON {p}: {exc}") from exc
    if not isinstance(data, dict):
        raise fail("profile must be a JSON object")
    allowed_top = {"profile_version", "evidence_kind", "rate_profile_id", "environment_id", "usage", "rates"}
    extra_top = sorted(set(data) - allowed_top)
    if extra_top:
        raise fail(f"unsupported top-level fields: {extra_top}")
    if data.get("profile_version") != "1.0":
        raise fail("profile_version must be '1.0'")
    if data.get("evidence_kind") not in {"estimated", "observed"}:
        raise fail("evidence_kind must be estimated or observed")
    if not isinstance(data.get("rate_profile_id"), str) or not data["rate_profile_id"].strip():
        raise fail("rate_profile_id is required")
    env = data.get("environment_id")
    if env is not None and (not isinstance(env, str) or not env.strip()):
        raise fail("environment_id must be null or a non-empty string")
    usage = data.get("usage")
    if not isinstance(usage, dict):
        raise fail("usage must be an object")
    allowed_usage = set(TOKEN_KEYS) | {"latency_ms"}
    extra_usage = sorted(set(usage) - allowed_usage)
    missing_usage = sorted(allowed_usage - set(usage))
    if extra_usage:
        raise fail(f"unsupported usage fields: {extra_usage}")
    if missing_usage:
        raise fail(f"missing usage fields: {missing_usage}")
    for key in TOKEN_KEYS:
        value = usage.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise fail(f"usage.{key} must be a non-negative integer")
    latency = usage.get("latency_ms")
    if latency is not None and (isinstance(latency, bool) or not isinstance(latency, (int, float)) or latency < 0 or not math.isfinite(float(latency))):
        raise fail("usage.latency_ms must be null or a finite non-negative number")
    rates = data.get("rates")
    if rates is not None:
        if not isinstance(rates, dict) or not isinstance(rates.get("currency"), str) or not rates["currency"].strip():
            raise fail("rates.currency is required when rates are present")
        extra_rates = sorted(set(rates) - {"currency", "per_million"})
        if extra_rates:
            raise fail(f"unsupported rates fields: {extra_rates}")
        per_million = rates.get("per_million")
        if not isinstance(per_million, dict):
            raise fail("rates.per_million must be an object")
        extra_pm = sorted(set(per_million) - set(RATE_KEYS))
        missing_pm = sorted(set(RATE_KEYS) - set(per_million))
        if extra_pm:
            raise fail(f"unsupported rates.per_million fields: {extra_pm}")
        if missing_pm:
            raise fail(f"missing rates.per_million fields: {missing_pm}")
        for key in RATE_KEYS:
            value = per_million.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 or not math.isfinite(float(value)):
                raise fail(f"rates.per_million.{key} must be a finite non-negative number")
    return data


def compute(profile: dict[str, Any]) -> dict[str, Any]:
    usage = profile["usage"]
    total_input = usage["uncached_input_tokens"] + usage["cache_write_tokens"] + usage["cache_read_tokens"]
    total_tokens = total_input + usage["output_tokens"]
    costs: dict[str, float] | None = None
    total_cost: float | None = None
    rates = profile.get("rates")
    if rates is not None:
        per_million = rates["per_million"]
        costs = {
            key: usage[RATE_TO_TOKEN[key]] / 1_000_000 * float(per_million[key])
            for key in RATE_KEYS
        }
        total_cost = sum(costs.values())
    return {
        "profile_version": profile["profile_version"],
        "evidence_kind": profile["evidence_kind"],
        "rate_profile_id": profile["rate_profile_id"],
        "environment_id": profile.get("environment_id"),
        "usage": dict(usage),
        "totals": {
            "input_tokens": total_input,
            "output_tokens": usage["output_tokens"],
            "total_tokens": total_tokens,
            "latency_ms": usage.get("latency_ms"),
            "cost": total_cost,
            "currency": rates.get("currency") if rates else None,
        },
        "cost_components": costs,
    }


def delta(before: float | int | None, after: float | int | None) -> float | int | None:
    if before is None or after is None:
        return None
    return after - before


def compare(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    b, a = compute(before), compute(after)
    same_rate = b["rate_profile_id"] == a["rate_profile_id"] and b["totals"]["currency"] == a["totals"]["currency"]
    same_env = bool(b["environment_id"]) and b["environment_id"] == a["environment_id"]
    both_observed = b["evidence_kind"] == a["evidence_kind"] == "observed"
    cost_comparable = same_rate and b["totals"]["cost"] is not None and a["totals"]["cost"] is not None
    runtime_comparable = both_observed and same_env
    return {
        "before": b,
        "after": a,
        "comparison": {
            "total_input_token_delta": delta(b["totals"]["input_tokens"], a["totals"]["input_tokens"]),
            "output_token_delta": delta(b["totals"]["output_tokens"], a["totals"]["output_tokens"]),
            "total_token_delta": delta(b["totals"]["total_tokens"], a["totals"]["total_tokens"]),
            "latency_ms_delta": delta(b["totals"]["latency_ms"], a["totals"]["latency_ms"]),
            "cost_delta": delta(b["totals"]["cost"], a["totals"]["cost"]) if cost_comparable else None,
            "same_rate_profile": same_rate,
            "same_environment": same_env,
            "both_observed": both_observed,
            "cost_comparable": cost_comparable,
            "runtime_comparable": runtime_comparable,
            "evidence_status": "runtime-comparable" if runtime_comparable else "planning-or-noncomparable",
            "overall_improvement_status": "not-decided-by-calculator"
        }
    }


def write(report: dict[str, Any], output: str | None) -> None:
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if output:
        p = Path(output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


def main() -> int:
    ap = argparse.ArgumentParser(description="Compute vendor-neutral runtime token/cost components from explicit profiles.")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--profile")
    group.add_argument("--before")
    ap.add_argument("--after")
    ap.add_argument("--json")
    args = ap.parse_args()
    if args.before and not args.after:
        ap.error("--before requires --after")
    if args.after and not args.before:
        ap.error("--after requires --before")
    try:
        report = {"profile": compute(load_profile(args.profile)), "overall_improvement_status": "not-decided-by-calculator"} if args.profile else compare(load_profile(args.before), load_profile(args.after))
    except ValueError as exc:
        report = {"status": "fail", "error": str(exc)}
        write(report, args.json)
        return 2
    write(report, args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
