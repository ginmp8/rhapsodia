#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

CLAIM_TYPES={"behavior","authorization","api-contract","event-contract","data-invariant","migration","concurrency","idempotency","retry","cli","ui-behavior","security","other"}
LAYERS={"existing-focused-test","integration-public-stack","contract-boundary","component-unit","static"}
MODES={"design-only","existing-test","generated-test","integration","contract","static"}
EXEC_STATES={"pass","fail","blocked","not-run"}
VERDICTS={"proven","rejected","inconclusive","blocked","not-run"}
OUTCOME_KINDS={"expected-observation","oracle-rejection","harness-error","environment-error","timeout","cancelled","unstable-observation","not-run"}
STRATEGIES={"specified","invariant","property","model-based","metamorphic","differential","statistical","implicit"}
ORIGINS={"human","specification","existing-test","generated","llm-assisted","inferred"}
STRENGTH_CHECKS={"not-required","planned","negative-control","oracle-gap","mutation"}
NONDET_MODES={"deterministic","controlled","probabilistic"}
SEED_POLICIES={"fixed","recorded","not-applicable"}
ORDER_POLICIES={"fixed","systematic","recorded","not-applicable"}
CLOCK_POLICIES={"controlled","recorded","real","not-applicable"}
SCHEDULER_POLICIES={"controlled","systematic","recorded","default","not-applicable"}
IDENTITY_RE=re.compile(r"^(?:sha256:[0-9a-f]{64}|vcs:.+|version:.+|declared:.+)$")
CANDIDATE_IDENTITY_RE=re.compile(r"^(?:sha256:[0-9a-f]{64}|vcs:.+|version:.+|declared:.+|unbound)$")
SHA256_ID_RE=re.compile(r"^sha256:[0-9a-f]{64}$")

V1_SPEC_FIELDS={"contract","oracle_id","claim","claim_type","source_identity","candidate_identity","target_scope","verification_write_scope","protected_paths","observable","execution","evaluator_identity","max_attempts"}
V1_PROOF_FIELDS={"contract","oracle_id","oracle_spec_identity","candidate_identity","verifier_identity","environment_identity","execution_state","verdict","command_argv","exit_code","evidence_refs","test_artifacts","production_mutation_performed","criteria_changed"}
V2_SPEC_FIELDS={"contract","oracle_id","claim","claim_type","source_identity","candidate_identity","target_scope","verification_write_scope","protected_paths","oracle_strategy","oracle_origin","quality","observable","execution","nondeterminism","evaluator_identity","max_attempts"}
V2_PROOF_FIELDS={"contract","oracle_id","oracle_spec_identity","candidate_identity","verifier_identity","environment_identity","attempt","execution_state","outcome_kind","verdict","command_argv","exit_code","observation","attempts","evidence_refs","test_artifacts","production_mutation_performed","criteria_changed"}
OBSERVABLE_FIELDS={"setup","input","action","expected","failure_signal"}
EXECUTION_FIELDS={"layer","mode","requirements","working_directory","command_argv"}
STRATEGY_FIELDS={"type","rationale","assumptions","blind_spots","property","relation","references","decision_rule","model_identity"}
ORIGIN_FIELDS={"type","generator_identity","independent_validation"}
QUALITY_FIELDS={"soundness_assumptions","completeness_limits","strength_check","strength_rationale"}
NONDET_FIELDS={"mode","repetitions","seed_policy","order_policy","clock_policy","scheduler_policy","statistical_rule"}
OBSERVATION_FIELDS={"expected_observed","failure_observed","summary","evidence_refs"}
ATTEMPT_FIELDS={"attempt","execution_state","outcome_kind","exit_code"}


def nonempty(v:Any)->bool:
    return isinstance(v,str) and bool(v.strip())

def strings(v:Any)->bool:
    return isinstance(v,list) and all(nonempty(x) for x in v)

def diag(code:str,path:str,message:str)->dict[str,str]:
    return {"code":code,"path":path,"message":message}

