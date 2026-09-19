from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"validate_reproducibility_contract.py"


def contract():
    return {
      "contract_version":2,
      "target":{"name":"x","path":"/tmp/x","baseline_identity":"base"},
      "ceiling":"tool-action",
      "protected_paths":[],
      "hard_gates":["valid"],
      "variability":[{"id":"v1","surface":"self-host","class":"mechanical","target_control":"isolate","validation":"gate"}],
      "evaluators":[{"id":"e1","type":"script","metric":"pass","command":"x"}],
      "scenario_groups":["core"],
      "acceptance":{"behavioral_improvement_required_for_improvement_claim":True,"freeze_after_pass":True,"stagnation_limit":2,"weaken_hard_gates_to_pass":False},
      "delivery":{"atomic_when_applicable":True,"package_exact_frozen_candidate":True,"reject_output_aliases_before_write":True,"preserve_last_good_on_failure":True,"preserve_recovery_on_rollback_failure":True,"durable_complete_receipts":True},
      "source_integrity":{"snapshot_material_evidence_before_analysis":True,"immutable_pinned_vcs_reads_when_supported":True,"reject_source_alias_escape":True,"rebaseline_if_source_identity_changes":True},
      "self_hosting":{"enabled":True,"generation_id":"g1","controller_identity":"controller","baseline_identity":"baseline","candidate_identity":"candidate","max_self_recursion_depth":1,"controller_read_only":True,"evaluator_outside_candidate_surface":True,"promotion_external_to_candidate":True,"last_known_good_identity":"lkg"}
    }


def run(data):
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"c.json"; p.write_text(json.dumps(data),encoding="utf-8")
        return subprocess.run([sys.executable,str(SCRIPT),str(p),"--strict"],capture_output=True,text=True)


def test_self_hosting_contract_passes():
    r=run(contract()); assert r.returncode==0, r.stdout+r.stderr


def test_same_controller_candidate_fails():
    d=contract(); d["self_hosting"]["candidate_identity"]="controller"
    r=run(d); assert r.returncode!=0; assert "must differ" in r.stdout


def test_external_promotion_required():
    d=contract(); d["self_hosting"]["promotion_external_to_candidate"]=False
    r=run(d); assert r.returncode!=0; assert "promotion_external_to_candidate" in r.stdout
