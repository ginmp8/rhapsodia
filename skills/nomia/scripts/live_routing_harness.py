#!/usr/bin/env python3
"""Prepare, evaluate, and validate externally executed live-model routing evidence."""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

ROLES=("mago","magia","nomia")
OBSERVED_LABELS=("mago","magia","nomia","none")


def sha256(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def load(path:Path)->dict[str,Any]:
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise ValueError(f"{path} must contain an object")
    return value

def atomic(path:Path,value:dict[str,Any]):
    path=path.resolve(); path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix=f".{path.name}.",suffix=".tmp",dir=str(path.parent))
    try:
        with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as f:
            f.write(json.dumps(value,indent=2,sort_keys=True)+"\n"); f.flush(); os.fsync(f.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name): os.unlink(name)

def tree_hash(root:Path)->str:
    h=hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.is_symlink(): continue
        rel=p.relative_to(root)
        if any(x in {".git","__pycache__",".pytest_cache"} for x in rel.parts) or p.suffix in {".pyc",".pyo",".zip"}: continue
        r=rel.as_posix().encode(); d=p.read_bytes(); h.update(len(r).to_bytes(4,"big")); h.update(r); h.update(len(d).to_bytes(8,"big")); h.update(d)
    return h.hexdigest()

def corpus_for(roots:dict[str,Path])->tuple[dict[str,Any],str]:
    values=[]
    for role in ROLES:
        path=roots[role]/"evals/ecosystem-routing-scenarios.json"
        if not path.is_file(): raise ValueError(f"missing routing corpus: {path}")
        values.append(path.read_bytes())
    if len(set(values))!=1: raise ValueError("routing corpus differs across packages")
    return json.loads(values[0]),sha256(values[0])

def prepare(roots:dict[str,Path])->dict[str,Any]:
    corpus,digest=corpus_for(roots)
    return {"schema_version":"1.0.0","status":"planned","ecosystem_release":corpus["ecosystem_release"],"corpus_sha256":digest,"skill_tree_hashes":{r:tree_hash(roots[r]) for r in ROLES},"scenario_count":len(corpus["scenarios"]),"scenarios":[{"id":s["id"],"category":s["category"],"prompt":s["prompt"],"expected_first_owner":s["expected_first_owner"],"expected_owner_sequence":s["owner_sequence"]} for s in corpus["scenarios"]],"required_observation_fields":["id","observed_first_owner","observed_owner_sequence","mode_selected","handoff_sequence","explanation_category"],"claims":{"live_model_routing_measured":False,"reason":"No model observations have been supplied."}}

def iso(value:Any)->bool:
    try: datetime.fromisoformat(str(value).replace("Z","+00:00")); return True
    except ValueError: return False

def metrics(rows:list[dict[str,Any]])->tuple[dict[str,Any],dict[str,dict[str,int]]]:
    matrix={e:{o:0 for o in OBSERVED_LABELS} for e in OBSERVED_LABELS}
    for row in rows: matrix[row["expected_first_owner"]][row["observed_first_owner"]]+=1
    per={}
    for role in ROLES:
        tp=matrix[role][role]; fp=sum(matrix[e][role] for e in OBSERVED_LABELS if e!=role); fn=sum(matrix[role][o] for o in OBSERVED_LABELS if o!=role)
        precision=tp/(tp+fp) if tp+fp else None; recall=tp/(tp+fn) if tp+fn else None
        per[role]={"true_positive":tp,"false_positive":fp,"false_negative":fn,"precision":precision,"recall":recall}
    correct=sum(1 for r in rows if r["passed"])
    return {"scenario_accuracy":correct/len(rows),"passed":correct,"failed":len(rows)-correct,"per_owner":per},matrix

