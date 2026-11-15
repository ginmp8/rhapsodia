"""Deterministic PR audit core. Python 3.10+, standard library only."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

VERSION = "pr-audit/v1"
SOURCE_SCHEMA = "pr-audit/source/v1"
REQUIREMENTS_SCHEMA = "pr-audit/requirements/v1"
CHECKS_SCHEMA = "pr-audit/checks/v1"
EXECUTIONS_SCHEMA = "pr-audit/executions/v1"
EVIDENCE_SCHEMA = "pr-audit/evidence/v1"
REPORT_SCHEMA = "pr-audit/report/v1"


class AuditError(ValueError):
    """Actionable validation or missing-evidence error."""


def canonical(obj: Any) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def read_json(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as handle:
        obj = json.load(handle)
    if not isinstance(obj, dict):
        raise AuditError(f"Expected JSON object: {path}")
    return obj


def write_immutable(path: str | Path, content: bytes) -> None:
    """Writes once; replay is a no-op only when exact bytes match."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != content:
            raise AuditError(f"Refusing to overwrite frozen artifact: {path}. Use a new output directory.")
        return
    tmp = path.with_name(path.name + ".tmp")
    if tmp.exists():
        raise AuditError(f"Stale temporary artifact: {tmp}")
    try:
        with open(tmp, "xb") as handle:
            handle.write(content)
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink()


def require_schema(obj: dict, schema: str) -> None:
    if obj.get("schema") != schema:
        raise AuditError(f"Expected schema {schema}, received {obj.get('schema')}")


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise AuditError("Expected text field")
    return value.replace("\r\n", "\n").replace("\r", "\n")