def reject_unknown(d:Any,allowed:set[str],path:str,e:list[dict[str,str]])->None:
    if isinstance(d,dict):
        for key in sorted(set(d)-allowed):
            e.append(diag("E_SCHEMA_ADDITIONAL_PROPERTY",f"{path}.{key}","property is not allowed by the schema"))

def reject_duplicates(v:Any,path:str,e:list[dict[str,str]])->None:
    if isinstance(v,list) and all(isinstance(x,str) for x in v) and len(v)!=len(set(v)):
        e.append(diag("E_DUPLICATE",path,"items must be unique"))

def canonical_json_bytes(data:Any)->bytes:
    return json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def identity(data:Any)->str:
    return hashlib.sha256(canonical_json_bytes(data)).hexdigest()

def valid_identity(value:Any, *, candidate:bool=False, sha256_only:bool=False)->bool:
    if not nonempty(value): return False
    if sha256_only: return bool(SHA256_ID_RE.fullmatch(value))
    return bool((CANDIDATE_IDENTITY_RE if candidate else IDENTITY_RE).fullmatch(value))

def validate_scope_arrays(d:dict[str,Any], e:list[dict[str,str]])->None:
    for f in ("target_scope","verification_write_scope","protected_paths"):
        if not strings(d.get(f)):
            e.append(diag("E_SCOPE",f"$.{f}","must be an array of non-empty strings"))
        else:
            reject_duplicates(d.get(f),f"$.{f}",e)
    if not d.get("target_scope"):
        e.append(diag("E_TARGET_SCOPE","$.target_scope","must not be empty"))

def validate_observable(obs:Any,e:list[dict[str,str]])->None:
    if not isinstance(obs,dict):
        e.append(diag("E_OBSERVABLE","$.observable","must be an object")); return
    reject_unknown(obs,OBSERVABLE_FIELDS,"$.observable",e)
    for f in OBSERVABLE_FIELDS:
        if not nonempty(obs.get(f)):
            e.append(diag("E_OBSERVABLE",f"$.observable.{f}","must be a non-empty string"))

def validate_execution(ex:Any,e:list[dict[str,str]])->None:
    if not isinstance(ex,dict):
        e.append(diag("E_EXECUTION","$.execution","must be an object")); return
    reject_unknown(ex,EXECUTION_FIELDS,"$.execution",e)
    if ex.get("layer") not in LAYERS:
        e.append(diag("E_LAYER","$.execution.layer",f"must be one of {sorted(LAYERS)}"))
    if ex.get("mode") not in MODES:
        e.append(diag("E_MODE","$.execution.mode",f"must be one of {sorted(MODES)}"))
    if not strings(ex.get("requirements")):
        e.append(diag("E_REQUIREMENTS","$.execution.requirements","must be an array of non-empty strings"))
    else:
        reject_duplicates(ex.get("requirements"),"$.execution.requirements",e)
    if "working_directory" in ex and not nonempty(ex.get("working_directory")):
        e.append(diag("E_WORKING_DIRECTORY","$.execution.working_directory","must be a non-empty string when present"))
    argv=ex.get("command_argv")
    if not isinstance(argv,list) or not all(nonempty(x) for x in argv):
        e.append(diag("E_COMMAND","$.execution.command_argv","must be an array of non-empty strings"))
    elif ex.get("mode") != "design-only" and not argv:
        e.append(diag("E_COMMAND","$.execution.command_argv","executable mode requires a command"))

def validate_attempt_limit(value:Any,e:list[dict[str,str]], maximum:int)->None:
    if not isinstance(value,int) or isinstance(value,bool) or not (1<=value<=maximum):
        e.append(diag("E_ATTEMPTS","$.max_attempts",f"must be an integer from 1 to {maximum}"))


def validate_spec_v1(d:dict[str,Any])->list[dict[str,str]]:
    e=[]
    reject_unknown(d,V1_SPEC_FIELDS,"$",e)
    for f in ("oracle_id","claim","source_identity","candidate_identity","evaluator_identity"):
        if not nonempty(d.get(f)): e.append(diag("E_REQUIRED",f"$.{f}","must be a non-empty string"))
    if d.get("claim_type") not in CLAIM_TYPES: e.append(diag("E_CLAIM_TYPE","$.claim_type",f"must be one of {sorted(CLAIM_TYPES)}"))
    validate_scope_arrays(d,e); validate_observable(d.get("observable"),e); validate_execution(d.get("execution"),e); validate_attempt_limit(d.get("max_attempts"),e,10)
    return e


