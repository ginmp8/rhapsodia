#!/usr/bin/env python3
"""Execute the strict Nomia -> Mago -> Magia -> Mago -> Nomia lifecycle fixture."""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NOW = datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc)
SPEC = "spec-2026-07-22-ecosystem-contract"


def load_module(root: Path, alias: str):
    path = root / "scripts" / "ecosystem_handoff.py"
    spec = importlib.util.spec_from_file_location(alias, path)
    if spec is None or spec.loader is None: raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def consume(module, root: Path, role: str, envelope: dict[str, Any]) -> dict[str, Any]:
    result = module.validate_envelope(envelope, as_of=NOW, role=role, operation="consume", root=root)
    if result["status"] != "accepted": raise RuntimeError(f"{role} rejected {envelope['direction']}: {result}")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mago", required=True)
    parser.add_argument("--magia", required=True)
    parser.add_argument("--nomia", required=True)
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    roots = {name:Path(getattr(args,name)).resolve() for name in ("mago","magia","nomia")}
    modules = {name:load_module(root, f"{name}_ecosystem_handoff") for name,root in roots.items()}
    steps: list[dict[str, Any]] = []
    try:
        for name, root in roots.items():
            errors = modules[name].contract_errors(modules[name].load_contract(root), root)
            if errors: raise RuntimeError(f"{name} contract invalid: {errors}")
        shared = ("references/priority-contract.json","references/ecosystem-handoff-contract.json","references/ecosystem-compatibility.json")
        for rel in shared:
            values = {(roots[name]/rel).read_bytes() for name in roots}
            if len(values) != 1: raise RuntimeError(f"shared contract differs: {rel}")
        nomia_payload = {
            "feature_key":"ecosystem-contract","outcome":"Deliver a governed coordinated capability","scope_summary":"Strict cross-skill contract fixture","owner":"delivery-owner",
            "business_priority":{"level":"high","owner":"nomia","source":"fixture://governance","observed_at":NOW.isoformat()},
            "dependencies":[],"governance_readiness":"ready","candidate_spec_id":SPEC,"candidate_spec_id_provenance":"fixture://mago-registry"
        }
        n2m = modules['nomia'].build_envelope(direction='nomia_to_mago',payload=nomia_payload,source='fixture://nomia-intake',authority='nomia',evidence_refs=['fixture://decision/1'],observed_at=NOW.isoformat(),freshness_days=30,root=roots['nomia'])
        consume(modules['mago'], roots['mago'], 'mago', n2m); steps.append({'step':'nomia_to_mago','handoff_id':n2m['handoff_id'],'status':'pass'})
        m2x_payload = {
            "spec_id":SPEC,"planning_state":"ready","planning_evidence":"fixture://mago/manifest","requirement_refs":["REQ-001"],"acceptance_criteria_refs":["AC-001"],"task_ids":["task001"],"validation_refs":["VAL-001"],
            "technical_criticality":{"level":"high","owner":"mago","rationale":"contract and compatibility impact"},
            "execution_sequence":{"rank":10,"lane":"fixed_date","owner":"mago","rationale":["dependency-safe","governed validation"]},"readiness":"ready"
        }
        m2x = modules['mago'].build_envelope(direction='mago_to_magia',payload=m2x_payload,source='fixture://mago-plan',authority='mago',evidence_refs=['fixture://manifest','fixture://validation'],observed_at=NOW.isoformat(),freshness_days=30,root=roots['mago'])
        consume(modules['magia'], roots['magia'], 'magia', m2x); steps.append({'step':'mago_to_magia','handoff_id':m2x['handoff_id'],'status':'pass'})
        x2m_payload = {"spec_id":SPEC,"execution_state":"done","validation_state":"passed","evidence_reference":"fixture://magia/validation-evidence","deviations":[],"planning_change_required":False}
        x2m = modules['magia'].build_envelope(direction='magia_to_mago',payload=x2m_payload,source='fixture://magia-execution',authority='magia',evidence_refs=['fixture://tests/pass'],observed_at=NOW.isoformat(),freshness_days=30,root=roots['magia'])
        consume(modules['mago'], roots['mago'], 'mago', x2m); steps.append({'step':'magia_to_mago','handoff_id':x2m['handoff_id'],'status':'pass'})
        final_mago_payload = {"spec_id":SPEC,"planning_state":"done","planning_evidence":"fixture://mago/reconciliation","dependency_summary":{"blocked":[],"unknown":[]},"technical_risk_summary":{"level":"low","residual":[]},"forecast_impact":{"kind":"none","evidence":[x2m['handoff_id']]}}
        m2n = modules['mago'].build_envelope(direction='mago_to_nomia',payload=final_mago_payload,source='fixture://mago-reconciliation',authority='mago',evidence_refs=[x2m['handoff_id']],observed_at=NOW.isoformat(),freshness_days=30,root=roots['mago'])
        consume(modules['nomia'], roots['nomia'], 'nomia', m2n); steps.append({'step':'mago_to_nomia','handoff_id':m2n['handoff_id'],'status':'pass'})
        x2n_payload = {"spec_id":SPEC,"execution_state":"done","validation_state":"passed","evidence_reference":"fixture://magia/validation-evidence","delivery_impacts":[]}
        x2n = modules['magia'].build_envelope(direction='magia_to_nomia',payload=x2n_payload,source='fixture://magia-execution',authority='magia',evidence_refs=['fixture://tests/pass'],observed_at=NOW.isoformat(),freshness_days=30,root=roots['magia'])
        consume(modules['nomia'], roots['nomia'], 'nomia', x2n); steps.append({'step':'magia_to_nomia','handoff_id':x2n['handoff_id'],'status':'pass'})
        closure = {
          "governance_status":"closed","governance_lifecycle":"close",
          "decision":{"state":"accepted","authority":"nomia","evidence":["fixture://governance-decision/close"]},
          "technical_state":{
            "planning":{"state":m2n['payload']['nomia_planning_state'],"source":m2n['handoff_id'],"observed_at":NOW.isoformat()},
            "execution":{"state":x2n['payload']['nomia_execution_state'],"source":x2n['handoff_id'],"observed_at":NOW.isoformat()},
            "validation":{"state":x2n['payload']['nomia_validation_state'],"source":x2n['handoff_id'],"observed_at":NOW.isoformat()},
          },
          "release":{"state":"closed","released_at":NOW.isoformat(),"evidence":["fixture://external-release/1.6.0"]}
        }
        with tempfile.TemporaryDirectory() as tmp:
            inp, out = Path(tmp)/'closure.json', Path(tmp)/'closure-result.json'
            inp.write_text(json.dumps(closure), encoding='utf-8')
            cmd=[sys.executable,str(roots['nomia']/ 'scripts/validate_governance_closure.py'),'--input',str(inp),'--json-output',str(out)]
            done=subprocess.run(cmd,text=True,capture_output=True,check=False)
            if done.returncode != 0: raise RuntimeError(f"Nomia closure gate failed: {done.stdout} {done.stderr}")
            closure_result=json.loads(out.read_text(encoding='utf-8'))
        steps.append({'step':'nomia_closure','status':closure_result['status']})
        result={'status':'pass','ecosystem_release':'1.6.0','scenario':'nomia-mago-magia-reconcile-close','steps':steps,'limitations':['Fixture evidence proves contract behavior only; it is not production release evidence.']}
        rc=0
    except Exception as exc:
        result={'status':'fail','ecosystem_release':'1.6.0','scenario':'nomia-mago-magia-reconcile-close','steps':steps,'error':str(exc)}
        rc=1
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.json_output: Path(args.json_output).write_text(text,encoding='utf-8')
    print(text,end='')
    return rc

if __name__ == '__main__':
    raise SystemExit(main())
