"""Reference-only artifact/evidence catalog; never emits validation approval."""
from __future__ import annotations
import time
from .common import HASH_RE, RuntimeFault, bounded, confined, fields, file_hash, number, read_bytes, safe_text, sha, strict_json

OWNERS = {"magia","mago","nomia","verifier","analyst","user"}
DIGESTS = {"candidate_digest","environment_digest","action_digest"}


def publish(cache, request: dict) -> dict:
    fields(request, {"kind","path","owner","label"}, DIGESTS | {"ttl_seconds"})
    if not isinstance(request['kind'],str) or not isinstance(request['owner'],str) or request["kind"] not in {"artifact","evidence"} or request["owner"] not in OWNERS:
        raise RuntimeFault("INVALID_INPUT", "Unsupported reference kind or canonical owner.")
    path = confined(cache.workspace, request["path"])
    digest = file_hash(path)
    value = {"path":request["path"],"sha256":digest,"owner":request["owner"],"label":safe_text(request["label"],128),
             "bytes":path.stat().st_size,"observed_at":time.time(),"ttl_seconds":number(request.get("ttl_seconds",86400),1,86400),
             "reuse_policy":"reference-only","producer_authenticated":False}
    for name in DIGESTS:
        x=request.get(name)
        if x is not None and (not isinstance(x,str) or not HASH_RE.fullmatch(x)):
            raise RuntimeFault("INVALID_INPUT", "Expected SHA-256 metadata, not executable instructions.")
        value[name]=x
    if request["kind"] == "evidence":
        receipt = strict_json(read_bytes(path, 4*1024*1024), 4*1024*1024)
        if not isinstance(receipt,dict) or receipt.get("producer",receipt.get("owner")) != request["owner"]:
            raise RuntimeFault("OWNER_MISMATCH", "Receipt producer must match the declared owner; this is not authentication.")
        status=receipt.get("status")
        if not isinstance(status,str) or status not in {"passed","failed","pass","fail","blocked","not-run","inconclusive"}:
            raise RuntimeFault("INVALID_RECEIPT", "Receipt must declare a supported observed status.")
        value["observed_status"]=status
        value["receipt_schema"]=str(receipt.get("schema",receipt.get("schema_version","unknown")))[:128]
        candidates=receipt.get("candidate_files",{})
        if not isinstance(candidates,dict) or len(candidates)>4096:
            raise RuntimeFault("INVALID_RECEIPT", "Candidate pins must be a bounded map.")
        for rel,pin in candidates.items():
            confined(cache.workspace,rel)
            if not isinstance(pin,str) or not HASH_RE.fullmatch(pin):
                raise RuntimeFault("INVALID_RECEIPT", "Candidate file pins require SHA-256.")
        value["candidate_files"]=candidates
        roots=receipt.get("request",{}).get("candidate_roots",[]) if isinstance(receipt.get("request",{}),dict) else []
        if not isinstance(roots,list) or len(roots)>32 or any(not isinstance(r,str) for r in roots):
            raise RuntimeFault('INVALID_RECEIPT','Candidate roots must be a bounded path array.')
        for root in roots:confined(cache.workspace,root)
        value["candidate_roots"]=roots
        if candidates:
            computed=sha(candidates)
            if value["candidate_digest"] is not None and value["candidate_digest"] != computed:
                raise RuntimeFault("INVALID_RECEIPT", "Declared candidate digest differs from receipt pins.")
            value["candidate_digest"]=computed
    key=cache.put(request["kind"],value)
    return {"status":"indexed","id":key,"uri":request["kind"]+"://"+key,"reuse_policy":"reference-only"}


def freshness(cache, value: dict) -> str:
    try:
        if file_hash(confined(cache.workspace,value["path"])) != value["sha256"]:
            return "stale"
        age=time.time()-value["observed_at"]
        if age < -5 or age > value["ttl_seconds"]:
            return "expired"
        pins=value.get("candidate_files",{})
        for rel,pin in pins.items():
            if file_hash(confined(cache.workspace,rel)) != pin:
                return "stale"
        if value.get("candidate_roots"):
            from .actions import inventory
            if inventory(cache,value["candidate_roots"]) != pins:
                return "stale"
        return "current"
    except (RuntimeFault,OSError,KeyError,TypeError):
        return "unavailable"


def query(cache, request: dict) -> dict:
    fields(request,{"kind"},{"ids","owner","label","budget_bytes"} | DIGESTS)
    kind=request["kind"]
    if not isinstance(kind,str) or kind not in {"artifact","evidence"}:
        raise RuntimeFault("INVALID_INPUT", "Only artifact or evidence indexes can be queried.")
    ids=request.get("ids")
    if ids is None:
        ids=cache.keys(kind)
    if not isinstance(ids,list) or len(ids)>4096:
        raise RuntimeFault("INVALID_INPUT", "Use a bounded list of object IDs.")
    if any(not isinstance(k,str) for k in ids) or len(set(ids)) != len(ids):
        raise RuntimeFault('INVALID_INPUT','Reference IDs must be distinct strings.')
    records=[]
    for key in ids:
        value=cache.get(kind,key)
        if any(value.get(f)!=request[f] for f in DIGESTS | {"owner","label"} if f in request):
            continue
        records.append({"id":key,"uri":kind+"://"+key,"path":value["path"],"sha256":value["sha256"],
                        "owner":value["owner"],"label":value["label"],"freshness":freshness(cache,value),
                        "observed_status":value.get("observed_status"),"reuse_policy":"reference-only",
                        "domain_approval":False,"producer_authenticated":False})
    return bounded({"status":"ok","records":records,"canonical_mutation_performed":False},
                   number(request.get("budget_bytes",8192),128,65536))
