#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any

CLAIM_TYPES={"behavior","authorization","api-contract","event-contract","data-invariant","migration","concurrency","idempotency","retry","cli","ui-behavior","security","other"}
LAYERS={"existing-focused-test","integration-public-stack","contract-boundary","component-unit","static"}
MODES={"design-only","existing-test","generated-test","integration","contract","static"}
EXEC_STATES={"pass","fail","blocked","not-run"}
VERDICTS={"proven","rejected","inconclusive","blocked","not-run"}

def nonempty(v:Any)->bool: return isinstance(v,str) and bool(v.strip())
def strings(v:Any)->bool: return isinstance(v,list) and all(nonempty(x) for x in v)
def diag(code,path,message): return {"code":code,"path":path,"message":message}
def identity(data:Any)->str:
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def validate_spec(d:dict[str,Any])->list[dict[str,str]]:
    e=[]
    for f in ("oracle_id","claim","source_identity","candidate_identity","evaluator_identity"):
        if not nonempty(d.get(f)): e.append(diag("E_REQUIRED",f"$.{f}","must be a non-empty string"))
    if d.get("claim_type") not in CLAIM_TYPES: e.append(diag("E_CLAIM_TYPE","$.claim_type",f"must be one of {sorted(CLAIM_TYPES)}"))
    for f in ("target_scope","verification_write_scope","protected_paths"):
        if not strings(d.get(f)): e.append(diag("E_SCOPE",f"$.{f}","must be an array of non-empty strings"))
        elif len(d[f])!=len(set(d[f])): e.append(diag("E_DUPLICATE",f"$.{f}","items must be unique"))
    if not d.get("target_scope"): e.append(diag("E_TARGET_SCOPE","$.target_scope","must not be empty"))
    obs=d.get("observable")
    if not isinstance(obs,dict): e.append(diag("E_OBSERVABLE","$.observable","must be an object"))
    else:
        for f in ("setup","input","action","expected","failure_signal"):
            if not nonempty(obs.get(f)): e.append(diag("E_OBSERVABLE",f"$.observable.{f}","must be a non-empty string"))
    ex=d.get("execution")
    if not isinstance(ex,dict): e.append(diag("E_EXECUTION","$.execution","must be an object"))
    else:
        if ex.get("layer") not in LAYERS: e.append(diag("E_LAYER","$.execution.layer",f"must be one of {sorted(LAYERS)}"))
        if ex.get("mode") not in MODES: e.append(diag("E_MODE","$.execution.mode",f"must be one of {sorted(MODES)}"))
        if not strings(ex.get("requirements")): e.append(diag("E_REQUIREMENTS","$.execution.requirements","must be an array of non-empty strings"))
        argv=ex.get("command_argv")
        if not isinstance(argv,list) or not all(nonempty(x) for x in argv): e.append(diag("E_COMMAND","$.execution.command_argv","must be an array of non-empty strings"))
        elif ex.get("mode") != "design-only" and not argv: e.append(diag("E_COMMAND","$.execution.command_argv","executable mode requires a command"))
    attempts=d.get("max_attempts")
    if not isinstance(attempts,int) or isinstance(attempts,bool) or not (1<=attempts<=10): e.append(diag("E_ATTEMPTS","$.max_attempts","must be an integer from 1 to 10"))
    return e

def validate_proof(d:dict[str,Any])->list[dict[str,str]]:
    e=[]
    for f in ("oracle_id","oracle_spec_identity","candidate_identity","verifier_identity","environment_identity"):
        if not nonempty(d.get(f)): e.append(diag("E_REQUIRED",f"$.{f}","must be a non-empty string"))
    state=d.get("execution_state"); verdict=d.get("verdict")
    if state not in EXEC_STATES: e.append(diag("E_EXEC_STATE","$.execution_state",f"must be one of {sorted(EXEC_STATES)}"))
    if verdict not in VERDICTS: e.append(diag("E_VERDICT","$.verdict",f"must be one of {sorted(VERDICTS)}"))
    argv=d.get("command_argv")
    if not isinstance(argv,list) or not all(nonempty(x) for x in argv): e.append(diag("E_COMMAND","$.command_argv","must be an array of non-empty strings"))
    for f in ("evidence_refs","test_artifacts"):
        if not strings(d.get(f)): e.append(diag("E_EVIDENCE",f"$.{f}","must be an array of non-empty strings"))
    if d.get("production_mutation_performed") is not False: e.append(diag("E_PRODUCTION_MUTATION","$.production_mutation_performed","must be false"))
    if d.get("criteria_changed") is not False: e.append(diag("E_CRITERIA_DRIFT","$.criteria_changed","must be false"))
    executed=state in {"pass","fail"}
    if executed and (not argv or d.get("exit_code") is None): e.append(diag("E_EXEC_EVIDENCE","$","executed result requires command_argv and exit_code"))
    if verdict=="proven" and state!="pass": e.append(diag("E_VERDICT_STATE","$.verdict","proven requires execution_state=pass"))
    if verdict=="rejected" and state!="fail": e.append(diag("E_VERDICT_STATE","$.verdict","rejected requires execution_state=fail"))
    if verdict in {"proven","rejected"} and not d.get("evidence_refs"): e.append(diag("E_EVIDENCE","$.evidence_refs","proven/rejected requires evidence refs"))
    if verdict=="blocked" and state!="blocked": e.append(diag("E_VERDICT_STATE","$.verdict","blocked verdict requires execution_state=blocked"))
    if verdict=="not-run" and state!="not-run": e.append(diag("E_VERDICT_STATE","$.verdict","not-run verdict requires execution_state=not-run"))
    return e

def validate(d:Any)->dict[str,Any]:
    if not isinstance(d,dict): return {"validator":"test-oracle-artifact-validator/v1","status":"fail","artifact_sha256":None,"errors":[diag("E_ROOT","$","must be an object")]}
    c=d.get("contract")
    if c=="test-oracle-spec/v1": errors=validate_spec(d)
    elif c=="test-oracle-proof/v1": errors=validate_proof(d)
    else: errors=[diag("E_CONTRACT","$.contract","must be test-oracle-spec/v1 or test-oracle-proof/v1")]
    return {"validator":"test-oracle-artifact-validator/v1","status":"pass" if not errors else "fail","artifact_sha256":identity(d),"errors":errors}

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("artifact"); ap.add_argument("--json",dest="out")
    a=ap.parse_args()
    try: report=validate(json.loads(Path(a.artifact).read_text(encoding="utf-8")))
    except Exception as exc: report={"validator":"test-oracle-artifact-validator/v1","status":"fail","artifact_sha256":None,"errors":[diag("E_PARSE","$",str(exc))]}
    payload=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
    if a.out: Path(a.out).write_text(payload,encoding="utf-8")
    print(payload,end="")
    return 0 if report["status"]=="pass" else 1
if __name__=="__main__": raise SystemExit(main())