def validate_proof_v1(d:dict[str,Any])->list[dict[str,str]]:
    e=[]
    reject_unknown(d,V1_PROOF_FIELDS,"$",e)
    for f in ("oracle_id","oracle_spec_identity","candidate_identity","verifier_identity","environment_identity"):
        if not nonempty(d.get(f)): e.append(diag("E_REQUIRED",f"$.{f}","must be a non-empty string"))
    state=d.get("execution_state"); verdict=d.get("verdict")
    if state not in EXEC_STATES: e.append(diag("E_EXEC_STATE","$.execution_state",f"must be one of {sorted(EXEC_STATES)}"))
    if verdict not in VERDICTS: e.append(diag("E_VERDICT","$.verdict",f"must be one of {sorted(VERDICTS)}"))
    argv=d.get("command_argv")
    if not isinstance(argv,list) or not all(nonempty(x) for x in argv): e.append(diag("E_COMMAND","$.command_argv","must be an array of non-empty strings"))
    for f in ("evidence_refs","test_artifacts"):
        if not strings(d.get(f)): e.append(diag("E_EVIDENCE",f"$.{f}","must be an array of non-empty strings"))
        else: reject_duplicates(d.get(f),f"$.{f}",e)
    exit_code=d.get("exit_code")
    valid_exit_code=exit_code is None or (isinstance(exit_code,int) and not isinstance(exit_code,bool))
    if not valid_exit_code: e.append(diag("E_EXIT_CODE","$.exit_code","must be an integer or null"))
    if d.get("production_mutation_performed") is not False: e.append(diag("E_PRODUCTION_MUTATION","$.production_mutation_performed","must be false"))
    if d.get("criteria_changed") is not False: e.append(diag("E_CRITERIA_DRIFT","$.criteria_changed","must be false"))
    executed=state in {"pass","fail"}
    if executed and (not argv or exit_code is None): e.append(diag("E_EXEC_EVIDENCE","$","executed result requires command_argv and exit_code"))
    if valid_exit_code and isinstance(exit_code,int) and not isinstance(exit_code,bool):
        if state=="pass" and exit_code!=0: e.append(diag("E_EXIT_CODE_STATE","$.exit_code","execution_state=pass requires exit_code=0"))
        if state=="fail" and exit_code==0: e.append(diag("E_EXIT_CODE_STATE","$.exit_code","execution_state=fail requires a non-zero exit_code"))
    if verdict=="proven" and state!="pass": e.append(diag("E_VERDICT_STATE","$.verdict","proven requires execution_state=pass"))
    if verdict=="rejected" and state!="fail": e.append(diag("E_VERDICT_STATE","$.verdict","rejected requires execution_state=fail"))
    if verdict in {"proven","rejected"} and not d.get("evidence_refs"): e.append(diag("E_EVIDENCE","$.evidence_refs","proven/rejected requires evidence refs"))
    if verdict=="blocked" and state!="blocked": e.append(diag("E_VERDICT_STATE","$.verdict","blocked verdict requires execution_state=blocked"))
    if verdict=="not-run" and state!="not-run": e.append(diag("E_VERDICT_STATE","$.verdict","not-run verdict requires execution_state=not-run"))
    return e


