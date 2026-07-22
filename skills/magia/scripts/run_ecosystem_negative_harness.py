#!/usr/bin/env python3
"""Run coordinated fail-closed scenarios for the Nomia/Mago/Magia ecosystem."""
from __future__ import annotations
import argparse, copy, importlib.util, json, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NOW = datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc)
SPEC = "spec-2026-07-22-negative-contract"


def load_module(root: Path, alias: str):
    path = root / "scripts/ecosystem_handoff.py"
    spec = importlib.util.spec_from_file_location(alias, path)
    if spec is None or spec.loader is None: raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


def expect_rejected(module, root: Path, role: str, envelope: dict[str, Any], name: str, steps: list[dict[str, Any]]):
    result = module.validate_envelope(envelope, as_of=NOW, role=role, operation="consume", root=root)
    if result.get("status") == "accepted": raise RuntimeError(f"{name} was accepted unexpectedly")
    steps.append({"scenario": name, "status": "pass", "decision": result.get("status"), "errors": result.get("errors", [])})


def closure_result(nomia_root: Path, closure: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    with tempfile.TemporaryDirectory() as tmp:
        inp, out = Path(tmp)/"closure.json", Path(tmp)/"result.json"
        inp.write_text(json.dumps(closure), encoding="utf-8")
        cmd = [sys.executable, str(nomia_root/"scripts/validate_governance_closure.py"), "--input", str(inp), "--json-output", str(out)]
        done = subprocess.run(cmd, text=True, capture_output=True, check=False)
        payload = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {"stdout": done.stdout, "stderr": done.stderr}
        return done.returncode, payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("mago", "magia", "nomia"): parser.add_argument(f"--{name}", required=True)
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    roots = {name: Path(getattr(args, name)).resolve() for name in ("mago", "magia", "nomia")}
    modules = {name: load_module(root, f"neg_{name}") for name, root in roots.items()}
    steps = []
    try:
        shared = (
            "references/priority-contract.json", "references/ecosystem-handoff-contract.json", "references/ecosystem-compatibility.json",
            "references/ecosystem-routing-contract.json", "evals/ecosystem-routing-scenarios.json", "references/ecosystem-contract-provenance.json",
        )
        for rel in shared:
            if len({(root/rel).read_bytes() for root in roots.values()}) != 1: raise RuntimeError(f"shared file differs: {rel}")
        payload = {
            "feature_key":"negative-contract", "outcome":"exercise fail-closed behavior", "scope_summary":"negative fixture", "owner":"delivery-owner",
            "business_priority":{"level":"high","owner":"nomia","source":"fixture://governance","observed_at":NOW.isoformat()},
            "dependencies":[], "governance_readiness":"ready", "candidate_spec_id":SPEC, "candidate_spec_id_provenance":"fixture://mago-registry",
        }
        current = modules["nomia"].build_envelope(direction="nomia_to_mago", payload=payload, source="fixture://nomia", authority="nomia", evidence_refs=["fixture://decision"], observed_at=NOW.isoformat(), freshness_days=30, root=roots["nomia"])
        mixed = copy.deepcopy(current); mixed["ecosystem_release"] = "1.6.0"; mixed["source_version"] = "1.6.0"
        expect_rejected(modules["mago"], roots["mago"], "mago", mixed, "mixed-version-rejected", steps)
        stale = copy.deepcopy(current); stale["observed_at"] = "2025-01-01T00:00:00+00:00"
        expect_rejected(modules["mago"], roots["mago"], "mago", stale, "stale-evidence-rejected", steps)
        wrong = copy.deepcopy(current); wrong["provenance"]["authority"] = "magia"
        expect_rejected(modules["mago"], roots["mago"], "mago", wrong, "wrong-authority-rejected", steps)
        generic = copy.deepcopy(current); generic["payload"]["priority"] = "high"
        expect_rejected(modules["mago"], roots["mago"], "mago", generic, "generic-priority-rejected", steps)
        bad_id = copy.deepcopy(current); bad_id["payload"]["candidate_spec_id"] = "spec002"
        expect_rejected(modules["mago"], roots["mago"], "mago", bad_id, "legacy-identity-rejected", steps)
        base_closure = {
            "governance_status":"closed", "governance_lifecycle":"close",
            "decision":{"state":"accepted","authority":"nomia","evidence":["fixture://decision/close"]},
            "technical_state":{
                "planning":{"state":"complete","source":"fixture://mago","observed_at":NOW.isoformat()},
                "execution":{"state":"complete","source":"fixture://magia","observed_at":NOW.isoformat()},
                "validation":{"state":"passed","source":"fixture://magia","observed_at":NOW.isoformat()},
            },
            "release":{"state":"closed","released_at":NOW.isoformat(),"evidence":["fixture://external-release"]},
        }
        failed = copy.deepcopy(base_closure); failed["technical_state"]["validation"]["state"] = "failed"
        rc, result = closure_result(roots["nomia"], failed)
        if rc == 0: raise RuntimeError("closure accepted failed validation")
        steps.append({"scenario":"closure-denied-after-failed-validation","status":"pass","decision":result.get("status","rejected")})
        missing_release = copy.deepcopy(base_closure); missing_release["release"]["evidence"] = []
        rc, result = closure_result(roots["nomia"], missing_release)
        if rc == 0: raise RuntimeError("closure accepted missing external release evidence")
        steps.append({"scenario":"closure-denied-without-release-evidence","status":"pass","decision":result.get("status","rejected")})
        result = {"status":"pass","ecosystem_release":(roots["mago"]/"VERSION").read_text().strip(),"scenario":"ecosystem-fail-closed-suite","steps":steps,"limitations":["Structural contract fixtures; live-model routing and production interruption are not measured."]}
        rc = 0
    except Exception as exc:
        result = {"status":"fail","scenario":"ecosystem-fail-closed-suite","steps":steps,"error":str(exc)}; rc = 1
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_output: Path(args.json_output).write_text(text, encoding="utf-8")
    print(text, end="")
    return rc

if __name__ == "__main__": raise SystemExit(main())