def normalize_source(src: dict, specs: list[dict] | None = None) -> dict:
    """Select immutable, relevant GitHub fields; reject incomplete PR identity."""
    repo = src.get("repository") or src.get("repo")
    if not isinstance(repo, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise AuditError("repository must be owner/repo")
    pr = src.get("pull_request") or src.get("pr") or {}
    issue = src.get("issue") or {}
    for key, record in (("pull_request", pr), ("issue", issue)):
        if not isinstance(record, dict) or not isinstance(record.get("number"), int) or record["number"] < 1:
            raise AuditError(f"{key}.number must be a positive integer")
    head = pr.get("head_sha") or (pr.get("head") or {}).get("sha")
    base = pr.get("base_sha") or (pr.get("base") or {}).get("sha")
    if not isinstance(head, str) or not re.fullmatch(r"[a-fA-F0-9]{40}", head):
        raise AuditError("pull_request.head_sha must be a full 40-character Git commit SHA")
    if not isinstance(base, str) or not re.fullmatch(r"[a-fA-F0-9]{40}", base):
        raise AuditError("pull_request.base_sha must be a full 40-character Git commit SHA")
    files = pr.get("files", [])
    if not isinstance(files, list):
        raise AuditError("pull_request.files must be an array")
    changed = []
    for item in files:
        if isinstance(item, str):
            changed.append(item)
        elif isinstance(item, dict):
            changed.append(item.get("filename") or item.get("path"))
        else:
            raise AuditError("Invalid changed file item")
    if not all(isinstance(p, str) and p for p in changed):
        raise AuditError("Invalid changed file path")
    comments = issue.get("comments", [])
    if not isinstance(comments, list):
        raise AuditError("issue.comments must be an array")
    norm_comments = []
    for c in comments:
        if not isinstance(c, dict) or not isinstance(c.get("id"), (str, int)):
            raise AuditError("Each issue comment must have a stable id")
        norm_comments.append({"id": str(c["id"]), "body": normalize_text(c.get("body"))})
    ids = [c["id"] for c in norm_comments]
    if len(ids) != len(set(ids)):
        raise AuditError("Duplicate issue comment IDs")
    all_specs = specs if specs is not None else src.get("spec_files", [])
    if not isinstance(all_specs, list):
        raise AuditError("spec_files must be an array")
    norm_specs = []
    for item in all_specs:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item["name"]:
            raise AuditError("Each spec file needs a name")
        norm_specs.append({"name": item["name"], "body": normalize_text(item.get("body"))})
    names = [s["name"] for s in norm_specs]
    if len(set(names)) != len(names):
        raise AuditError("Duplicate spec file names")
    capture = src.get("capture") or {}
    if not isinstance(capture, dict):
        raise AuditError("capture provenance must be an object")
    method = capture.get("method", "unspecified")
    if method not in ("gh_api_live", "offline_input"):
        method = "unspecified"
    completeness = "verified_by_pagination" if method == "gh_api_live" and capture.get("issue_completeness") == "verified_by_pagination" else "not_verified"
    return {
        "schema": SOURCE_SCHEMA,
        "repository": repo,
        "capture": {"method": method, "issue_completeness": completeness},
        "pull_request": {
            "number": pr["number"],
            "title": normalize_text(pr.get("title")),
            "body": normalize_text(pr.get("body")),
            "url": pr.get("url") or pr.get("html_url") or f"https://github.com/{repo}/pull/{pr['number']}",
            "head_sha": head.lower(),
            "base_sha": base.lower(),
            "files": sorted(set(changed)),
        },
        "issue": {
            "number": issue["number"],
            "title": normalize_text(issue.get("title")),
            "body": normalize_text(issue.get("body")),
            "url": issue.get("url") or issue.get("html_url") or f"https://github.com/{repo}/issues/{issue['number']}",
            "comments": sorted(norm_comments, key=lambda c: (len(c["id"]), c["id"])),
        },
        "spec_files": sorted(norm_specs, key=lambda s: s["name"]),
    }


def spec_material(source: dict) -> dict:
    require_schema(source, SOURCE_SCHEMA)
    return {"repository": source["repository"], "issue": source["issue"], "spec_files": source["spec_files"]}


EXPLICIT = re.compile(r"^\s*(?:#{1,6}\s*|[-*+]\s*|\d+[.)]\s*|\|\s*)?(?:\*\*)?\b((?:REQ|AC)[-_ ]?\d+)\b(?:\*\*)?\s*[:.\-–—|)]?\s*(.*)$", re.I)
CHECKBOX = re.compile(r"^\s*[-*+]\s*\[(?: |x|X)\]\s+(.+)$")
HEADING = re.compile(r"^\s*(#{1,6})\s+(.+)$")
AC_SECTION = re.compile(r"\b(acceptance|accepta[çc][ãa]o|criteria|crit[eé]rios|definition of done)\b", re.I)


def clean_criterion_text(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().strip("| ").strip("* ")).strip()


def extract_requirements(source: dict) -> dict:
    """Explicit REQ/AC markers and checkboxes in acceptance sections only.

    Does not pretend prose elsewhere has been completely captured.
    """
    require_schema(source, SOURCE_SCHEMA)
    sections = [("issue-body", source["issue"]["body"])]
    sections += [(f"issue-comment-{c['id']}", c["body"]) for c in source["issue"]["comments"]]
    sections += [(f"spec:{s['name']}", s["body"]) for s in source["spec_files"]]
    extracted: dict[str, dict] = {}
    conflicts = []
    warnings = []
    for origin, body in sections:
        active_section_level = None
        in_fence = False
        records: list[dict] = []
        for lineno, line in enumerate(body.splitlines(), start=1):
            if line.lstrip().startswith(("```", "~~~")):
                in_fence = not in_fence
                continue
            if in_fence or line.lstrip().startswith(">"):
                continue
            heading = HEADING.match(line)
            if heading:
                depth = len(heading.group(1))
                if active_section_level is not None and depth <= active_section_level:
                    active_section_level = None
                if AC_SECTION.search(heading.group(2)):
                    active_section_level = depth
            explicit = EXPLICIT.match(line)
            if explicit:
                raw_id = explicit.group(1).upper().replace("_", "-").replace(" ", "-")
                prefix, number = re.match(r"(REQ|AC)-(\d+)", raw_id).groups()
                crit_id = f"{prefix}-{int(number):02d}"
                description = clean_criterion_text(explicit.group(2))
                if not description:
                    warnings.append(f"{origin}:{lineno}: {crit_id} has no inline description; fill it from authoritative text before scoring")
                records.append({"id": crit_id, "text": description, "source": origin, "line": lineno})
            elif active_section_level is not None:
                check = CHECKBOX.match(line)
                if check:
                    description = clean_criterion_text(check.group(1))
                    if description:
                        # Content ID survives checkbox reordering and checked/unchecked changes.
                        h = hashlib.sha256(description.casefold().encode("utf-8")).hexdigest()[:12]
                        records.append({"id": f"CHK-{h}", "text": description, "source": origin, "line": lineno})
        if body.strip() and not records:
            warnings.append(f"{origin}: no machine-extractable REQ/AC or acceptance checkbox; prose must be reviewed")
        for entry in records:
            ident = entry["id"]
            if ident in extracted:
                old = extracted[ident]
                if old["text"].casefold() != entry["text"].casefold():
                    conflicts.append(f"Conflicting criterion {ident}: {old['source']}:{old['line']} vs {origin}:{entry['line']}")
                else:
                    old["also_at"].append({"source": origin, "line": entry["line"]})
            else:
                extracted[ident] = {**entry, "also_at": []}
    if conflicts:
        raise AuditError("Ambiguous normative requirements:\n  " + "\n  ".join(sorted(conflicts)))
    if not extracted:
        warnings.append("No explicit criteria extracted. A percentage would be meaningless until requirements are structured.")
    if any(not item["text"] for item in extracted.values()):
        raise AuditError("Some REQ/AC items have empty descriptions. Supply a structured specification before scoring.")
    criteria = sorted(extracted.values(), key=lambda x: (x["id"].split("-")[0], x["id"]))
    return {
        "schema": REQUIREMENTS_SCHEMA,
        "spec_digest": digest(spec_material(source)),
        "criteria": criteria,
        "warnings": sorted(set(warnings)),
    }


def init_checks(requirements: dict) -> dict:
    require_schema(requirements, REQUIREMENTS_SCHEMA)
    return {
        "schema": CHECKS_SCHEMA,
        "requirements_digest": digest(requirements),
        "requirements": {
            c["id"]: {"weight": 1, "proof_policy": "runtime", "checks": []}
            for c in requirements["criteria"]
        },
    }


def assert_valid_path(path: Any) -> str:
    if (not isinstance(path, str) or not path or "\\" in path or "\0" in path or
        path.startswith("/") or path.startswith("~") or ":" in path.split("/")[0] or
        any(part in ("", ".", "..") for part in path.split("/")) or path.startswith("-")):
        raise AuditError(f"Unsafe or invalid repository-relative path: {path!r}")
    return path


def validate_checks(requirements: dict, checks: dict) -> None:
    require_schema(requirements, REQUIREMENTS_SCHEMA)
    require_schema(checks, CHECKS_SCHEMA)
    if checks.get("requirements_digest") != digest(requirements):
        raise AuditError("Evidence plan belongs to another frozen requirements version")
    expected = {c["id"] for c in requirements["criteria"]}
    present = set(checks.get("requirements", {}))
    if expected != present:
        raise AuditError(f"Evidence plan criterion ID mismatch: missing={sorted(expected-present)}, extra={sorted(present-expected)}")
    for ident, binding in checks["requirements"].items():
        if not isinstance(binding, dict):
            raise AuditError(f"Invalid binding {ident}")
        if set(binding) - {"weight", "proof_policy", "checks", "not_applicable", "reason"}:
            raise AuditError(f"Unrecognized binding field for {ident}")
        if not isinstance(binding.get("weight"), int) or isinstance(binding["weight"], bool) or not 1 <= binding["weight"] <= 100:
            raise AuditError(f"{ident}: weight must be an integer 1..100")
        if binding.get("proof_policy") not in ("static", "runtime"):
            raise AuditError(f"{ident}: proof_policy must be static or runtime")
        if not isinstance(binding.get("checks"), list):
            raise AuditError(f"{ident}: checks must be a list")
        if binding.get("not_applicable"):
            if not isinstance(binding.get("reason"), str) or len(binding["reason"].strip()) < 10:
                raise AuditError(f"{ident}: NOT_APPLICABLE needs a reason of at least 10 characters")
            if binding["checks"]:
                raise AuditError(f"{ident}: NOT_APPLICABLE must not retain checks")
        elif binding.get("not_applicable") not in (None, False):
            raise AuditError(f"{ident}: invalid not_applicable flag")
        seen = set()
        for item in binding["checks"]:
            if not isinstance(item, dict):
                raise AuditError(f"{ident}: each check must be an object")
            name, kind = item.get("id"), item.get("kind")
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", name) or name in seen:
                raise AuditError(f"{ident}: check IDs must be unique and alphanumeric/dash/underscore")
            seen.add(name)
            if kind in ("path_exists", "contains", "not_contains"):
                if set(item) != ({"id", "kind", "path"} if kind == "path_exists" else {"id", "kind", "path", "text"}):
                    raise AuditError(f"{ident}/{name}: malformed {kind} check")
                assert_valid_path(item["path"])
                if kind != "path_exists" and (not isinstance(item["text"], str) or not item["text"] or len(item["text"]) > 500):
                    raise AuditError(f"{ident}/{name}: nonempty literal text up to 500 characters required")
            elif kind == "test":
                if set(item) - {"id", "kind", "argv", "timeout_seconds"} or "argv" not in item:
                    raise AuditError(f"{ident}/{name}: malformed test check")
                argv = item["argv"]
                if not isinstance(argv, list) or not argv or len(argv) > 32 or not all(isinstance(x, str) and x and "\0" not in x for x in argv):
                    raise AuditError(f"{ident}/{name}: argv must be a nonempty string array")
                timeout = item.get("timeout_seconds", 120)
                if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 1800:
                    raise AuditError(f"{ident}/{name}: timeout_seconds must be 1..1800")
            else:
                raise AuditError(f"{ident}/{name}: unsupported check kind {kind!r}")


def git_bytes(repo_path: str | Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(repo_path), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        raise AuditError(f"git {args[0]} failed: {result.stderr.decode('utf-8', 'replace')[:300].strip()}")
    return result.stdout


def verify_commit_available(repo_path: str | Path, sha: str) -> None:
    kind = git_bytes(repo_path, "cat-file", "-t", sha).strip()
    if kind != b"commit":
        raise AuditError(f"Not a commit: {sha}")


def inspect(source: dict, requirements: dict, checks: dict, repo_path: str | Path | None = None, executions: dict | None = None) -> dict:
    require_schema(source, SOURCE_SCHEMA)
    validate_checks(requirements, checks)
    head = source["pull_request"]["head_sha"]
    if requirements["spec_digest"] != digest(spec_material(source)):
        raise AuditError("Issue/spec content differs from frozen requirements")
    if repo_path is not None:
        verify_commit_available(repo_path, head)
    if executions is not None:
        require_schema(executions, EXECUTIONS_SCHEMA)
        needed = {"source_digest": digest(source), "requirements_digest": digest(requirements), "checks_digest": digest(checks), "head_sha": head}
        if any(executions.get(key) != value for key, value in needed.items()):
            raise AuditError("Execution receipts do not belong to the exact source, plan, and HEAD SHA")
    results = {}
    blob_cache: dict[str, bytes | None] = {}
    for criterion in requirements["criteria"]:
        ident = criterion["id"]
        results[ident] = {}
        for check in checks["requirements"][ident]["checks"]:
            name, kind = check["id"], check["kind"]
            if kind == "test":
                receipt = (executions or {}).get("results", {}).get(f"{ident}/{name}")
                if receipt is None:
                    results[ident][name] = {"status": "NOT_RUN", "kind": kind, "reason": "No frozen execution receipt"}
                    continue
                if not isinstance(receipt, dict) or receipt.get("argv") != check["argv"] or receipt.get("status") not in ("PASS", "FAIL", "TIMEOUT", "ERROR"):
                    raise AuditError(f"Malformed or mismatched execution receipt for {ident}/{name}")
                exit_code = receipt.get("exit_code")
                if (receipt["status"] == "PASS" and exit_code != 0 or
                    receipt["status"] == "FAIL" and (not isinstance(exit_code, int) or exit_code == 0) or
                    receipt["status"] in ("TIMEOUT", "ERROR") and exit_code is not None):
                    raise AuditError(f"Inconsistent command outcome receipt for {ident}/{name}")
                status = receipt["status"] if receipt["status"] in ("PASS", "FAIL") else "NOT_RUN"
                results[ident][name] = {"status": status, "kind": kind, "reason": receipt["status"]}
                continue
            if repo_path is None:
                results[ident][name] = {"status": "NOT_RUN", "kind": kind, "reason": "Local Git repository not supplied"}
                continue
            path = check["path"]
            if path not in blob_cache:
                result = subprocess.run(["git", "-C", str(repo_path), "show", f"{head}:{path}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode == 0:
                    blob_cache[path] = result.stdout
                elif b"does not exist" in result.stderr or b"exists on disk" in result.stderr or b"path '" in result.stderr:
                    blob_cache[path] = None
                else:
                    raise AuditError(f"Cannot read Git object {head}:{path}: {result.stderr.decode('utf-8','replace')[:200]}")
            blob = blob_cache[path]
            if kind == "path_exists":
                ok = blob is not None
            elif kind == "contains":
                ok = blob is not None and check["text"].encode("utf-8") in blob
            else:  # not_contains: absent file is not affirmative proof
                ok = blob is not None and check["text"].encode("utf-8") not in blob
            results[ident][name] = {"status": "PASS" if ok else "FAIL", "kind": kind, "reason": "Git object at pinned HEAD"}
    return {
        "schema": EVIDENCE_SCHEMA,
        "source_digest": digest(source),
        "requirements_digest": digest(requirements),
        "checks_digest": digest(checks),
        "executions_digest": digest(executions) if executions else None,
        "head_sha": head,
        "results": results,
    }


def two_dec(n: Decimal) -> str:
    return str(n.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def score_group(criteria: list[dict]) -> dict:
    """Evidence lower bounds, never inferred feature-implementation progress.

    A zero is meaningful only after at least one declared check was evaluated.
    In particular, no checkout and no test receipts must yield N/A, not 0%.
    """
    counts = {k: 0 for k in ("PASS", "PARTIAL", "FAIL", "UNVERIFIED", "NOT_APPLICABLE")}
    weights = {k: 0 for k in counts}
    total_checks = observed_checks = mapped = assessed = 0
    for c in criteria:
        counts[c["status"]] += 1
        weights[c["status"]] += c["weight"]
        if c["status"] == "NOT_APPLICABLE":
            continue
        probes = c["checks"]
        total_checks += len(probes)
        observed = sum(p["status"] in ("PASS", "FAIL") for p in probes)
        observed_checks += observed
        mapped += bool(probes)
        assessed += bool(observed)
    eligible_weight = sum(weights.values()) - weights["NOT_APPLICABLE"]
    eligible_count = len(criteria) - counts["NOT_APPLICABLE"]
    pct = lambda a, b: two_dec(Decimal(a) * 100 / Decimal(b)) if b else None
    plan_complete = mapped == eligible_count
    any_terminal_result = bool(counts["PASS"] or counts["FAIL"])
    numeric_ready = bool(observed_checks and plan_complete and any_terminal_result)
    assessment = (
        "NOT_ASSESSED" if not observed_checks else
        "INCOMPLETE_PLAN" if not plan_complete else
        "PARTIALLY_ASSESSED" if counts["UNVERIFIED"] or counts["PARTIAL"] else
        "EVALUATED_KNOWN_SCOPE"
    )
    return {
        "counts": counts,
        "eligible_count": eligible_count,
        "eligible_weight": eligible_weight,
        "assessment_state": assessment,
        "observed_checks": observed_checks,
        "declared_checks": total_checks,
        "checks_not_run": total_checks - observed_checks,
        "requirements_with_observations": assessed,
        "completion_verified_pct": pct(weights["PASS"], eligible_weight) if numeric_ready else None,
        "completion_possible_upper_pct": pct(weights["PASS"] + weights["PARTIAL"] + weights["UNVERIFIED"], eligible_weight) if numeric_ready else None,
        "probes_pass_pct": pct(sum(p["status"] == "PASS" for c in criteria if c["status"] != "NOT_APPLICABLE" for p in c["checks"]), total_checks) if observed_checks else None,
        "requirements_mapped_pct": pct(mapped, eligible_count),
    }


def score(source: dict, requirements: dict, checks: dict, evidence: dict) -> dict:
    require_schema(source, SOURCE_SCHEMA)
    validate_checks(requirements, checks)
    require_schema(evidence, EVIDENCE_SCHEMA)
    refs = {"source_digest": digest(source), "requirements_digest": digest(requirements), "checks_digest": digest(checks), "head_sha": source["pull_request"]["head_sha"]}
    if any(evidence.get(k) != v for k, v in refs.items()):
        raise AuditError("Evidence does not match the exact frozen source, criteria, plan, and commit")
    if set(evidence.get("results", {})) != set(checks["requirements"]):
        raise AuditError("Evidence has missing or extra requirement results")
    criteria = []
    for crit in requirements["criteria"]:
        ident = crit["id"]
        binding = checks["requirements"][ident]
        declared = binding["checks"]
        observed = evidence["results"][ident]
        if set(observed) != {c["id"] for c in declared}:
            raise AuditError(f"Evidence check IDs do not match plan for {ident}")
        statuses = []
        proof_types = []
        for ch in declared:
            item = observed[ch["id"]]
            if not isinstance(item, dict) or item.get("status") not in ("PASS", "FAIL", "NOT_RUN") or item.get("kind") != ch["kind"]:
                raise AuditError(f"Invalid evidence for {ident}/{ch['id']}")
            statuses.append(item["status"])
            if item["status"] == "PASS":
                proof_types.append(ch["kind"])
        if binding.get("not_applicable"):
            status = "NOT_APPLICABLE"
        elif not declared or all(s == "NOT_RUN" for s in statuses):
            status = "UNVERIFIED"
        elif "FAIL" in statuses:
            status = "PARTIAL" if "PASS" in statuses else "FAIL"
        elif "NOT_RUN" in statuses:
            status = "PARTIAL" if "PASS" in statuses else "UNVERIFIED"
        elif binding["proof_policy"] == "runtime" and "test" not in proof_types:
            status = "PARTIAL"
        else:
            status = "PASS"
        criteria.append({
            "id": ident, "text": crit["text"], "source": crit["source"], "line": crit["line"],
            "weight": binding["weight"], "proof_policy": binding["proof_policy"],
            "status": status, "checks": [{"id": c["id"], **observed[c["id"]]} for c in declared],
            **({"reason": binding["reason"]} if binding.get("not_applicable") else {}),
        })
    overall = score_group(criteria)
    # Parent REQs and executable ACs are two views of one specification. They
    # must not be silently presented as a single 54-step implementation rate.
    overall["acceptance_criteria"] = score_group([c for c in criteria if c["id"].startswith("AC-")])
    overall["parent_requirements"] = score_group([c for c in criteria if c["id"].startswith("REQ-")])
    overall["scoring_scope"] = "all_explicit_criteria_including_parent_requirements"
    counts = overall["counts"]
    eligible = overall["eligible_weight"]
    eligible_count = overall["eligible_count"]
    warnings = list(requirements.get("warnings", []))
    if source.get("capture", {}).get("issue_completeness") != "verified_by_pagination":
        warnings.append("Normative issue coverage is NOT independently verified: offline/manual input may omit context, amendments or comments. Confirm the full issue before claiming closure.")
    if not eligible:
        warnings.append("No applicable explicit criteria: no defensible completion percentage")
    elif overall["assessment_state"] == "NOT_ASSESSED":
        warnings.append("No checks were evaluated: NOT ASSESSED. N/A is not 0% implemented. Acquire the pinned repository and/or exact-SHA test receipts; use a qualitative source-backed review if neither is available.")
    elif overall["assessment_state"] == "INCOMPLETE_PLAN":
        warnings.append("INCOMPLETE PLAN: some applicable requirements have no checks. N/A is not 0% implemented; complete the evidence plan before any numeric headline.")
    elif overall["completion_verified_pct"] is None:
        warnings.append("No fully PASS or FAIL criterion was established despite some observed probes; runtime proof may still be missing. Do not emit a numerical implementation-progress headline.")
    elif counts["UNVERIFIED"]:
        warnings.append("Unmapped requirements are UNVERIFIED; 0% verified does not imply 0% implemented")
    if overall["parent_requirements"]["eligible_count"] and overall["acceptance_criteria"]["eligible_count"]:
        warnings.append("REQ parent objectives and AC acceptance criteria overlap; their combined all-criteria evidence floor is NOT a functional-completion percentage. Report acceptance and parent evidence separately.")
    if any(c["status"] == "PARTIAL" and c["proof_policy"] == "runtime" for c in criteria):
        warnings.append("Static checks alone cannot prove runtime behavior")
    return {
        "schema": REPORT_SCHEMA,
        "algorithm_version": "score-v1.1.0",
        "repository": source["repository"],
        "pull_request": {k: source["pull_request"][k] for k in ("number", "url", "base_sha", "head_sha")},
        "issue": {k: source["issue"][k] for k in ("number", "url")},
        "identity": {**refs, "evidence_digest": digest(evidence)},
        "overall": overall,
        "criteria": criteria,
        "warnings": sorted(set(warnings)),
        # Parser only certifies explicit criteria, not exhaustive normative scope.
        "verdict": "INCONCLUSIVE" if not eligible or counts["UNVERIFIED"] else (
            "COMPLIANT_KNOWN_SCOPE" if counts["PASS"] == eligible_count else
            "NON_COMPLIANT_KNOWN_SCOPE" if counts["FAIL"] and not (counts["PASS"] or counts["PARTIAL"]) else
            "PARTIALLY_COMPLIANT_KNOWN_SCOPE"),
    }


def markdown_report(report: dict) -> str:
    require_schema(report, REPORT_SCHEMA)
    total = report["overall"]
    pct_string = lambda value: f"{value}%" if value is not None else "N/A"
    if total["assessment_state"] == "NOT_ASSESSED":
        verified_line = "**Verified completion:** NOT ASSESSED (N/A; no checks were evaluated; not 0% implementation)"
    elif total["completion_verified_pct"] is None:
        verified_line = f"**Verified evidence floor:** N/A ({total['assessment_state']}; no defensible numeric result)"
    else:
        verified_line = f"**Verified evidence floor:** {pct_string(total['completion_verified_pct'])} (not functional implementation progress)"
    lines = [
        f"# Deterministic PR audit — {report['repository']} PR #{report['pull_request']['number']}", "",
        f"- **Verdict:** {report['verdict']}",
        f"- **Audit readiness:** {total['assessment_state']} ({total['observed_checks']}/{total['declared_checks']} checks evaluated)",
        f"- {verified_line}",
        f"- **Possible mathematical ceiling:** {pct_string(total['completion_possible_upper_pct'])} (NOT a forecast)",
        f"- **Passing declared checks:** {pct_string(total['probes_pass_pct'])} (not functional completion)",
        f"- **Requirements with check plans:** {pct_string(total['requirements_mapped_pct'])}",
        f"- **Head SHA:** `{report['pull_request']['head_sha']}`",
        f"- **Requirements digest:** `{report['identity']['requirements_digest']}`",
        f"- **Check plan digest:** `{report['identity']['checks_digest']}`", "",
    ]
    ac = total["acceptance_criteria"]
    parent = total["parent_requirements"]
    if ac["eligible_count"]:
        lines += ["## Acceptance criteria (AC), separate from parent REQs", "",
                  f"- **Acceptance criteria:** {ac['eligible_count']}; {ac['requirements_with_observations']} with observed checks",
                  f"- **Acceptance evidence floor:** {pct_string(ac['completion_verified_pct'])} ({ac['assessment_state']}; not implementation progress)",
                  f"- **Parent REQ evidence floor:** {pct_string(parent['completion_verified_pct'])} ({parent['eligible_count']} parent requirements; not added to AC denominator)", ""]
    lines += ["| Status | Count |", "|---|---:|"]
    for status, count in total["counts"].items():
        lines.append(f"| {status} | {count} |")
    lines += ["", "## Criteria", "", "| Criterion | Status | Passed checks | Source |", "|---|---|---:|---|"]
    for c in report["criteria"]:
        passed = sum(x["status"] == "PASS" for x in c["checks"])
        lines.append(f"| {c['id']} | {c['status']} | {passed}/{len(c['checks'])} | {c['source']}:{c['line']} |")
    lines += ["", "## Outstanding criteria", ""]
    for c in report["criteria"]:
        if c["status"] not in ("PASS", "NOT_APPLICABLE"):
            lines.append(f"- **{c['id']} ({c['status']})**: {c['text']}")
            for ck in c["checks"]:
                if ck["status"] != "PASS":
                    lines.append(f"  - {ck['id']}: {ck['status']} — {ck['reason']}")
    lines += ["", "## Limitations and warnings", ""]
    lines += [f"- {w}" for w in report["warnings"]]
    lines += ["- Scope is explicit REQ/AC and acceptance checkboxes only, not necessarily the complete normative issue.",
              "- A passing text/file probe is not equivalent to verified product behavior.",
              "- Test receipts prove that the declared command exited as expected at the captured SHA; test quality must be reviewed independently.",
              "- Replaying the same frozen evidence and scoring contract is byte-for-byte deterministic; a fresh audit can produce new evidence."]
    return "\n".join(lines) + "\n"


def compare_reports(left: dict, right: dict) -> dict:
    require_schema(left, REPORT_SCHEMA)
    require_schema(right, REPORT_SCHEMA)
    comparable = (
        left["identity"]["requirements_digest"] == right["identity"]["requirements_digest"] and
        left["identity"]["checks_digest"] == right["identity"]["checks_digest"] and
        left["algorithm_version"] == right["algorithm_version"]
    )
    if not comparable:
        raise AuditError("Not comparable: requirements, check plan, or scoring algorithm differs. Rebaseline first.")
    if left["algorithm_version"] != "score-v1.1.0":
        raise AuditError("Not comparable: legacy reports predate the no-evidence readiness guard. Recompute under score-v1.1.0.")
    if (left["overall"].get("completion_verified_pct") is None or
        right["overall"].get("completion_verified_pct") is None):
        raise AuditError("Not comparable: at least one candidate was NOT ASSESSED or has incomplete evidence/plan. Missing proof cannot count as equal progress.")
    old = {c["id"]: c for c in left["criteria"]}
    changes = []
    for c in right["criteria"]:
        prior = old[c["id"]]
        if prior["status"] != c["status"]:
            changes.append({"id": c["id"], "before": prior["status"], "after": c["status"]})
    return {
        "schema": "pr-audit/comparison/v1",
        "left": {"head_sha": left["pull_request"]["head_sha"], "verified_pct": left["overall"]["completion_verified_pct"]},
        "right": {"head_sha": right["pull_request"]["head_sha"], "verified_pct": right["overall"]["completion_verified_pct"]},
        "changed_requirements": changes,
        "scope_warning": "Evidence-floor comparison only; not a functional-implementation-progress comparison." if (
            left["overall"].get("assessment_state") != "EVALUATED_KNOWN_SCOPE" or
            right["overall"].get("assessment_state") != "EVALUATED_KNOWN_SCOPE"
        ) else None,
    }


# Advisory only: lexical hints never enter the compliance score.
_STOPWORDS = frozenset({
    "about", "after", "again", "allow", "also", "before", "between", "changes",
    "should", "could", "would", "there", "their", "through", "with", "from",
    "that", "this", "when", "where", "which", "have", "into", "must", "user",
    "users", "using", "to" "dos", "para", "como", "deve", "dever", "pode", "com", 
    "entre", "cada", "essa", "esse", "esta", "este", "to" "dos", "todas", "sistema",
    "feature", "requirement", "implement", "implementation", "support", "provide",
})


def term_set(value: str) -> set[str]:
    return {t for t in re.findall(r"[^\W\d_]{4,}", value.casefold()) if t not in _STOPWORDS}


def suggest_paths(source: dict, requirements: dict, repo_path: str | Path, max_candidates: int = 5) -> dict:
    """Rank changed source files using pinned tree lexical overlap. Never call it proof."""
    require_schema(source, SOURCE_SCHEMA)
    if requirements["spec_digest"] != digest(spec_material(source)):
        raise AuditError("Requirements are not bound to this issue snapshot")
    head = source["pull_request"]["head_sha"]
    verify_commit_available(repo_path, head)
    paths = source["pull_request"]["files"]
    indexed = []
    for path in paths:
        try:
            assert_valid_path(path)
        except AuditError:
            continue
        # Git show is read-only, and failed retrieval (deleted files) is not proof.
        completed = subprocess.run(["git", "-C", str(repo_path), "show", f"{head}:{path}"], capture_output=True)
        if completed.returncode or len(completed.stdout) > 524288 or b"\0" in completed.stdout:
            continue
        name_terms = term_set(Path(path).stem.replace("-", " ").replace("_", " ") + " " + path)
        body_terms = term_set(completed.stdout.decode("utf-8", "replace"))
        indexed.append((path, name_terms, body_terms))
    result = {}
    for criterion in requirements["criteria"]:
        words = term_set(criterion["text"])
        candidates = []
        for path, name_terms, body_terms in indexed:
            named, contained = words & name_terms, words & body_terms
            points = len(named) * 3 + len(contained)
            if points:
                candidates.append({"path": path, "signal_score": points,
                                   "matched_terms": sorted(named | contained)})
        candidates.sort(key=lambda x: (-x["signal_score"], x["path"]))
        result[criterion["id"]] = candidates[:max_candidates]
    return {"schema": "pr-audit/hints/v1", "source_digest": digest(source),
            "requirements_digest": digest(requirements), "head_sha": head,
            "warning": "Lexical candidates only; not evidence and never used for completion scoring",
            "candidates": result}