def validate_strategy(value:Any,e:list[dict[str,str]])->None:
    if not isinstance(value,dict): e.append(diag("E_STRATEGY","$.oracle_strategy","must be an object")); return
    reject_unknown(value,STRATEGY_FIELDS,"$.oracle_strategy",e)
    st=value.get("type")
    if st not in STRATEGIES: e.append(diag("E_STRATEGY","$.oracle_strategy.type",f"must be one of {sorted(STRATEGIES)}"))
    if not nonempty(value.get("rationale")): e.append(diag("E_STRATEGY","$.oracle_strategy.rationale","must be a non-empty string"))
    for f in ("assumptions","blind_spots"):
        if not strings(value.get(f)): e.append(diag("E_STRATEGY",f"$.oracle_strategy.{f}","must be an array of non-empty strings"))
        else: reject_duplicates(value.get(f),f"$.oracle_strategy.{f}",e)
    if st in {"property","invariant"} and not nonempty(value.get("property")):
        e.append(diag("E_STRATEGY_DETAIL","$.oracle_strategy.property",f"{st} strategy requires property"))
    if st=="metamorphic" and not nonempty(value.get("relation")):
        e.append(diag("E_STRATEGY_DETAIL","$.oracle_strategy.relation","metamorphic strategy requires relation"))
    if st=="differential":
        refs=value.get("references")
        if not strings(refs) or len(refs)<2: e.append(diag("E_STRATEGY_DETAIL","$.oracle_strategy.references","differential strategy requires at least two references"))
        if not nonempty(value.get("decision_rule")): e.append(diag("E_STRATEGY_DETAIL","$.oracle_strategy.decision_rule","differential strategy requires decision_rule"))
    if st=="model-based" and not valid_identity(value.get("model_identity")):
        e.append(diag("E_STRATEGY_DETAIL","$.oracle_strategy.model_identity","model-based strategy requires a typed model identity"))
    if st=="statistical" and not nonempty(value.get("decision_rule")):
        e.append(diag("E_STRATEGY_DETAIL","$.oracle_strategy.decision_rule","statistical strategy requires decision_rule"))


def validate_origin(value:Any,e:list[dict[str,str]])->None:
    if not isinstance(value,dict): e.append(diag("E_ORACLE_ORIGIN","$.oracle_origin","must be an object")); return
    reject_unknown(value,ORIGIN_FIELDS,"$.oracle_origin",e)
    origin=value.get("type")
    if origin not in ORIGINS: e.append(diag("E_ORACLE_ORIGIN","$.oracle_origin.type",f"must be one of {sorted(ORIGINS)}"))
    if not nonempty(value.get("generator_identity")): e.append(diag("E_ORACLE_ORIGIN","$.oracle_origin.generator_identity","must be a non-empty string"))
    independent=value.get("independent_validation")
    if not isinstance(independent,str): e.append(diag("E_ORACLE_ORIGIN","$.oracle_origin.independent_validation","must be a string"))
    if origin in {"llm-assisted","generated","inferred"} and not nonempty(independent):
        e.append(diag("E_ORACLE_ORIGIN_VALIDATION","$.oracle_origin.independent_validation",f"{origin} oracle origin requires independent validation"))


def validate_quality(value:Any,e:list[dict[str,str]])->None:
    if not isinstance(value,dict): e.append(diag("E_QUALITY","$.quality","must be an object")); return
    reject_unknown(value,QUALITY_FIELDS,"$.quality",e)
    for f in ("soundness_assumptions","completeness_limits"):
        if not strings(value.get(f)): e.append(diag("E_QUALITY",f"$.quality.{f}","must be an array of non-empty strings"))
        else: reject_duplicates(value.get(f),f"$.quality.{f}",e)
    if value.get("strength_check") not in STRENGTH_CHECKS: e.append(diag("E_QUALITY","$.quality.strength_check",f"must be one of {sorted(STRENGTH_CHECKS)}"))
    if not nonempty(value.get("strength_rationale")): e.append(diag("E_QUALITY","$.quality.strength_rationale","must be a non-empty string"))


