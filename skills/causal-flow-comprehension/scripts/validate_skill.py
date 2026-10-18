#!/usr/bin/env python3
"""Static validator for one Causal Flow Comprehension portable skill package.

Inspects structural metadata, Top-100 contract, Markdown reachability, SemVer,
corpus-bounded S/F/R/C/E links and authored scenarios. No agent host is run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
DESC_LIMIT = 500
FINDING_DISPOSITIONS = {"implement", "already-covered", "rejected", "not-applicable", "uncertain", "conflict"}


def validate(root: Path) -> list[str]:
    errs: list[str] = []
    root = root.resolve()

    def read(rel: str) -> str:
        try:
            return (root / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errs.append(f"{rel}: not readable ({exc})")
            return ""

    raw = read("SKILL.md")
    lines = raw.splitlines()
    if not lines or lines[0].strip() != "---":
        errs.append("SKILL.md: YAML frontmatter missing at first line")
        return errs
    try:
        end = lines.index("---", 1)
    except ValueError:
        errs.append("SKILL.md: frontmatter not closed")
        return errs
    head: dict[str, str] = {}
    for line in lines[1:end]:
        key, sep, val = line.partition(":")
        if not sep or not key.strip() or key.strip() in head:
            errs.append(f"SKILL.md: invalid/duplicate metadata line {line!r}")
            continue
        val = val.strip()
        if val.startswith('"'):
            try:
                val = json.loads(val)
            except json.JSONDecodeError:
                errs.append(f"SKILL.md: invalid quoted metadata {key}")
        head[key.strip()] = val
    if set(head) != {"name", "description"}:
        errs.append(f"SKILL.md: nonportable frontmatter fields {sorted(set(head) - {'name','description'})} or required fields missing")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", head.get("name", "")):
        errs.append("SKILL.md: name must be lowercase kebab-case")
    if head.get("name") != root.name:
        errs.append("SKILL.md: name must equal root folder name")
    if len(head.get("description", "")) > DESC_LIMIT or not head.get("description"):
        errs.append(f"SKILL.md: description empty or exceeds {DESC_LIMIT} chars ({len(head.get('description',''))})")
    top = "\n".join(lines[:100])
    for token in ["## Purpose and authority", "## Activate / route", "## Modes", "## Workflow", "## Non-negotiable reasoning and evidence rules", "## Output and validation", "## Direct reference routing", "## Release identity / stop condition"]:
        if token not in top:
            errs.append(f"SKILL.md first-100: missing {token}")
    for concept in ["read-only", "counterexample", "unknown", "source", "closed-world", "not-run"]:
        if concept.lower() not in top.lower():
            errs.append(f"SKILL.md first-100: missing critical operational concept {concept}")

    version = read("VERSION").strip()
    if not SEMVER.fullmatch(version):
        errs.append("VERSION: expected single SemVer line")
    if not re.search(r"^## \[" + re.escape(version) + r"\](?:\s+-\s+\d{4}-\d{2}-\d{2})?\s*$", read("CHANGELOG.md"), re.M):
        errs.append("CHANGELOG.md: current VERSION entry missing or mismatched")

    refs = sorted((root / "references").glob("*.md"))
    linkset: set[str] = set()
    for mdlink in re.findall(r"\[[^\]]+\]\(([^)]+)\)", raw):
        if "references/" not in mdlink:
            continue
        if mdlink.startswith("http") or ".." in Path(mdlink).parts:
            errs.append(f"SKILL.md: unsafe/indirect reference {mdlink}")
            continue
        path = (root / mdlink).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            errs.append(f"SKILL.md: missing reference {mdlink}")
        linkset.add(mdlink)
    for r in refs:
        rel = r.relative_to(root).as_posix()
        if rel not in linkset:
            errs.append(f"Mandatory reference not directly linked from root: {rel}")
        text = r.read_text(encoding="utf-8")
        rlines = text.splitlines()
        if len(rlines) > 100:
            first40 = "\n".join(rlines[:40])
            if not all(s in first40 for s in ["Purpose:", "Load when:", "Decision impact:", "Contents"]):
                errs.append(f"{rel}: >100 lines and missing semantic preview/contents")
    if not refs:
        errs.append("references: none found")

    tracepath = root / "research/traceability.json"
    try:
        trace = json.loads(tracepath.read_text(encoding="utf-8"))
        errs.extend(validate_trace(root, trace))
    except (OSError, ValueError) as exc:
        errs.append(f"research/traceability.json: invalid/unavailable ({exc})")
    for name in ("activation", "behavioral"):
        path = root / f"evals/{name}-scenarios.json"
        try:
            suite = json.loads(path.read_text(encoding="utf-8"))
            if suite.get("execution_state") != "authored-not-executed":
                errs.append(f"{path.name}: misleading execution status")
            ids = [s["id"] for s in suite["scenarios"]]
            if len(ids) < 5 or len(ids) != len(set(ids)):
                errs.append(f"{path.name}: too few scenarios or duplicate IDs")
            if name == "activation":
                routes = {s["expected_route"] for s in suite["scenarios"]}
                if not {"activate", "handoff"}.issubset(routes):
                    errs.append("activation-scenarios: positive and negative routes required")
        except (OSError, KeyError, ValueError, TypeError) as exc:
            errs.append(f"{path.name}: invalid suite ({exc})")
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.is_symlink():
            errs.append(f"Symlink not allowed in canonical package: {path}")
        if any(part in {".git", "__pycache__", ".pytest_cache", ".venv"} for part in path.parts):
            errs.append(f"Generated/protected file in package: {path}")
    return errs


def validate_trace(root: Path, trace: dict) -> list[str]:
    errors = []
    if trace.get("schema_version") != "1.0" or trace.get("scope", {}).get("completeness_boundary") != "corpus-bounded":
        errors.append("trace: invalid schema/completeness boundary")
    groups = {}
    for k, prefix in [("sources", "S"), ("findings", "F"), ("requirements", "R"), ("changes", "C"), ("evaluations", "E"), ("conflicts", "K")]:
        objs = trace.get(k, [])
        if not isinstance(objs, list):
            errors.append(f"trace: {k} is not a list")
            objs = []
        ids = [item.get("id", "") for item in objs if isinstance(item, dict)]
        if len(ids) != len(set(ids)) or any(not re.fullmatch(prefix + r"-\d{3}", id) for id in ids):
            errors.append(f"trace: invalid/duplicate {k} IDs")
        groups[k] = {obj["id"]: obj for obj in objs if isinstance(obj, dict) and "id" in obj}
    S,F,R,C,E,K = (groups[k] for k in ("sources", "findings", "requirements", "changes", "evaluations", "conflicts"))
    for sid, s in S.items():
        for fid in s.get("finding_ids", []):
            if fid not in F or sid not in F[fid].get("source_ids", []):
                errors.append(f"{sid}: missing reverse finding link {fid}")
    for fid, f in F.items():
        if f.get("disposition") not in FINDING_DISPOSITIONS or not f.get("rationale"):
            errors.append(f"{fid}: missing disposition/rationale")
        if not f.get("source_ids"):
            errors.append(f"{fid}: missing source")
        for sid in f.get("source_ids", []):
            if sid not in S or fid not in S[sid].get("finding_ids", []):
                errors.append(f"{fid}: missing reverse source link {sid}")
        if f.get("disposition") in {"implement", "already-covered"} and not f.get("requirement_ids"):
            errors.append(f"{fid}: accepted finding without requirement")
        if f.get("disposition") not in {"implement", "already-covered"} and f.get("requirement_ids"):
            errors.append(f"{fid}: excluded finding unexpectedly drives requirement")
        for rid in f.get("requirement_ids", []):
            if rid not in R or fid not in R[rid].get("finding_ids", []):
                errors.append(f"{fid}: missing reverse requirement link {rid}")
    for rid, r in R.items():
        if not r.get("finding_ids") or not r.get("change_ids") or not r.get("evaluation_ids"):
            errors.append(f"{rid}: incomplete finding/change/evaluation chain")
        for fid in r.get("finding_ids", []):
            if fid not in F or rid not in F[fid].get("requirement_ids", []):
                errors.append(f"{rid}: missing reverse finding link {fid}")
        for cid in r.get("change_ids", []):
            if cid not in C or rid not in C[cid].get("satisfies", []):
                errors.append(f"{rid}: missing reverse change link {cid}")
        for eid in r.get("evaluation_ids", []):
            if eid not in E or rid not in E[eid].get("verifies", []):
                errors.append(f"{rid}: missing reverse evaluation link {eid}")
    for cid, c in C.items():
        if not c.get("satisfies"):
            errors.append(f"{cid}: change without requirements")
        path = root / c.get("path", "")
        if not path.is_file() or not path.resolve().is_relative_to(root):
            errors.append(f"{cid}: changed path missing/outside root")
        for rid in c.get("satisfies", []):
            if rid not in R or cid not in R[rid].get("change_ids", []):
                errors.append(f"{cid}: missing reverse requirement link {rid}")
    for eid, e in E.items():
        if e.get("status") not in {"pass", "fail", "not-run"} or not e.get("verifies"):
            errors.append(f"{eid}: invalid status / no checked requirement")
        if e.get("status") == "fail":
            errors.append(f"{eid}: failed evaluation")
        for rid in e.get("verifies", []):
            if rid not in R or eid not in R[rid].get("evaluation_ids", []):
                errors.append(f"{eid}: missing reverse requirement link {rid}")
    if any(k.get("status") == "unresolved" for k in K.values()):
        errors.append("trace: unresolved material conflict")
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    errors = validate(args.root)
    response = {"status": "fail" if errors else "pass", "root": str(args.root.resolve()),
                "diagnostics": errors,
                "limit": "Static structure and trace integrity only; agent execution and research semantics not proven."}
    if args.json:
        print(json.dumps(response, indent=2, ensure_ascii=False))
    else:
        print(response["status"].upper(), args.root)
        for error in errors:
            print(" -", error)
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
