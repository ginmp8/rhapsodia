#!/usr/bin/env python3
"""Audit/compare token-efficient skill refactors with reproducible preservation gates."""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, json, os, re, sys
from pathlib import Path
from typing import Any, Callable

TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".toml", ".template", ".skill"}
TEXT_NAMES = {"SKILL.md", "skill.md", "openai.yaml", "AGENTS.md", "CLAUDE.md"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}
SKIP_SUFFIXES = {".zip", ".pyc", ".pyo"}
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".docx", ".pptx", ".xlsx"}
WORD_RE = re.compile(r"\w+", re.U)
TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[^\sA-Za-z0-9_]", re.U)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CODE_REF_RE = re.compile(r"`([^`\n]+)`")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
URL_RE = re.compile(r"https?://[^\s)>\]]+")
ENV_RE = re.compile(r"\$[A-Z_][A-Z0-9_]*\b")
FLAG_RE = re.compile(r"(?<!\w)--[A-Za-z0-9][A-Za-z0-9_-]*")
VERSION_RE = re.compile(r"\bv?\d+\.\d+(?:\.\d+)*(?:[-+][A-Za-z0-9.-]+)?\b")
NUMBER_RE = re.compile(r"(?<![A-Za-z_])\d+(?:\.\d+)?(?:%|[A-Za-z]+)?")
PATHISH_RE = re.compile(r"(?<!\w)(?:\.?\.?/)?(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+")
PROTECTED_RE = re.compile(r"```[\s\S]*?```|`[^`\n]+`|https?://[^\s)>\]]+|(?<!\w)--[A-Za-z0-9][A-Za-z0-9_-]*|\$[A-Z_][A-Z0-9_]*|\b[\w.-]+/[\w./-]+")
TRACE_PATTERNS = [r"\bcitations?\b", r"\breferences?\b", r"\bsources?\b", r"\bline ranges?\b", r"\bfile paths?\b", r"\breport paths?\b", r"\bevidence\s*/\s*citation\b", r"\bevidence\s+(?:and|or)\s+citations?\b"]
TRACE_RE = [re.compile(p, re.I) for p in TRACE_PATTERNS]
LOCAL_EXTS = (".md", ".json", ".yaml", ".yml", ".py", ".sh", ".template", ".toml")

class Tokenizer:
    def __init__(self, method: str):
        self.method = method
        if method == "estimator-v1":
            self.kind = "estimated"
            self.implementation = "builtin-regex-v1"
            self.count: Callable[[str], int] = self._estimate
        elif method.startswith("tiktoken:"):
            encoding = method.split(":", 1)[1]
            if not encoding:
                raise ValueError("tiktoken method requires an encoding")
            try:
                import tiktoken  # type: ignore
            except Exception as exc:
                raise ValueError(f"tiktoken unavailable: {exc}") from exc
            try:
                enc = tiktoken.get_encoding(encoding)
            except Exception as exc:
                raise ValueError(f"unknown tiktoken encoding {encoding!r}: {exc}") from exc
            try:
                version = importlib.metadata.version("tiktoken")
            except Exception:
                version = "unknown"
            self.kind = "model-tokenizer"
            self.implementation = f"tiktoken {version} / {encoding}"
            self.count = lambda text: len(enc.encode(text))
        else:
            raise ValueError(f"unsupported tokenizer method: {method}")
    @staticmethod
    def _estimate(text: str) -> int:
        tokens = TOKEN_RE.findall(text)
        words = sum(bool(re.fullmatch(r"[A-Za-z0-9_]+", t)) for t in tokens)
        non_ascii = sum(ord(c) > 127 for c in text)
        return max(1, round(words * 0.95 + (len(tokens) - words) * 0.75 + non_ascii * 0.3)) if text else 0
    def info(self) -> dict[str, Any]:
        return {"method": self.method, "kind": self.kind, "implementation": self.implementation}

def is_text_file(path: Path) -> bool:
    return path.name in TEXT_NAMES or (path.suffix.lower() not in BINARY_SUFFIXES and (path.suffix.lower() in TEXT_SUFFIXES or ".template" in path.name))

def iter_all_files(root: Path):
    root = root.resolve()
    if root.is_file():
        yield root; return
    for dirpath, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(names):
            p = Path(dirpath) / name
            if p.suffix.lower() not in SKIP_SUFFIXES and not p.is_symlink():
                yield p

def iter_text_files(root: Path):
    for p in iter_all_files(root):
        if is_text_file(p): yield p

def read_text(path: Path) -> str:
    for enc in ("utf-8", "latin-1"):
        try: return path.read_text(encoding=enc)
        except UnicodeDecodeError: continue
        except Exception: return ""
    return ""

def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix() if root.is_dir() else path.name

def tree_identity(root: Path) -> str:
    h = hashlib.sha256()
    for p in iter_all_files(root):
        rp = rel(root, p).encode("utf-8")
        data = p.read_bytes()
        h.update(len(rp).to_bytes(4, "big")); h.update(rp)
        h.update(len(data).to_bytes(8, "big")); h.update(hashlib.sha256(data).digest())
    return h.hexdigest()

def markdown_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {"__preamble__": []}; stack: list[tuple[int, str]] = []; current = "__preamble__"
    for line in text.splitlines(keepends=True):
        m = HEADING_RE.match(line.rstrip("\n"))
        if m:
            level, title = len(m.group(1)), m.group(2).strip()
            stack = [(lvl, name) for lvl, name in stack if lvl < level] + [(level, title)]
            current = " > ".join(name for _, name in stack); sections.setdefault(current, [])
        sections.setdefault(current, []).append(line)
    return {k:"".join(v) for k,v in sections.items() if "".join(v).strip()}

def local_refs_in_text(text: str) -> list[str]:
    refs = []
    for target in LINK_RE.findall(text): refs.append(target.split("#", 1)[0].strip())
    for code in CODE_REF_RE.findall(text):
        c = code.strip()
        if c.endswith(LOCAL_EXTS) and " " not in c: refs.append(c)
    return sorted(set(r for r in refs if r and "://" not in r and not r.startswith(("#", "mailto:"))))

def reference_graph(root: Path) -> dict[str, Any]:
    root = root.resolve(); entry = root / "SKILL.md"
    reachable, unresolved, edges, queue = set(), [], {}, [entry] if entry.exists() else []
    seen = set()
    while queue:
        src = queue.pop(0)
        if src in seen: continue
        seen.add(src)
        src_rel = rel(root, src)
        refs = local_refs_in_text(read_text(src))
        edges[src_rel] = []
        for raw in refs:
            source_relative = (src.parent / raw).resolve()
            root_relative = (root / raw).resolve()
            if source_relative.exists():
                dest = source_relative
            elif root_relative.exists():
                dest = root_relative
            elif raw.startswith(("./", "../")):
                dest = source_relative
            else:
                dest = root_relative
            try: dest_rel = dest.relative_to(root).as_posix()
            except Exception:
                unresolved.append({"source":src_rel,"reference":raw,"reason":"outside-target"}); continue
            edges[src_rel].append(dest_rel)
            if not dest.exists(): unresolved.append({"source":src_rel,"reference":raw,"reason":"missing"}); continue
            reachable.add(dest_rel)
            if is_text_file(dest): queue.append(dest)
    reference_files = sorted(rel(root,p) for p in iter_text_files(root) if rel(root,p).startswith("references/"))
    unreachable_reference_files = sorted(set(reference_files) - reachable)
    return {"entrypoint":"SKILL.md", "reachable":sorted(reachable), "edges":edges, "unresolved":unresolved, "reference_files":reference_files, "unreachable_reference_files":unreachable_reference_files, "status":"pass" if not unresolved else "fail"}

def protected_regions(text: str) -> list[str]: return sorted(set(PROTECTED_RE.findall(text)))
def trace_hits(text: str) -> dict[str,int]:
    out = {}
    for p, rx in zip(TRACE_PATTERNS, TRACE_RE):
        c = len(rx.findall(text))
        if c: out[p] = c
    return out

def auto_surfaces(text: str) -> dict[str, list[str]]:
    code = CODE_REF_RE.findall(text)
    commands = [c for c in code if re.match(r"^(?:python\d*|bash|sh|git|gh|curl|npm|pnpm|yarn|dotnet|uv|pip\d*)\b", c.strip())]
    schemas = [c for c in code if re.search(r"(?:schema|_version|\.schema\.json$)", c, re.I)]
    return {
        "urls": sorted(set(URL_RE.findall(text))),
        "paths": sorted(set(PATHISH_RE.findall(text))),
        "commands": sorted(set(commands)),
        "env_vars": sorted(set(ENV_RE.findall(text))),
        "schemas": sorted(set(schemas)),
        "flags": sorted(set(FLAG_RE.findall(text))),
        "proper_nouns": [],
        "versions": sorted(set(VERSION_RE.findall(text))),
        "numbers": sorted(set(NUMBER_RE.findall(text))),
    }

def missing_links(path: Path, text: str) -> list[str]:
    missing = []
    for target in LINK_RE.findall(text):
        candidate = target.split("#",1)[0].strip()
        if not candidate or "://" in candidate or target.startswith(("#","mailto:")): continue
        if not (path.parent / candidate).exists(): missing.append(target)
    return missing

def file_stat(root: Path, path: Path, tok: Tokenizer) -> dict[str, Any]:
    text = read_text(path); lines = text.splitlines(); paras = re.split(r"\n\s*\n", text); trace = trace_hits(text); count = tok.count(text)
    return {"path":rel(root,path),"chars":len(text),"words":len(WORD_RE.findall(text)),"lines":len(lines),"token_count":count,"estimated_tokens":count,"tables":sum(line.strip().startswith("|") and "|" in line.strip()[1:] for line in lines),"long_paragraphs":sum(len(WORD_RE.findall(p))>=80 for p in paras),"scaffold_markers":len(re.findall(r"\bTODO\b|\[TODO",text,re.I)),"broken_links":missing_links(path,text),"protected_count":len(protected_regions(text)),"traceability_terms":sum(trace.values()),"traceability_detail":trace}

def audit(target: str|Path, tok: Tokenizer) -> dict[str, Any]:
    root = Path(target).resolve(); stats = [file_stat(root,p,tok) for p in iter_text_files(root)]
    total = lambda k: sum(i[k] for i in stats)
    totals = {"files":len(stats),"chars":total("chars"),"words":total("words"),"lines":total("lines"),"token_count":total("token_count"),"estimated_tokens":total("estimated_tokens"),"tables":total("tables"),"long_paragraphs":total("long_paragraphs"),"scaffold_markers":total("scaffold_markers"),"broken_links":sum(len(i["broken_links"]) for i in stats),"traceability_terms":total("traceability_terms")}
    warnings=[]
    if totals["scaffold_markers"]: warnings.append(f"scaffold markers found: {totals['scaffold_markers']}")
    if totals["broken_links"]: warnings.append(f"broken markdown links found: {totals['broken_links']}")
    if totals["long_paragraphs"]: warnings.append(f"long paragraphs found: {totals['long_paragraphs']}")
    graph = reference_graph(root)
    if graph["unresolved"]: warnings.append(f"unresolved local references: {len(graph['unresolved'])}")
    by_path = {item["path"]: item for item in stats}
    entrypoint_count = by_path.get("SKILL.md", {}).get("token_count", 0)
    instruction_paths = {"SKILL.md"}
    for rp in graph["reachable"]:
        if rp.startswith("references/") or rp.startswith("examples/") or rp.startswith("assets/templates/"):
            if rp in by_path:
                instruction_paths.add(rp)
    instruction_count = sum(by_path[p]["token_count"] for p in instruction_paths if p in by_path)
    token_scopes = {
        "entrypoint": entrypoint_count,
        "instructions": instruction_count,
        "all-text": totals["token_count"],
        "instruction_paths": sorted(p for p in instruction_paths if p in by_path),
    }
    corpus = "\n".join(read_text(p) for p in iter_text_files(root))
    return {"target":str(root),"target_identity_sha256":tree_identity(root),"tokenization":tok.info(),"token_scopes":token_scopes,"files":stats,"totals":totals,"top_files":[{k:i[k] for k in ("path","token_count","estimated_tokens","chars","lines")} for i in sorted(stats,key=lambda i:i["token_count"],reverse=True)[:10]],"local_reference_graph":graph,"auto_protected_surfaces":auto_surfaces(corpus),"warnings":warnings}

def text_map(target: str|Path) -> dict[str,str]:
    root=Path(target).resolve(); return {rel(root,p):read_text(p) for p in iter_text_files(root)}

def file_token_deltas(before: dict[str,str], after: dict[str,str], tok: Tokenizer) -> list[dict[str,Any]]:
    rows=[]
    for name in sorted(set(before)&set(after)):
        b,a=tok.count(before[name]),tok.count(after[name]); d=a-b
        rows.append({"path":name,"before_token_count":b,"after_token_count":a,"before_estimated_tokens":b,"after_estimated_tokens":a,"token_delta":d,"reduction_pct":round(((b-a)/b*100) if b else 0,2),"status":"increased" if d>0 else "decreased" if d<0 else "unchanged"})
    return rows

def section_token_deltas(before: dict[str,str], after: dict[str,str], tok: Tokenizer) -> list[dict[str,Any]]:
    rows=[]
    for name in sorted(set(before)&set(after)):
        if not (name.lower().endswith(".md") or name.lower().endswith(".md.template")): continue
        bs,as_=markdown_sections(before[name]),markdown_sections(after[name])
        for sec in sorted(set(bs)&set(as_)):
            b,a=tok.count(bs[sec]),tok.count(as_[sec]); d=a-b
            if d: rows.append({"path":name,"section":sec,"before_token_count":b,"after_token_count":a,"token_delta":d,"status":"increased" if d>0 else "decreased"})
    return rows

def trace_diff(before: dict[str,str], after: dict[str,str]) -> list[dict[str,Any]]:
    losses=[]
    for name in sorted(set(before)&set(after)):
        bh,ah=trace_hits(before[name]),trace_hits(after[name]); lost={k:c-ah.get(k,0) for k,c in bh.items() if ah.get(k,0)<c}
        if lost: losses.append({"path":name,"lost_traceability_terms":lost})
    return losses

def load_contract(path: str|None) -> dict[str,Any]|None:
    if not path: return None
    return json.loads(Path(path).read_text(encoding="utf-8"))

def preservation_check(contract: dict[str,Any]|None, after_root: Path) -> dict[str,Any]:
    if not contract: return {"status":"not-run","reason":"no contract supplied","protected":{},"invariants":[],"manual_or_scenario_required":[]}
    corpus="\n".join(read_text(p) for p in iter_text_files(after_root)); corpus_cf=corpus.casefold(); graph=reference_graph(after_root)
    protected_results={}; failures=[]
    for category, values in contract.get("protected",{}).items():
        rows=[]
        for item in values:
            if isinstance(item, str):
                value, equivalents, authorized, reason = item, [], False, None
            else:
                value = item.get("value", "")
                equivalents = item.get("equivalents", [])
                authorized = item.get("authorized") is True
                reason = item.get("reason")
            if value in corpus:
                status, matched = "pass", value
            else:
                matched = next((x for x in equivalents if x in corpus), None)
                status = "pass-authorized-equivalent" if matched and authorized else "fail"
            rows.append({"value":value,"status":status,"matched":matched,"reason":reason})
            if status == "fail": failures.append({"kind":"protected","category":category,"value":value})
        protected_results[category]=rows
    invariant_results=[]; manual=[]
    for inv in contract.get("semantic_invariants",[]):
        ver=inv.get("verification"); pattern=inv.get("pattern",""); status="manual-required"; evidence={}
        if ver=="contains": status="pass" if pattern.casefold() in corpus_cf else "fail"; evidence={"pattern":pattern}
        elif ver=="regex":
            try: ok=bool(re.search(pattern,corpus,re.I|re.M)); status="pass" if ok else "fail"; evidence={"pattern":pattern}
            except re.error as exc: status="fail"; evidence={"pattern":pattern,"error":str(exc)}
        elif ver=="local_reference": status="pass" if pattern in graph["reachable"] else "fail"; evidence={"path":pattern}
        elif ver in {"manual","scenario"}: manual.append({"id":inv.get("id"),"verification":ver,"evidence_refs":inv.get("evidence_refs",[]),"scenario_ids":inv.get("scenario_ids",[])})
        else: status="fail"; evidence={"error":f"unsupported verification {ver!r}"}
        row={"id":inv.get("id"),"category":inv.get("category"),"verification":ver,"status":status,"evidence":evidence}; invariant_results.append(row)
        if status=="fail": failures.append({"kind":"invariant","id":inv.get("id"),"category":inv.get("category")})
    return {"status":"fail" if failures else "pass","protected":protected_results,"invariants":invariant_results,"manual_or_scenario_required":manual,"failures":failures}

def compare(before_target: str|Path, after_target: str|Path, tok: Tokenizer, contract: dict[str,Any]|None, token_scope: str) -> dict[str,Any]:
    before_a,after_a=audit(before_target,tok),audit(after_target,tok); before,after=text_map(before_target),text_map(after_target)
    protected_diffs=[]
    for name in sorted(set(before)&set(after)):
        b,a=set(protected_regions(before[name])),set(protected_regions(after[name])); missing,added=sorted(b-a)[:40],sorted(a-b)[:40]
        if missing or added: protected_diffs.append({"path":name,"missing_after":missing,"added_after":added})
    file_deltas=file_token_deltas(before,after,tok); section_deltas=section_token_deltas(before,after,tok); increased_files=[x for x in file_deltas if x["token_delta"]>0]; increased_sections=[x for x in section_deltas if x["token_delta"]>0]
    bt,at=before_a["token_scopes"][token_scope],after_a["token_scopes"][token_scope]
    bg,ag=before_a["local_reference_graph"],after_a["local_reference_graph"]
    baseline_refs={r for r in bg["reachable"] if r.startswith("references/")}; lost_refs=sorted(baseline_refs-set(ag["reachable"])); progressive_fail=bool(lost_refs or ag["unresolved"])
    preservation=preservation_check(contract,Path(after_target).resolve())
    return {
        "tokenization":{**tok.info(), "scope": token_scope},
        "comparison":{"token_scope":token_scope,"before_token_count":bt,"after_token_count":at,"before_estimated_tokens":bt,"after_estimated_tokens":at,"token_delta":at-bt,"reduction_pct":round(((bt-at)/bt*100) if bt else 0,2),"token_reduced":at<bt,"improved":at<bt},
        "local_token_comparison":{"common_files_checked":len(set(before)&set(after)),"increased_files":len(increased_files),"increased_sections":len(increased_sections),"file_token_deltas":file_deltas,"section_token_deltas":section_deltas,"local_regressions":{"files":increased_files,"sections":increased_sections}},
        "protected_region_comparison":{"common_files_checked":len(set(before)&set(after)),"files_missing_after":sorted(set(before)-set(after)),"files_added_after":sorted(set(after)-set(before)),"files_with_protected_diffs":len(protected_diffs),"diffs":protected_diffs[:40]},
        "traceability_comparison":{"before_terms":before_a["totals"]["traceability_terms"],"after_terms":after_a["totals"]["traceability_terms"],"term_delta":after_a["totals"]["traceability_terms"]-before_a["totals"]["traceability_terms"],"losses":trace_diff(before,after)},
        "progressive_loading_comparison":{"status":"fail" if progressive_fail else "pass","baseline_reachable_references":sorted(baseline_refs),"lost_references":lost_refs,"candidate_unresolved":ag["unresolved"],"candidate_unreachable_reference_files":ag["unreachable_reference_files"]},
        "preservation":preservation,
        "targets":[before_a,after_a]
    }

def to_markdown(report: dict[str,Any]) -> str:
    lines=["# Token Refactor Audit",""]
    lines += ["## Tokenization",f"- Method: {report.get('tokenization',{}).get('method','n/a')}",f"- Kind: {report.get('tokenization',{}).get('kind','n/a')}",f"- Implementation: {report.get('tokenization',{}).get('implementation','n/a')}",f"- Scope: {report.get('tokenization',{}).get('scope','n/a')}",""]
    c=report.get("comparison")
    if c: lines += ["## Token Delta",f"- Before: {c['before_token_count']}",f"- After: {c['after_token_count']}",f"- Delta: {c['token_delta']}",f"- Reduction: {c['reduction_pct']}%",f"- Token reduced: {c['token_reduced']}",""]
    p=report.get("preservation")
    if p: lines += ["## Semantic Preservation",f"- Mechanical status: {p['status']}",f"- Manual/scenario checks still required: {len(p.get('manual_or_scenario_required',[]))}",""]
    g=report.get("progressive_loading_comparison")
    if g: lines += ["## Progressive Loading",f"- Status: {g['status']}",f"- Lost baseline refs: {len(g['lost_references'])}",f"- Candidate unresolved refs: {len(g['candidate_unresolved'])}",""]
    for t in report.get("targets",[]):
        lines += [f"## {t['target']}",f"- Identity SHA-256: {t['target_identity_sha256']}",f"- Token count: {t['totals']['token_count']}",f"- Files: {t['totals']['files']}",f"- Broken links: {t['totals']['broken_links']}",f"- Traceability terms: {t['totals']['traceability_terms']}",""]
    return "\n".join(lines)

def main() -> int:
    ap=argparse.ArgumentParser(description="Audit or compare token-efficient skill packages with preservation gates.")
    ap.add_argument("--target"); ap.add_argument("--before"); ap.add_argument("--after"); ap.add_argument("--contract"); ap.add_argument("--tokenizer",default="estimator-v1"); ap.add_argument("--token-scope",choices=["entrypoint","instructions","all-text"],default="instructions"); ap.add_argument("--output"); ap.add_argument("--markdown"); ap.add_argument("--fail-on-regression",action="store_true"); ap.add_argument("--fail-on-preservation-loss",action="store_true"); ap.add_argument("--require-token-reduction",action="store_true")
    args=ap.parse_args()
    if args.target and (args.before or args.after): ap.error("use --target or --before/--after, not both")
    if not args.target and not (args.before and args.after): ap.error("provide --target or both --before and --after")
    try: tok=Tokenizer(args.tokenizer)
    except ValueError as exc: print(json.dumps({"status":"fail","stage":"tokenizer","error":str(exc)},indent=2),file=sys.stderr); return 2
    try: contract=load_contract(args.contract)
    except Exception as exc: print(json.dumps({"status":"fail","stage":"contract","error":str(exc)},indent=2),file=sys.stderr); return 2
    report={"tokenization":{**tok.info(), "scope": args.token_scope},"targets":[audit(args.target,tok)]} if args.target else compare(args.before,args.after,tok,contract,args.token_scope)
    payload=json.dumps(report,ensure_ascii=False,indent=2)
    if args.output: Path(args.output).parent.mkdir(parents=True,exist_ok=True); Path(args.output).write_text(payload+"\n",encoding="utf-8")
    else: print(payload)
    if args.markdown: Path(args.markdown).parent.mkdir(parents=True,exist_ok=True); Path(args.markdown).write_text(to_markdown(report),encoding="utf-8")
    if "comparison" in report:
        if args.fail_on_regression and (report["local_token_comparison"]["increased_files"] or report["local_token_comparison"]["increased_sections"]): return 3
        if args.fail_on_preservation_loss and (report["preservation"]["status"]=="fail" or report["progressive_loading_comparison"]["status"]=="fail"): return 4
        if args.require_token_reduction and not report["comparison"]["token_reduced"]: return 5
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