def validate_nondeterminism(value:Any,e:list[dict[str,str]],strategy:Any)->None:
    if not isinstance(value,dict): e.append(diag("E_NONDETERMINISM","$.nondeterminism","must be an object")); return
    reject_unknown(value,NONDET_FIELDS,"$.nondeterminism",e)
    mode=value.get("mode")
    if mode not in NONDET_MODES: e.append(diag("E_NONDETERMINISM","$.nondeterminism.mode",f"must be one of {sorted(NONDET_MODES)}"))
    reps=value.get("repetitions")
    if not isinstance(reps,int) or isinstance(reps,bool) or not (1<=reps<=100): e.append(diag("E_NONDETERMINISM","$.nondeterminism.repetitions","must be an integer from 1 to 100"))
    policies=(("seed_policy",SEED_POLICIES),("order_policy",ORDER_POLICIES),("clock_policy",CLOCK_POLICIES),("scheduler_policy",SCHEDULER_POLICIES))
    for f,allowed in policies:
        if value.get(f) not in allowed: e.append(diag("E_NONDETERMINISM",f"$.nondeterminism.{f}",f"must be one of {sorted(allowed)}"))
    st=strategy.get("type") if isinstance(strategy,dict) else None
    if (mode=="probabilistic" or st=="statistical") and not nonempty(value.get("statistical_rule")):
        e.append(diag("E_STATISTICAL_RULE","$.nondeterminism.statistical_rule","probabilistic/statistical oracle requires a predeclared statistical_rule"))
    if st=="statistical" and mode!="probabilistic":
        e.append(diag("E_STATISTICAL_RULE","$.nondeterminism.mode","statistical strategy requires probabilistic nondeterminism mode"))


def validate_spec_v2(d:dict[str,Any])->list[dict[str,str]]:
    e=[]; reject_unknown(d,V2_SPEC_FIELDS,"$",e)
    for f in ("oracle_id","claim"):
        if not nonempty(d.get(f)): e.append(diag("E_REQUIRED",f"$.{f}","must be a non-empty string"))
    if d.get("claim_type") not in CLAIM_TYPES: e.append(diag("E_CLAIM_TYPE","$.claim_type",f"must be one of {sorted(CLAIM_TYPES)}"))
    if not valid_identity(d.get("source_identity")): e.append(diag("E_IDENTITY","$.source_identity","must use sha256:, vcs:, version:, or declared: identity"))
    if not valid_identity(d.get("candidate_identity"),candidate=True): e.append(diag("E_IDENTITY","$.candidate_identity","must use a typed identity or unbound"))
    if not valid_identity(d.get("evaluator_identity")): e.append(diag("E_IDENTITY","$.evaluator_identity","must use sha256:, vcs:, version:, or declared: identity"))
    validate_scope_arrays(d,e)
    validate_strategy(d.get("oracle_strategy"),e)
    validate_origin(d.get("oracle_origin"),e)
    validate_quality(d.get("quality"),e)
    validate_observable(d.get("observable"),e)
    validate_execution(d.get("execution"),e)
    validate_nondeterminism(d.get("nondeterminism"),e,d.get("oracle_strategy"))
    validate_attempt_limit(d.get("max_attempts"),e,100)
    return e


def validate_attempt_record(value:Any,path:str,e:list[dict[str,str]])->None:
    if not isinstance(value,dict): e.append(diag("E_ATTEMPT_RECORD",path,"must be an object")); return
    reject_unknown(value,ATTEMPT_FIELDS,path,e)
    n=value.get("attempt")
    if not isinstance(n,int) or isinstance(n,bool) or n<1: e.append(diag("E_ATTEMPT_RECORD",f"{path}.attempt","must be a positive integer"))
    if value.get("execution_state") not in EXEC_STATES: e.append(diag("E_EXEC_STATE",f"{path}.execution_state",f"must be one of {sorted(EXEC_STATES)}"))
    if value.get("outcome_kind") not in OUTCOME_KINDS: e.append(diag("E_OUTCOME",f"{path}.outcome_kind",f"must be one of {sorted(OUTCOME_KINDS)}"))
    code=value.get("exit_code")
    if code is not None and (not isinstance(code,int) or isinstance(code,bool)): e.append(diag("E_EXIT_CODE",f"{path}.exit_code","must be an integer or null"))


