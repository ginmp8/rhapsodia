#!/usr/bin/env python3
"""Portable structural helper for skill-change-gate.

The helper is intentionally host-neutral and standard-library only. It inspects one
candidate skill folder and, optionally, a before folder. Its JSON output is
mechanical evidence for the semantic gate; it is not a substitute for reviewer
judgment, behavioral benchmarks, or host/runtime execution evidence.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import py_compile
import re
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


RECEIPT_VERSION = 2
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.DOTALL)
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
RESOURCE_REF_RE = re.compile(r"`((?:scripts|references|assets|evals|examples|tests)/[^`\s]+\.[A-Za-z0-9]+)`")
SCAFFOLD_WORDS = ["TO" + "DO", "FIX" + "ME", "T" + "BD", "PLACE" + "HOLDER", "X" + "XX"]
SCAFFOLD_RE = re.compile(r"\b(" + "|".join(SCAFFOLD_WORDS) + r")\b", re.IGNORECASE)
PORTABILITY_PRIVATE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("openai-internal-skill-uri", re.compile(r"\bskills://", re.IGNORECASE)),
    ("sandbox-uri", re.compile(r"\bsandbox:/", re.IGNORECASE)),
    ("openai-internal-tool", re.compile(r"\b(?:tools\.skills__|functions\.exec|api_tool\.|container\.exec|python_user_visible)\b")),
    ("openai-sandbox-path", re.compile(r"/(?:home/oai|mnt/data)(?:/|\b)", re.IGNORECASE)),
)
NOISE_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
FORBIDDEN_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules"}
FORBIDDEN_SUFFIXES = {".zip", ".pyc", ".pyo"}
SENSITIVE_RE = re.compile(r"(?i)(?:^|[/_.-])(secrets?|credentials?|passwords?|api[_-]?keys?|private[_-]?keys?)(?:$|[/_.-])")


@dataclass
class Finding:
    severity: str
    area: str
    code: str
    message: str
    evidence: dict[str, object] = field(default_factory=dict)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def canonical(path: str | Path) -> Path:
    try:
        return Path(path).expanduser().resolve(strict=False)
    except RuntimeError as exc:
        raise ValueError(f"path contains a symbolic-link cycle: {path}") from exc


def path_inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def fsync_directory(directory: Path) -> None:
    if os.name == "nt":
        return
    try:
        fd = os.open(directory, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        fsync_directory(path.parent)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise


def emit(result: dict[str, object], json_path: Path | None) -> None:
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if json_path is not None:
        atomic_write_text(json_path, text)
    sys.stdout.write(text)
    sys.stdout.flush()


def preflight_report_path(target: Path, before: Path | None, raw: str | None) -> tuple[Path | None, dict[str, object] | None]:
    if not raw:
        return None, None
    try:
        out = canonical(raw)
    except ValueError as exc:
        return None, failure_receipt("preflight", "report/path-cycle", str(exc))
    if path_inside(target, out):
        return None, failure_receipt(
            "preflight",
            "report/inside-target",
            "--json must resolve outside the target skill root",
            report=str(out),
            target=str(target),
        )
    if before is not None and path_inside(before, out):
        return None, failure_receipt(
            "preflight",
            "report/inside-before",
            "--json must resolve outside the before skill root",
            report=str(out),
            before=str(before),
        )
    if out.exists() and not out.is_file():
        return None, failure_receipt("preflight", "report/not-file", "--json must identify a file target", report=str(out))
    return out, None


def failure_receipt(stage: str, code: str, message: str, **evidence: object) -> dict[str, object]:
    return {
        "receipt_version": RECEIPT_VERSION,
        "status": "fail",
        "stage": stage,
        "policy": None,
        "profile": None,
        "target": None,
        "before": None,
        "target_tree_sha256": None,
        "before_tree_sha256": None,
        "change_set": {"added": [], "removed": [], "changed": []},
        "findings": [asdict(Finding("blocking", "evidence", code, message, dict(evidence)))],
        "errors": 1,
        "warnings": 0,
        "note": "static helper output; semantic gate decision still requires skill review",
    }


def root_skill_md(target: Path, findings: list[Finding]) -> Path | None:
    candidate = target / "SKILL.md"
    nested = [p for p in target.rglob("SKILL.md") if p != candidate and ".git" not in p.parts]
    if not candidate.exists():
        findings.append(Finding("blocking", "package", "package/root-skill-missing", "root SKILL.md is missing"))
        if nested:
            findings.append(Finding("blocking", "package", "package/ambiguous-root", f"found nested SKILL.md files without root: {len(nested)}"))
        return None
    if nested:
        findings.append(Finding("material", "package", "package/nested-skills", f"nested SKILL.md files exist and may indicate ambiguous package roots: {len(nested)}"))
    return candidate


def _strip_yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _validate_plain_yaml_scalar(value: str) -> str | None:
    """Return a portable YAML syntax error for common invalid plain scalars.

    Agent Skills frontmatter is intentionally simple. YAML reserves ``: `` inside
    an unquoted plain scalar as a mapping separator, so descriptions containing
    that sequence must be quoted or expressed as a block scalar. This catches the
    class of syntax error that a line-split parser would otherwise silently accept.
    """
    stripped = value.strip()
    if not stripped or stripped[0] in {"'", '"', "[", "{"}:
        return None
    if re.search(r":(?:[ \t]|$)", stripped):
        return "unquoted plain scalar contains a mapping separator ': '; quote it or use a block scalar"
    return None


def parse_frontmatter(text: str, findings: list[Finding]) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        findings.append(Finding("blocking", "frontmatter", "frontmatter/missing", "SKILL.md is missing YAML frontmatter delimited by ---"))
        return {}
    lines = match.group(1).splitlines()
    data: dict[str, str] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line.startswith((" ", "\t")):
            i += 1
            continue
        if ":" not in line:
            findings.append(Finding("blocking", "frontmatter", "frontmatter/invalid-line", f"invalid top-level frontmatter line: {line}"))
            i += 1
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value in {"|", ">", "|-", ">-", "|+", ">+"}:
            mode = raw_value[0]
            parts: list[str] = []
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i].startswith((" ", "\t"))):
                parts.append(lines[i].strip())
                i += 1
            data[key] = ("\n" if mode == "|" else " ").join(parts).strip()
            continue
        scalar_error = _validate_plain_yaml_scalar(raw_value)
        if scalar_error:
            findings.append(Finding("blocking", "frontmatter", "frontmatter/yaml-invalid", f"invalid YAML for '{key}': {scalar_error}"))
        if raw_value.startswith(("'", '"')) and (len(raw_value) < 2 or raw_value[-1] != raw_value[0]):
            findings.append(Finding("blocking", "frontmatter", "frontmatter/yaml-invalid", f"invalid YAML for '{key}': unterminated quoted scalar"))
        data[key] = _strip_yaml_scalar(raw_value)
        i += 1

    name = data.get("name", "")
    description = data.get("description", "")
    if not name:
        findings.append(Finding("blocking", "frontmatter", "frontmatter/name-missing", "missing required frontmatter field: name"))
    elif len(name) > 64:
        findings.append(Finding("blocking", "frontmatter", "frontmatter/name-too-long", "frontmatter name exceeds 64 characters"))
    elif not NAME_RE.fullmatch(name):
        findings.append(Finding("blocking", "frontmatter", "frontmatter/name-invalid", "frontmatter name is not lowercase hyphen-case"))
    if not description:
        findings.append(Finding("blocking", "frontmatter", "frontmatter/description-missing", "missing required frontmatter field: description"))
    elif len(description) > 1024:
        findings.append(Finding("blocking", "frontmatter", "frontmatter/description-too-long", "frontmatter description exceeds 1024 characters"))
    elif len(description.split()) < 20:
        findings.append(Finding("material", "activation", "activation/description-short", "frontmatter description may be too short for reliable activation"))
    return data


def iter_manifest_entries(root: Path) -> Iterable[tuple[str, dict[str, object]]]:
    for path in sorted(root.rglob("*")):
        rel_path = path.relative_to(root)
        if any(part in NOISE_DIRS for part in rel_path.parts):
            continue
        rel = rel_path.as_posix()
        if path.is_symlink():
            yield rel, {"type": "symlink", "target": os.readlink(path)}
            continue
        if not path.is_file():
            continue
        h = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(chunk)
        yield rel, {"type": "file", "size": path.stat().st_size, "sha256": h.hexdigest()}


def tree_manifest(root: Path) -> dict[str, dict[str, object]]:
    return dict(iter_manifest_entries(root))


def tree_hash(manifest: dict[str, dict[str, object]]) -> str:
    # Canonical list form intentionally matches the reproducibility-engineer
    # package receipt algorithm without importing or depending on that skill.
    rows = [{"path": rel, **manifest[rel]} for rel in sorted(manifest)]
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def change_set(before_manifest: dict[str, dict[str, object]], after_manifest: dict[str, dict[str, object]]) -> dict[str, list[str]]:
    before_keys = set(before_manifest)
    after_keys = set(after_manifest)
    return {
        "added": sorted(after_keys - before_keys),
        "removed": sorted(before_keys - after_keys),
        "changed": sorted(k for k in before_keys & after_keys if before_manifest[k] != after_manifest[k]),
    }


def pattern_matches(rel: str, pattern: str) -> bool:
    pattern = pattern.replace("\\", "/").strip().lstrip("./")
    if not pattern:
        return False
    if any(ch in pattern for ch in "*?["):
        if fnmatch.fnmatch(rel, pattern):
            return True
        if pattern.endswith("/**") and rel.startswith(pattern[:-3].rstrip("/") + "/"):
            return True
        return False
    return rel == pattern or rel.startswith(pattern.rstrip("/") + "/")


def check_protected_changes(changes: dict[str, list[str]], patterns: list[str], findings: list[Finding]) -> list[str]:
    touched = sorted({rel for values in changes.values() for rel in values if any(pattern_matches(rel, p) for p in patterns)})
    for rel in touched:
        findings.append(Finding(
            "blocking",
            "evidence",
            "evidence/protected-path-changed",
            f"protected path changed: {rel}",
            {"path": rel, "patterns": [p for p in patterns if pattern_matches(rel, p)]},
        ))
    return touched


def check_links(root: Path, skill_text: str, findings: list[Finding]) -> None:
    seen: set[str] = set()
    for raw in LINK_RE.findall(skill_text):
        link = raw.split("#", 1)[0].strip().strip("<>")
        if not link or re.match(r"^[a-z][a-z0-9+.-]*://", link, re.IGNORECASE) or link.startswith("mailto:"):
            continue
        seen.add(link)
    for raw in RESOURCE_REF_RE.findall(skill_text):
        seen.add(raw.rstrip(".,;:)"))

    root_resolved = root.resolve()
    for link in sorted(seen):
        target = canonical(root / link)
        if not path_inside(root_resolved, target):
            findings.append(Finding("blocking", "references", "references/path-escape", f"local reference escapes package: {link}"))
            continue
        if not target.exists():
            findings.append(Finding("blocking", "references", "references/missing", f"local reference does not resolve: {link}"))


def check_hygiene(root: Path, findings: list[Finding]) -> None:
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        base = Path(dirpath)
        for dirname in list(dirnames):
            p = base / dirname
            rel = p.relative_to(root).as_posix()
            if p.is_symlink():
                findings.append(Finding("blocking", "package", "package/symlink", f"symlink is not allowed in portable package: {rel}", {"target": os.readlink(p)}))
                dirnames.remove(dirname)
                continue
            if dirname in FORBIDDEN_DIRS:
                severity = "blocking" if dirname in {".git", "node_modules"} else "material"
                findings.append(Finding(severity, "package", "package/forbidden-directory", f"package contains forbidden or generated directory: {rel}"))
                dirnames.remove(dirname)
        for filename in filenames:
            p = base / filename
            rel = p.relative_to(root).as_posix()
            if p.is_symlink():
                findings.append(Finding("blocking", "package", "package/symlink", f"symlink is not allowed in portable package: {rel}", {"target": os.readlink(p)}))
                continue
            if p.suffix.lower() in FORBIDDEN_SUFFIXES:
                findings.append(Finding("material", "package", "package/generated-artifact", f"generated/archive artifact should not be packaged: {rel}"))
            if SENSITIVE_RE.search(rel):
                findings.append(Finding("blocking", "safety", "safety/sensitive-path", f"sensitive-looking file path included: {rel}"))


def check_placeholders(root: Path, findings: list[Finding]) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink() or path.suffix.lower() not in {".md", ".txt", ".yaml", ".yml", ".json"}:
            continue
        if any(part in NOISE_DIRS for part in path.relative_to(root).parts):
            continue
        text = read_text(path)
        if SCAFFOLD_RE.search(text) and "template" not in {part.lower() for part in path.parts}:
            findings.append(Finding("material", "content", "content/scaffold-marker", f"scaffold marker remains in {path.relative_to(root).as_posix()}"))


def check_python_scripts(root: Path, findings: list[Finding]) -> None:
    scripts = root / "scripts"
    if not scripts.exists():
        return
    for script in scripts.rglob("*.py"):
        if script.is_symlink():
            continue
        try:
            fd, tmp_name = tempfile.mkstemp(suffix=".pyc")
            os.close(fd)
            Path(tmp_name).unlink(missing_ok=True)
            py_compile.compile(str(script), cfile=tmp_name, doraise=True)
            Path(tmp_name).unlink(missing_ok=True)
        except py_compile.PyCompileError as exc:
            findings.append(Finding("blocking", "scripts", "scripts/python-syntax", f"python script does not compile: {script.relative_to(root).as_posix()}: {exc.msg}"))


def check_portability(root: Path, skill_text: str, frontmatter: dict[str, str], profile: str, findings: list[Finding]) -> dict[str, object]:
    name = frontmatter.get("name")
    if name and root.name != name:
        findings.append(Finding(
            "blocking" if profile == "portable" else "material",
            "portability",
            "portability/root-name-mismatch",
            f"skill directory name '{root.name}' does not match SKILL.md name '{name}'",
        ))

    private_hits: list[dict[str, str]] = []
    for code, pattern in PORTABILITY_PRIVATE_PATTERNS:
        match = pattern.search(skill_text)
        if match:
            private_hits.append({"code": code, "match": match.group(0)})
            findings.append(Finding(
                "material",
                "portability",
                "portability/host-private-core-dependency",
                f"portable core references a host-private runtime primitive: {match.group(0)}",
                {"pattern": code},
            ))

    adapters: list[str] = []
    if (root / "agents" / "openai.yaml").is_file():
        adapters.append("openai")
    if (root / ".cursor").exists():
        adapters.append("cursor")
    if (root / ".claude").exists():
        adapters.append("claude")

    if profile == "openai":
        openai = root / "agents" / "openai.yaml"
        if not openai.is_file():
            findings.append(Finding("blocking", "portability", "openai/adapter-missing", "OpenAI profile requires agents/openai.yaml"))
        else:
            text = read_text(openai)
            if not re.search(r"(?m)^interface:\s*$", text) or not re.search(r"(?m)^\s+display_name:\s*\S", text):
                findings.append(Finding("blocking", "portability", "openai/adapter-invalid", "agents/openai.yaml is missing interface.display_name"))
            for key in ("icon_small", "icon_large"):
                match = re.search(rf"(?m)^\s+{key}:\s*(.+?)\s*$", text)
                if match:
                    raw = _strip_yaml_scalar(match.group(1))
                    icon = canonical(root / raw)
                    if not path_inside(root.resolve(), icon) or not icon.is_file():
                        findings.append(Finding("blocking", "portability", "openai/icon-missing", f"{key} does not resolve inside package: {raw}"))

    return {"host_adapters": sorted(set(adapters)), "private_core_hits": private_hits}


def compare_frontmatter(before: Path, after: Path, findings: list[Finding]) -> None:
    before_skill = before / "SKILL.md"
    after_skill = after / "SKILL.md"
    if not before_skill.is_file() or not after_skill.is_file():
        return
    b_findings: list[Finding] = []
    a_findings: list[Finding] = []
    b_front = parse_frontmatter(read_text(before_skill), b_findings)
    a_front = parse_frontmatter(read_text(after_skill), a_findings)
    if b_front.get("name") and a_front.get("name") and b_front["name"] != a_front["name"]:
        findings.append(Finding("material", "identity", "identity/name-changed", f"skill name changed from {b_front['name']} to {a_front['name']}"))
    if b_front.get("description") and a_front.get("description"):
        before_words = len(b_front["description"].split())
        after_words = len(a_front["description"].split())
        if after_words < max(15, int(before_words * 0.45)):
            findings.append(Finding("material", "activation", "activation/description-sharply-shortened", "frontmatter description was sharply shortened; verify activation recall and boundaries"))


def check_expected_hash(actual: str | None, expected: str | None, label: str, findings: list[Finding]) -> None:
    if not expected:
        return
    normalized = expected.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", normalized):
        findings.append(Finding("blocking", "evidence", f"evidence/{label}-expected-hash-invalid", f"expected {label} SHA-256 is not a 64-character hex digest"))
        return
    if actual != normalized:
        findings.append(Finding(
            "blocking",
            "evidence",
            f"evidence/{label}-identity-mismatch",
            f"{label} tree identity differs from the frozen expected hash",
            {"expected": normalized, "actual": actual},
        ))


def check_artifact_receipt(receipt_path: Path | None, target_root: Path, target_hash: str | None, findings: list[Finding]) -> dict[str, object] | None:
    if receipt_path is None:
        return None
    resolved = canonical(receipt_path)
    if path_inside(target_root, resolved):
        findings.append(Finding("blocking", "delivery", "delivery/receipt-inside-target", "artifact receipt is inside the candidate skill tree and therefore changes the subject it claims to identify", {"receipt": str(resolved)}))
        return {"path": str(resolved), "status": "invalid"}
    try:
        data = json.loads(resolved.read_text(encoding="utf-8"))
    except Exception as exc:
        findings.append(Finding("blocking", "delivery", "delivery/receipt-unreadable", f"artifact receipt is not readable JSON: {exc}", {"receipt": str(resolved)}))
        return {"path": str(resolved), "status": "invalid"}
    status = data.get("status")
    if status != "pass":
        findings.append(Finding("blocking", "delivery", "delivery/receipt-not-pass", "artifact receipt does not report pass", {"receipt": str(resolved), "status": status}))
    identity_field = None
    identity = None
    for key in ("source_tree_sha256", "candidate_tree_sha256", "target_tree_sha256"):
        value = data.get(key)
        if isinstance(value, str) and value:
            identity_field = key
            identity = value.strip().lower()
            break
    if identity is None:
        findings.append(Finding("material", "delivery", "delivery/receipt-missing-candidate-identity", "artifact receipt does not identify the candidate tree it was built from", {"receipt": str(resolved)}))
    elif target_hash is not None and identity != target_hash:
        findings.append(Finding("blocking", "delivery", "delivery/receipt-candidate-mismatch", "artifact receipt refers to candidate bytes different from the gated candidate", {"receipt": str(resolved), "field": identity_field, "receipt_identity": identity, "target_identity": target_hash}))
    return {"path": str(resolved), "status": status, "identity_field": identity_field, "identity": identity}


def status_from(findings: list[Finding], policy: str) -> str:
    if any(f.severity == "blocking" for f in findings):
        return "fail"
    if any(f.severity == "material" for f in findings):
        return "fail" if policy == "strict" else "pass-with-warnings"
    return "pass"


def run(
    target: Path,
    before: Path | None,
    *,
    policy: str,
    profile: str,
    expected_before_sha256: str | None,
    expected_target_sha256: str | None,
    protected_paths: list[str],
    artifact_receipt: Path | None,
) -> dict[str, object]:
    findings: list[Finding] = []
    target = canonical(target)
    before = canonical(before) if before is not None else None

    if not target.exists() or not target.is_dir():
        findings.append(Finding("blocking", "package", "package/target-missing", "target does not exist or is not a directory"))
        return build_result(target, before, policy, profile, findings)
    if before is not None and (not before.exists() or not before.is_dir()):
        findings.append(Finding("blocking", "evidence", "evidence/before-missing", "before path does not exist or is not a directory"))
        before = None

    skill = root_skill_md(target, findings)
    frontmatter: dict[str, str] = {}
    skill_text = ""
    if skill is not None:
        skill_text = read_text(skill)
        frontmatter = parse_frontmatter(skill_text, findings)
        check_links(target, skill_text, findings)
    check_hygiene(target, findings)
    check_placeholders(target, findings)
    check_python_scripts(target, findings)
    portability = check_portability(target, skill_text, frontmatter, profile, findings) if skill_text else {"host_adapters": [], "private_core_hits": []}

    target_manifest = tree_manifest(target)
    target_hash = tree_hash(target_manifest)
    before_manifest: dict[str, dict[str, object]] = {}
    before_hash = None
    changes = {"added": [], "removed": [], "changed": []}
    if before is not None:
        before_manifest = tree_manifest(before)
        before_hash = tree_hash(before_manifest)
        changes = change_set(before_manifest, target_manifest)
        compare_frontmatter(before, target, findings)

    check_expected_hash(before_hash, expected_before_sha256, "before", findings)
    check_expected_hash(target_hash, expected_target_sha256, "target", findings)
    protected_touched = check_protected_changes(changes, protected_paths, findings) if before is not None else []
    receipt_summary = check_artifact_receipt(artifact_receipt, target, target_hash, findings)

    return build_result(
        target,
        before,
        policy,
        profile,
        findings,
        target_hash=target_hash,
        before_hash=before_hash,
        changes=changes,
        protected_paths=protected_paths,
        protected_touched=protected_touched,
        portability=portability,
        artifact_receipt=receipt_summary,
        manifest_counts={"target": len(target_manifest), "before": len(before_manifest) if before is not None else None},
    )


def build_result(
    target: Path,
    before: Path | None,
    policy: str,
    profile: str,
    findings: list[Finding],
    *,
    target_hash: str | None = None,
    before_hash: str | None = None,
    changes: dict[str, list[str]] | None = None,
    protected_paths: list[str] | None = None,
    protected_touched: list[str] | None = None,
    portability: dict[str, object] | None = None,
    artifact_receipt: dict[str, object] | None = None,
    manifest_counts: dict[str, object] | None = None,
) -> dict[str, object]:
    changes = changes or {"added": [], "removed": [], "changed": []}
    status = status_from(findings, policy)
    return {
        "receipt_version": RECEIPT_VERSION,
        "status": status,
        "stage": "complete",
        "policy": policy,
        "profile": profile,
        "target": str(target),
        "before": str(before) if before is not None else None,
        "target_tree_sha256": target_hash,
        "before_tree_sha256": before_hash,
        "manifest_counts": manifest_counts or {"target": None, "before": None},
        "change_set": changes,
        "protected_paths": protected_paths or [],
        "protected_path_changes": protected_touched or [],
        "artifact_receipt": artifact_receipt,
        "portability": portability or {"host_adapters": [], "private_core_hits": []},
        "findings": [asdict(f) for f in findings],
        "errors": sum(1 for f in findings if f.severity == "blocking"),
        "warnings": sum(1 for f in findings if f.severity == "material"),
        "note": "static helper output; semantic gate decision still requires skill review",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run portable static checks for a candidate Agent Skill change.")
    parser.add_argument("--target", required=True, help="after/candidate skill folder")
    parser.add_argument("--before", help="optional before skill folder")
    parser.add_argument("--policy", choices=("normal", "strict", "advisory"), default="normal")
    parser.add_argument("--profile", choices=("portable", "openai"), default="portable")
    parser.add_argument("--expected-before-sha256", help="optional frozen SHA-256 for the before tree")
    parser.add_argument("--expected-target-sha256", help="optional frozen SHA-256 for the candidate tree")
    parser.add_argument("--protected-path", action="append", default=[], help="relative path, directory, or glob that must not change between before and target; repeatable")
    parser.add_argument("--artifact-receipt", help="optional JSON receipt whose candidate tree identity must match the gated target")
    parser.add_argument("--json", help="optional JSON report path; must resolve outside target/before roots")
    args = parser.parse_args(argv)

    try:
        target = canonical(args.target)
        before = canonical(args.before) if args.before else None
        report_path, preflight_failure = preflight_report_path(target, before, args.json)
        if preflight_failure is not None:
            preflight_failure["policy"] = args.policy
            preflight_failure["profile"] = args.profile
            preflight_failure["target"] = str(target)
            preflight_failure["before"] = str(before) if before is not None else None
            emit(preflight_failure, None)
            return 1

        result = run(
            target,
            before,
            policy=args.policy,
            profile=args.profile,
            expected_before_sha256=args.expected_before_sha256,
            expected_target_sha256=args.expected_target_sha256,
            protected_paths=args.protected_path,
            artifact_receipt=Path(args.artifact_receipt) if args.artifact_receipt else None,
        )
        emit(result, report_path)
        return 0 if result["status"] in {"pass", "pass-with-warnings"} else 1
    except Exception as exc:
        result = failure_receipt("exception", "gate/unhandled-exception", str(exc))
        result["policy"] = args.policy
        result["profile"] = args.profile
        result["target"] = str(args.target)
        result["before"] = str(args.before) if args.before else None
        try:
            emit(result, None)
        finally:
            return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
