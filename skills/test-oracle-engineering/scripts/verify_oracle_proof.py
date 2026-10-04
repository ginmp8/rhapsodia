#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("oracle_validator",ROOT/"scripts"/"validate_oracle_artifact.py")
v=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(v)


def diag(code:str,path:str,message:str)->dict[str,str]: return {"code":code,"path":path,"message":message}
def canonical_json_bytes(data:Any)->bytes: return json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
def json_identity(data:Any)->str: return "sha256:"+hashlib.sha256(canonical_json_bytes(data)).hexdigest()

def tree_identity(root:Path)->str:
    root=root.resolve(); h=hashlib.sha256()
    for p in sorted((x for x in root.rglob("*") if x.is_file() or x.is_symlink()),key=lambda x:x.relative_to(root).as_posix()):
        rel=p.relative_to(root).as_posix().encode("utf-8")
        h.update(len(rel).to_bytes(8,"big")); h.update(rel)
        if p.is_symlink():
            data=("SYMLINK:"+str(p.readlink())).encode("utf-8")
        else: data=p.read_bytes()
        h.update(len(data).to_bytes(8,"big")); h.update(data)
    return "sha256:"+h.hexdigest()

def load_json(path:Path)->Any: return json.loads(path.read_text(encoding="utf-8"))

def verify(spec_doc:dict[str,Any],proof:dict[str,Any],candidate_identity:str|None)->dict[str,Any]:
    errors=[]; warnings=[]
    sr=v.validate(spec_doc); pr=v.validate(proof)
    if sr["status"]!="pass": errors.append(diag("E_SPEC_INVALID","$.spec","oracle spec failed standalone validation"))
    if pr["status"]!="pass": errors.append(diag("E_PROOF_INVALID","$.proof","proof receipt failed standalone validation"))
    if spec_doc.get("contract")!="test-oracle-spec/v2" or proof.get("contract")!="test-oracle-proof/v2":
        errors.append(diag("E_STRICT_VERSION","$","cross-artifact proof verification requires v2 spec and v2 proof; v1 remains review-only"))
    expected_spec_id=json_identity(spec_doc)
    if proof.get("oracle_spec_identity")!=expected_spec_id:
        errors.append(diag("E_SPEC_IDENTITY","$.proof.oracle_spec_identity",f"expected {expected_spec_id}"))
    if proof.get("oracle_id")!=spec_doc.get("oracle_id"):
        errors.append(diag("E_ORACLE_ID","$.proof.oracle_id","must equal spec.oracle_id"))
    spec_candidate=spec_doc.get("candidate_identity")
    if spec_candidate=="unbound": errors.append(diag("E_CANDIDATE_UNBOUND","$.spec.candidate_identity","must be bound before execution proof can be accepted"))
    if proof.get("candidate_identity")!=spec_candidate:
        errors.append(diag("E_CANDIDATE_IDENTITY","$.proof.candidate_identity","must equal spec.candidate_identity"))
    if candidate_identity is not None and candidate_identity!=spec_candidate:
        errors.append(diag("E_CANDIDATE_IDENTITY","$.candidate","supplied/recomputed candidate identity does not match the frozen spec"))
    spec_argv=spec_doc.get("execution",{}).get("command_argv")
    if proof.get("command_argv")!=spec_argv:
        errors.append(diag("E_COMMAND_DRIFT","$.proof.command_argv","executed command must exactly match frozen spec.execution.command_argv"))
    max_attempts=spec_doc.get("max_attempts")
    attempts=proof.get("attempts") if isinstance(proof.get("attempts"),list) else []
    if isinstance(max_attempts,int):
        if isinstance(proof.get("attempt"),int) and proof["attempt"]>max_attempts: errors.append(diag("E_ATTEMPT_BUDGET","$.proof.attempt","attempt exceeds spec.max_attempts"))
        if len(attempts)>max_attempts: errors.append(diag("E_ATTEMPT_BUDGET","$.proof.attempts","recorded attempts exceed spec.max_attempts"))
        for rec in attempts:
            if isinstance(rec,dict) and isinstance(rec.get("attempt"),int) and rec["attempt"]>max_attempts:
                errors.append(diag("E_ATTEMPT_BUDGET","$.proof.attempts","attempt record exceeds spec.max_attempts")); break
    reps=spec_doc.get("nondeterminism",{}).get("repetitions")
    verdict=proof.get("verdict")
    if verdict in {"proven","rejected"} and isinstance(reps,int) and len(attempts)<reps:
        errors.append(diag("E_REPETITIONS","$.proof.attempts",f"strong proof requires at least {reps} recorded attempt(s)"))
    semantic={rec.get("outcome_kind") for rec in attempts if isinstance(rec,dict) and rec.get("outcome_kind") in {"expected-observation","oracle-rejection"}}
    if len(semantic)>1:
        errors.append(diag("E_UNSTABLE_OBSERVATION","$.proof.attempts","same frozen proof observed both expected and rejecting semantic outcomes"))
    if verdict=="proven" and semantic and semantic!={"expected-observation"}:
        errors.append(diag("E_UNSTABLE_OBSERVATION","$.proof.attempts","proven requires stable expected semantic observations"))
    if verdict=="rejected" and semantic and semantic!={"oracle-rejection"}:
        errors.append(diag("E_UNSTABLE_OBSERVATION","$.proof.attempts","rejected requires stable rejecting semantic observations"))
    mode=spec_doc.get("nondeterminism",{}).get("mode")
    if mode=="probabilistic" and verdict in {"proven","rejected"}:
        warnings.append(diag("W_STATISTICAL_SEMANTICS","$.spec.nondeterminism.statistical_rule","mechanical verifier checks presence/identity/repetition only; it does not evaluate the domain statistical rule"))
    return {
        "verifier":"test-oracle-proof-verifier/v1",
        "status":"pass" if not errors else "fail",
        "spec_identity":expected_spec_id,
        "candidate_identity":candidate_identity or spec_candidate,
        "proof_identity":json_identity(proof),
        "warnings":warnings,
        "errors":errors,
        "standalone":{"spec":sr["status"],"proof":pr["status"]}
    }


def main()->int:
    ap=argparse.ArgumentParser(description="Cross-verify a v2 oracle proof against its frozen spec and candidate identity.")
    ap.add_argument("--spec",required=True); ap.add_argument("--proof",required=True)
    group=ap.add_mutually_exclusive_group(); group.add_argument("--candidate-identity"); group.add_argument("--candidate-root")
    ap.add_argument("--json",dest="out")
    a=ap.parse_args()
    try:
        spec_doc=load_json(Path(a.spec)); proof=load_json(Path(a.proof))
        candidate=a.candidate_identity
        if a.candidate_root: candidate=tree_identity(Path(a.candidate_root))
        report=verify(spec_doc,proof,candidate)
    except Exception as exc:
        report={"verifier":"test-oracle-proof-verifier/v1","status":"fail","spec_identity":None,"candidate_identity":None,"proof_identity":None,"warnings":[],"errors":[diag("E_RUNTIME","$",str(exc))],"standalone":{"spec":"not-run","proof":"not-run"}}
    payload=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
    if a.out: Path(a.out).write_text(payload,encoding="utf-8")
    print(payload,end="")
    return 0 if report["status"]=="pass" else 1

if __name__=="__main__": raise SystemExit(main())