def validate_proof_v2(d:dict[str,Any])->list[dict[str,str]]:
    e=[]; reject_unknown(d,V2_PROOF_FIELDS,"$",e)
    if not nonempty(d.get("oracle_id")): e.append(diag("E_REQUIRED","$.oracle_id","must be a non-empty string"))
    if not valid_identity(d.get("oracle_spec_identity"),sha256_only=True): e.append(diag("E_IDENTITY","$.oracle_spec_identity","must be sha256:<64 lowercase hex>"))
    for f in ("candidate_identity","verifier_identity","environment_identity"):
        if not valid_identity(d.get(f)): e.append(diag("E_IDENTITY",f"$.{f}","must use sha256:, vcs:, version:, or declared: identity"))
    attempt=d.get("attempt")
    if not isinstance(attempt,int) or isinstance(attempt,bool) or attempt<1: e.append(diag("E_ATTEMPT","$.attempt","must be a positive integer"))
    state=d.get("execution_state"); outcome=d.get("outcome_kind"); verdict=d.get("verdict")
    if state not in EXEC_STATES: e.append(diag("E_EXEC_STATE","$.execution_state",f"must be one of {sorted(EXEC_STATES)}"))
    if outcome not in OUTCOME_KINDS: e.append(diag("E_OUTCOME","$.outcome_kind",f"must be one of {sorted(OUTCOME_KINDS)}"))
    if verdict not in VERDICTS: e.append(diag("E_VERDICT","$.verdict",f"must be one of {sorted(VERDICTS)}"))
    argv=d.get("command_argv")
    if not isinstance(argv,list) or not all(nonempty(x) for x in argv): e.append(diag("E_COMMAND","$.command_argv","must be an array of non-empty strings"))
    code=d.get("exit_code")
    if code is not None and (not isinstance(code,int) or isinstance(code,bool)): e.append(diag("E_EXIT_CODE","$.exit_code","must be an integer or null"))
    obs=d.get("observation")
    if not isinstance(obs,dict): e.append(diag("E_OBSERVATION","$.observation","must be an object"))
    else:
        reject_unknown(obs,OBSERVATION_FIELDS,"$.observation",e)
        if not isinstance(obs.get("expected_observed"),bool): e.append(diag("E_OBSERVATION","$.observation.expected_observed","must be boolean"))
        if not isinstance(obs.get("failure_observed"),bool): e.append(diag("E_OBSERVATION","$.observation.failure_observed","must be boolean"))
        if not nonempty(obs.get("summary")): e.append(diag("E_OBSERVATION","$.observation.summary","must be a non-empty string"))
        refs=obs.get("evidence_refs")
        if not strings(refs) or not refs: e.append(diag("E_OBSERVATION","$.observation.evidence_refs","must contain at least one evidence ref"))
        else: reject_duplicates(refs,"$.observation.evidence_refs",e)
    attempts=d.get("attempts")
    if not isinstance(attempts,list) or not attempts:
        e.append(diag("E_ATTEMPTS","$.attempts","must contain at least one attempt record"))
    else:
        for i,rec in enumerate(attempts): validate_attempt_record(rec,f"$.attempts[{i}]",e)
        nums=[x.get("attempt") for x in attempts if isinstance(x,dict) and isinstance(x.get("attempt"),int) and not isinstance(x.get("attempt"),bool)]
        if len(nums)!=len(set(nums)): e.append(diag("E_DUPLICATE","$.attempts","attempt numbers must be unique"))
        if nums and nums!=sorted(nums): e.append(diag("E_ATTEMPT_ORDER","$.attempts","attempts must be ordered by attempt number"))
        if nums and isinstance(attempt,int) and nums[-1]!=attempt: e.append(diag("E_ATTEMPT_LAST","$.attempt","must equal the last recorded attempt"))
    for f in ("evidence_refs","test_artifacts"):
        refs=d.get(f)
        if not strings(refs): e.append(diag("E_EVIDENCE",f"$.{f}","must be an array of non-empty strings"))
        else: reject_duplicates(refs,f"$.{f}",e)
    if verdict in {"proven","rejected"} and not d.get("evidence_refs"): e.append(diag("E_EVIDENCE","$.evidence_refs","proven/rejected requires evidence refs"))
    if d.get("production_mutation_performed") is not False: e.append(diag("E_PRODUCTION_MUTATION","$.production_mutation_performed","must be false"))
    if d.get("criteria_changed") is not False: e.append(diag("E_CRITERIA_DRIFT","$.criteria_changed","must be false"))

    executed=state in {"pass","fail"}
    if executed and (not argv or code is None): e.append(diag("E_EXEC_EVIDENCE","$","executed result requires command_argv and exit_code"))
    if state=="pass" and isinstance(code,int) and code!=0: e.append(diag("E_EXIT_CODE_STATE","$.exit_code","execution_state=pass requires exit_code=0"))
    if state=="fail" and isinstance(code,int) and code==0: e.append(diag("E_EXIT_CODE_STATE","$.exit_code","execution_state=fail requires non-zero exit_code"))
    if state in {"blocked","not-run"} and code is not None: e.append(diag("E_EXIT_CODE_STATE","$.exit_code",f"execution_state={state} requires exit_code=null"))

    expected=obs.get("expected_observed") if isinstance(obs,dict) else None
    failure=obs.get("failure_observed") if isinstance(obs,dict) else None
    if verdict=="proven":
        if state!="pass" or outcome!="expected-observation" or expected is not True or failure is not False:
            e.append(diag("E_OUTCOME_VERDICT","$.verdict","proven requires pass + expected-observation + expected_observed=true + failure_observed=false"))
    if verdict=="rejected":
        if state!="fail" or outcome!="oracle-rejection" or failure is not True or expected is not False:
            e.append(diag("E_OUTCOME_VERDICT","$.verdict","rejected requires fail + oracle-rejection + failure_observed=true + expected_observed=false"))
    if outcome in {"harness-error","environment-error","timeout","cancelled","unstable-observation"} and verdict in {"proven","rejected"}:
        e.append(diag("E_OUTCOME_VERDICT","$.verdict",f"{outcome} cannot yield proven or rejected"))
    if verdict=="blocked" and state!="blocked": e.append(diag("E_VERDICT_STATE","$.verdict","blocked verdict requires execution_state=blocked"))
    if verdict=="not-run" and (state!="not-run" or outcome!="not-run"): e.append(diag("E_VERDICT_STATE","$.verdict","not-run verdict requires execution_state=not-run and outcome_kind=not-run"))
    return e


