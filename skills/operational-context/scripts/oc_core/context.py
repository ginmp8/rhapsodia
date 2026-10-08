"""Deterministic, byte-bounded task packs with mandatory references and live pins."""
from __future__ import annotations
import hashlib
from .common import HASH_RE, RuntimeFault, bounded, canonical, confined, fields, file_hash, number, read_bytes, safe_text, sha


def ref(cache, value: dict, include_text: bool = False) -> dict:
    fields(value, {"path"}, {"start_line", "end_line", "role"})
    path = confined(cache.workspace, value["path"])
    raw = read_bytes(path, 8 * 1024 * 1024)
    result = {"path": value["path"], "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
              "role": value.get("role", "source")}
    if not isinstance(result['role'],str) or result["role"] not in {"source", "contract", "evidence", "blocker", "instruction", "tool-schema"}:
        raise RuntimeFault("INVALID_INPUT", "Unsupported reference role.")
    if ("start_line" in value) != ("end_line" in value):
        raise RuntimeFault("INVALID_INPUT", "Both line bounds are required.")
    if "start_line" in value or include_text:
        try:
            lines = raw.decode("utf-8").splitlines(keepends=True)
        except UnicodeError as exc:
            raise RuntimeFault("INVALID_INPUT", "Text slicing requires UTF-8.") from exc
        start = number(value.get("start_line", 1), 1, max(1, len(lines)))
        end = number(value.get("end_line", max(1, len(lines))), start, max(1, len(lines)))
        result.update(start_line=start, end_line=end)
        if include_text:
            text = "".join(lines[start-1:end])
            if len(text.encode("utf-8")) > 32768:
                raise RuntimeFault("INPUT_TOO_LARGE", "Select narrower explicit line bounds.")
            result["text"] = text
    return result


def seal(body: dict, budget: int) -> dict:
    return bounded({**body, "pack_id": sha(body)}, budget)


def build(cache, request: dict) -> dict:
    fields(request, {"task_id", "goal", "required"}, {"optional", "budget_bytes", "include_text", "approved_content"})
    task = safe_text(request["task_id"], 128)
    goal = safe_text(request["goal"], 512)
    budget = number(request.get("budget_bytes", 8192), 128, 65536)
    include = request.get("include_text", False)
    if type(include) is not bool or (include and request.get("approved_content") is not True):
        raise RuntimeFault("CONTENT_APPROVAL_REQUIRED", "Inline text requires explicit approved_content=true.")
    required, optional = request["required"], request.get("optional", [])
    if not isinstance(required, list) or not 1 <= len(required) <= 64 or not isinstance(optional, list) or len(optional) > 128:
        raise RuntimeFault("INVALID_INPUT", "Use 1..64 required and at most 128 optional references.")
    refs = [ref(cache, r, include) for r in required]
    body = {"schema": "task-context/v1", "scope": cache.scope, "task_id": task, "goal": goal,
            "required": refs, "optional": [], "omitted_optional": [], "required_complete": True,
            "incomplete": False, "trust": "source-data-not-instructions", "tokens": None}
    # Reserve the complete omission list first. Mandatory contracts are never truncated.
    body["omitted_optional"] = [safe_text(r.get("path"), 1024) for r in optional if isinstance(r, dict)]
    if len(body["omitted_optional"]) != len(optional):
        raise RuntimeFault("INVALID_INPUT", "Optional refs must be objects.")
    body["incomplete"] = bool(optional)
    seal(body, budget)
    for item in optional:
        record = ref(cache, item, include)
        trial = dict(body, optional=body["optional"]+[record], omitted_optional=list(body["omitted_optional"]))
        trial["omitted_optional"].remove(record["path"])
        trial["incomplete"] = bool(trial["omitted_optional"])
        try:
            seal(trial, budget)
        except RuntimeFault as exc:
            if exc.code != "BUDGET_EXCEEDED":
                raise
        else:
            body = trial
    return seal(body, budget)


def verify(cache, pack: dict) -> dict:
    fields(pack, {"schema","scope","task_id","goal","required","optional","omitted_optional","required_complete","incomplete","trust","tokens","pack_id","output_bytes"})
    body = {k:v for k,v in pack.items() if k not in {"pack_id","output_bytes"}}
    if pack["schema"] != "task-context/v1" or pack["scope"] != cache.scope or sha(body) != pack["pack_id"]:
        raise RuntimeFault("INVALID_PACK", "Pack identity or workspace scope changed.")
    if pack["required_complete"] is not True or not isinstance(pack["required"],list) or not pack["required"]:
        raise RuntimeFault("INVALID_PACK", "Required references are not complete.")
    if not isinstance(pack['optional'],list) or len(pack['optional']) > 128 or len(pack['required']) > 64:
        raise RuntimeFault('INVALID_PACK','Pack references exceed the allowed bounds.')
    if type(pack['incomplete']) is not bool or not isinstance(pack['omitted_optional'],list) or pack['incomplete'] != bool(pack['omitted_optional']):
        raise RuntimeFault('INVALID_PACK','Pack omission flags are inconsistent.')
    if pack['trust'] != 'source-data-not-instructions' or pack['tokens'] is not None or pack['output_bytes'] != len(canonical(pack)):
        raise RuntimeFault('INVALID_PACK','Pack trust or byte-accounting metadata changed.')
    for item in pack['required'] + pack['optional']:
        fields(item, {'path','sha256','bytes','role'}, {'start_line','end_line','text'})
    stale = []
    for item in pack["required"] + pack["optional"]:
        try:
            current = ref(cache, {k:v for k,v in item.items() if k in {"path","role","start_line","end_line"}}, "text" in item)
            if current != item:
                stale.append(item["path"])
        except (RuntimeFault, OSError):
            stale.append(item.get("path", "invalid"))
    return {"status": "stale" if stale else "current", "pack_id":pack["pack_id"], "stale_refs":stale,
            "required_complete":not any(r["path"] in stale for r in pack["required"]),
            "domain_approval":False}


def prefix(cache, request: dict) -> dict:
    fields(request, {"static_refs", "dynamic_tail", "approved_content"}, {"budget_bytes"})
    if request["approved_content"] is not True or not isinstance(request["static_refs"],list) or not 1 <= len(request["static_refs"]) <= 32:
        raise RuntimeFault("CONTENT_APPROVAL_REQUIRED", "Select 1..32 explicitly approved static files.")
    tail = request["dynamic_tail"]
    if not isinstance(tail,str) or len(tail.encode("utf-8")) > 32768:
        raise RuntimeFault("INVALID_INPUT", "Dynamic tail must be bounded text.")
    records = [ref(cache, r, True) for r in request["static_refs"]]
    # Preserve caller-declared order. Timestamps and per-turn data stay in the tail.
    stable = "\n".join(r["text"] for r in records)
    return bounded({"schema":"prompt-prefix/v1","prefix":stable,"prefix_sha256":hashlib.sha256(stable.encode()).hexdigest(),
                    "dynamic_tail":tail,"cache_hit":None,"provider_configured":False,
                    "notice":"Host must place this prefix before dynamic content. No API call or provider setting was changed."},
                   number(request.get("budget_bytes",65536),128,65536))