def evaluate(request:dict[str,Any],observations:dict[str,Any],corpus:dict[str,Any],corpus_hash:str)->dict[str,Any]:
    if request.get("corpus_sha256")!=corpus_hash: raise ValueError("request corpus hash does not match frozen corpus")
    for field in ("model","run_at","results","evidence_kind"):
        if field not in observations: raise ValueError(f"missing observations.{field}")
    if observations["evidence_kind"] not in {"live-model","fixture"}: raise ValueError("invalid evidence_kind")
    if not iso(observations["run_at"]): raise ValueError("invalid run_at")
    expected={s["id"]:s for s in corpus["scenarios"]}; seen={}
    for item in observations["results"]:
        sid=item.get("id")
        if sid not in expected or sid in seen: raise ValueError(f"invalid or duplicate scenario id: {sid}")
        seen[sid]=item
    if set(seen)!=set(expected): raise ValueError("observations must cover the complete frozen corpus")
    rows=[]; failures=[]
    forbidden_direct=[]
    for sid,exp in expected.items():
        obs=seen[sid]; owner=str(obs.get("observed_first_owner"))
        if owner not in OBSERVED_LABELS: raise ValueError(f"invalid observed owner for {sid}")
        sequence=list(obs.get("observed_owner_sequence") or [])
        handoffs=list(obs.get("handoff_sequence") or [])
        direct=any(a=="nomia" and b=="magia" for a,b in zip(sequence,sequence[1:])) or "nomia_to_magia" in handoffs
        passed=owner==exp["expected_first_owner"] and sequence==exp["owner_sequence"] and not direct
        row={"id":sid,"category":exp["category"],"expected_first_owner":exp["expected_first_owner"],"observed_first_owner":owner,"expected_owner_sequence":exp["owner_sequence"],"observed_owner_sequence":sequence,"mode_selected":obs.get("mode_selected"),"handoff_sequence":handoffs,"explanation_category":str(obs.get("explanation_category") or "unclassified"),"passed":passed}
        rows.append(row)
        if not passed: failures.append({"id":sid,"owner_match":owner==exp["expected_first_owner"],"sequence_match":sequence==exp["owner_sequence"],"forbidden_direct_handoff":direct})
        if direct: forbidden_direct.append(sid)
    m,matrix=metrics(rows)
    kind=observations["evidence_kind"]
    return {"schema_version":"1.0.0","evidence_kind":kind,"model":observations["model"],"run_at":observations["run_at"],"ecosystem_release":request["ecosystem_release"],"corpus_sha256":corpus_hash,"skill_tree_hashes":request["skill_tree_hashes"],"scenario_count":len(rows),"results":rows,"confusion_matrix":matrix,"metrics":m,"failures":failures,"claims":{"structural_corpus_validated":True,"live_routing_measured":kind=="live-model","precision_recall_supported":kind=="live-model"},"forbidden_direct_handoff_scenarios":forbidden_direct}

def validate_result(result:dict[str,Any],corpus_hash:str)->list[str]:
    errors=[]
    required=("schema_version","evidence_kind","model","run_at","ecosystem_release","corpus_sha256","skill_tree_hashes","scenario_count","results","confusion_matrix","metrics","failures","claims")
    for f in required:
        if f not in result: errors.append(f"missing {f}")
    if result.get("schema_version")!="1.0.0": errors.append("schema_version must be 1.0.0")
    if result.get("corpus_sha256")!=corpus_hash: errors.append("corpus hash mismatch")
    kind=result.get("evidence_kind")
    if kind not in {"live-model","fixture"}: errors.append("invalid evidence_kind")
    claims=result.get("claims") or {}
    expected=kind=="live-model"
    if claims.get("live_routing_measured") is not expected or claims.get("precision_recall_supported") is not expected: errors.append("claim/evidence-kind mismatch")
    if result.get("forbidden_direct_handoff_scenarios"): errors.append("forbidden direct Nomia-to-Magia routing observed")
    return errors

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest="cmd",required=True)
    prep=sub.add_parser("prepare")
    for r in ROLES: prep.add_argument(f"--{r}",required=True)
    prep.add_argument("--output",required=True)
    ev=sub.add_parser("evaluate")
    for r in ROLES: ev.add_argument(f"--{r}",required=True)
    ev.add_argument("--request",required=True); ev.add_argument("--observations",required=True); ev.add_argument("--output",required=True)
    val=sub.add_parser("validate"); val.add_argument("--input",required=True); val.add_argument("--corpus",required=True); val.add_argument("--json-output")
    args=p.parse_args(argv)
    try:
        if args.cmd=="validate":
            corpus_bytes=Path(args.corpus).read_bytes(); errors=validate_result(load(Path(args.input)),sha256(corpus_bytes)); result={"status":"pass" if not errors else "fail","errors":errors};
            if args.json_output: atomic(Path(args.json_output),result)
            print(json.dumps(result,indent=2,sort_keys=True)); return 0 if not errors else 1
        roots={r:Path(getattr(args,r)).resolve() for r in ROLES}; corpus,digest=corpus_for(roots)
        if args.cmd=="prepare": result=prepare(roots)
        else: result=evaluate(load(Path(args.request)),load(Path(args.observations)),corpus,digest)
        atomic(Path(args.output),result); print(json.dumps(result,indent=2,sort_keys=True)); return 0
    except (OSError,ValueError,KeyError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"error","error":str(exc)},indent=2)); return 2
if __name__=="__main__": raise SystemExit(main())