def validate(d:Any)->dict[str,Any]:
    if not isinstance(d,dict):
        return {"validator":"test-oracle-artifact-validator/v2","status":"fail","artifact_sha256":None,"contract":None,"legacy":False,"warnings":[],"errors":[diag("E_ROOT","$","must be an object")]}
    c=d.get("contract"); warnings=[]; legacy=False
    if c=="test-oracle-spec/v1": errors=validate_spec_v1(d); legacy=True; warnings.append(diag("W_LEGACY_CONTRACT","$.contract","v1 is review-compatible only; emit v2 for new material proofs"))
    elif c=="test-oracle-proof/v1": errors=validate_proof_v1(d); legacy=True; warnings.append(diag("W_LEGACY_CONTRACT","$.contract","v1 cannot establish strict cross-artifact proof binding; emit v2 for new material proofs"))
    elif c=="test-oracle-spec/v2": errors=validate_spec_v2(d)
    elif c=="test-oracle-proof/v2": errors=validate_proof_v2(d)
    else: errors=[diag("E_CONTRACT","$.contract","must be test-oracle-spec/v1|v2 or test-oracle-proof/v1|v2")]
    return {"validator":"test-oracle-artifact-validator/v2","status":"pass" if not errors else "fail","artifact_sha256":identity(d),"contract":c,"legacy":legacy,"warnings":warnings,"errors":errors}


def main()->int:
    ap=argparse.ArgumentParser(description="Validate standalone Test Oracle Engineering spec/proof artifacts.")
    ap.add_argument("artifact"); ap.add_argument("--json",dest="out")
    a=ap.parse_args()
    try: report=validate(json.loads(Path(a.artifact).read_text(encoding="utf-8")))
    except Exception as exc: report={"validator":"test-oracle-artifact-validator/v2","status":"fail","artifact_sha256":None,"contract":None,"legacy":False,"warnings":[],"errors":[diag("E_PARSE","$",str(exc))]}
    payload=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
    if a.out: Path(a.out).write_text(payload,encoding="utf-8")
    print(payload,end="")
    return 0 if report["status"]=="pass" else 1

if __name__=="__main__": raise SystemExit(main())
