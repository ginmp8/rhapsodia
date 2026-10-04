#!/usr/bin/env python3
"""Deterministic static analyzer for EF Core migration conflicts and hazards.

Version 3 keeps a portable Python-only core, binds all supplied evidence by SHA-256,
and makes EF/provider/runtime judgments explicitly version/context aware. Optional
semantic evidence may enrich the analysis without becoming a runtime dependency.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

ANALYSIS_VERSION = "3.0.0"
REPORT_SCHEMA_VERSION = "3.0"
SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
MAIN_MIGRATION_RE = re.compile(r"^\d{14}_.+\.cs$")
EXCLUDED_RE = re.compile(r"(\.Designer\.cs$|ModelSnapshot\.cs$)")
MUTATING_SQL_RE = re.compile(r"\b(create|alter|drop|truncate|merge|update|delete|insert|exec|execute)\b", re.I)
NON_IDEMPOTENT_UPDATE_RE = re.compile(r"\bset\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\1\s*[+\-]", re.I)
STARTUP_MIGRATE_RE = re.compile(r"\bDatabase\s*\.\s*(?:Migrate|MigrateAsync)\s*\(", re.I)
BEGIN_TRANSACTION_RE = re.compile(r"\b(?:BeginTransaction|BeginTransactionAsync)\s*\(", re.I)
RUNTIME_DEPENDENCY_PATTERNS = {
    "DateTime.Now": re.compile(r"\bDateTime\s*\.\s*Now\b"),
    "DateTime.UtcNow": re.compile(r"\bDateTime\s*\.\s*UtcNow\b"),
    "Guid.NewGuid": re.compile(r"\bGuid\s*\.\s*NewGuid\s*\("),
    "Environment": re.compile(r"\bEnvironment\s*\.\s*(?:GetEnvironmentVariable|MachineName|UserName)\b"),
    "filesystem": re.compile(r"\b(?:File|Directory)\s*\.\s*(?:Read|Write|Open|Create|Delete|Enumerate|GetFiles)"),
    "network": re.compile(r"\b(?:HttpClient|WebClient)\b"),
}
KNOWN_OPS = {
    "AddColumn", "DropColumn", "AlterColumn", "RenameColumn",
    "CreateTable", "DropTable", "RenameTable", "AlterTable",
    "CreateIndex", "DropIndex", "RenameIndex",
    "AddForeignKey", "DropForeignKey",
    "AddPrimaryKey", "DropPrimaryKey",
    "AddUniqueConstraint", "DropUniqueConstraint",
    "AddCheckConstraint", "DropCheckConstraint",
    "CreateSequence", "DropSequence", "RenameSequence", "AlterSequence",
    "EnsureSchema", "DropSchema", "AlterDatabase",
    "InsertData", "UpdateData", "DeleteData",
    "Sql",
}
DATA_OPS = {"InsertData", "UpdateData", "DeleteData"}
CONSTRAINT_OPS = {"AddUniqueConstraint", "AddCheckConstraint", "AddForeignKey"}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def read_text(path: Path) -> str:
    data = read_bytes(path)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def logical_path(path: Path, repo_root: Optional[Path] = None) -> str:
    resolved = path.resolve()
    for base in (repo_root, Path.cwd().resolve()):
        if base is None:
            continue
        try:
            return resolved.relative_to(base.resolve()).as_posix()
        except ValueError:
            pass
    return resolved.as_posix()


def is_main_migration_name(name: str) -> bool:
    return bool(MAIN_MIGRATION_RE.match(name)) and not EXCLUDED_RE.search(name)


def role_for_path(path: Path) -> str:
    name = path.name
    if name.endswith("ModelSnapshot.cs"):
        return "model_snapshot"
    if name.endswith(".Designer.cs"):
        return "designer"
    if is_main_migration_name(name):
        return "migration"
    return "other"


def migration_id_from_name(path_name: str) -> Optional[str]:
    return Path(path_name).stem if re.match(r"^\d{14}_", Path(path_name).name) else None


def migration_name_from_text(path_name: str, text: str) -> str:
    match = re.search(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*Migration\b", text)
    if match:
        return match.group(1)
    stem = Path(path_name).stem
    return stem.split("_", 1)[-1]


def strip_comments(text: str) -> str:
    text = re.sub(r"//.*", "", text)
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def extract_method_body(text: str, method_name: str) -> str:
    marker = re.search(r"protected\s+override\s+void\s+" + re.escape(method_name) + r"\s*\([^)]*\)\s*\{", text)
    if not marker:
        return ""
    start = marker.end() - 1
    depth = 0
    in_string = False
    quote = ""
    escape = False
    for idx in range(start, len(text)):
        ch = text[idx]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                in_string = False
            continue
        if ch in ("'", '"'):
            in_string = True
            quote = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:idx]
    return text[start + 1:]


def find_invocations(body: str) -> List[Tuple[str, Optional[str], str]]:
    calls: List[Tuple[str, Optional[str], str]] = []
    token = "migrationBuilder."
    cursor = 0
    while True:
        start = body.find(token, cursor)
        if start < 0:
            break
        op_start = start + len(token)
        match = re.match(r"([A-Za-z_][A-Za-z0-9_]*)(?:\s*<([^>]+)>)?\s*\(", body[op_start:])
        if not match:
            cursor = op_start
            continue
        op, generic = match.group(1), match.group(2)
        paren_start = op_start + match.end() - 1
        depth = 0
        in_string = False
        quote = ""
        escape = False
        end = len(body) - 1
        for pos in range(paren_start, len(body)):
            ch = body[pos]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == quote:
                    in_string = False
                continue
            if ch in ("'", '"'):
                in_string = True
                quote = ch
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    end = pos
                    break
        calls.append((op, generic.strip() if generic else None, body[paren_start + 1:end]))
        cursor = end + 1
    return calls


def named_string(args: str, key: str) -> Optional[str]:
    for pattern in (rf"\b{re.escape(key)}\s*:\s*@?\"([^\"]*)\"", rf"\b{re.escape(key)}\s*=\s*@?\"([^\"]*)\""):
        match = re.search(pattern, args, flags=re.S)
        if match:
            return match.group(1)
    return None


def first_positional_string(args: str) -> Optional[str]:
    match = re.search(r"^\s*@?\"([^\"]*)\"", args, flags=re.S)
    return match.group(1) if match else None


def named_bool(args: str, key: str) -> Optional[bool]:
    match = re.search(rf"\b{re.escape(key)}\s*:\s*(true|false)", args, flags=re.I)
    return None if not match else match.group(1).lower() == "true"


def named_int(args: str, key: str) -> Optional[int]:
    match = re.search(rf"\b{re.escape(key)}\s*:\s*(-?\d+)", args)
    return int(match.group(1)) if match else None


def named_typeof(args: str, key: str) -> Optional[str]:
    match = re.search(rf"\b{re.escape(key)}\s*:\s*typeof\s*\(\s*([^\)]+)\s*\)", args)
    return match.group(1).strip() if match else None


def has_named(args: str, key: str) -> bool:
    return re.search(rf"\b{re.escape(key)}\s*:", args) is not None


def named_string_list(args: str, singular: str, plural: str) -> List[str]:
    one = named_string(args, singular)
    if one is not None:
        return [one]
    match = re.search(rf"\b{re.escape(plural)}\s*:\s*new(?:\s+[A-Za-z0-9_<>,\[\]]+)?\s*\[?\]?\s*\{{(.*?)\}}", args, flags=re.S)
    if not match:
        match = re.search(rf"\b{re.escape(plural)}\s*:\s*new\[\]\s*\{{(.*?)\}}", args, flags=re.S)
    return [] if not match else re.findall(r"@?\"([^\"]+)\"", match.group(1))


def extract_create_table_columns(args: str) -> List[Tuple[str, Optional[bool], bool]]:
    result: List[Tuple[str, Optional[bool], bool]] = []
    pattern = r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*table\.Column(?:<[^>]+>)?\s*\((.*?)\)"
    for match in re.finditer(pattern, args, flags=re.S):
        col_args = match.group(2)
        result.append((match.group(1), named_bool(col_args, "nullable"), has_named(col_args, "defaultValue") or has_named(col_args, "defaultValueSql") or has_named(col_args, "computedColumnSql")))
    return result


def parse_major(version: Optional[str]) -> Optional[int]:
    if not version:
        return None
    match = re.match(r"\s*(\d+)", version)
    return int(match.group(1)) if match else None


def normalize_provider(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    v = value.strip().lower()
    if v in {"sqlserver", "microsoft.entityframeworkcore.sqlserver"} or "sqlserver" in v:
        return "sqlserver"
    if v in {"postgresql", "postgres", "npgsql", "npgsql.entityframeworkcore.postgresql"} or "npgsql" in v or "postgres" in v:
        return "postgresql"
    if v in {"sqlite", "microsoft.entityframeworkcore.sqlite"} or "sqlite" in v:
        return "sqlite"
    return v


@dataclass
class FileIdentity:
    path: str
    role: str
    sha256: str
    size: int
    git_status: Optional[str] = None


@dataclass
class Operation:
    id: str
    file: str
    file_sha256: str
    migration: str
    migration_id: Optional[str]
    timestamp: Optional[str]
    scope_key: str
    method: str
    migration_order: int
    ordinal: int
    op: str
    table: Optional[str] = None
    column: Optional[str] = None
    columns: List[str] = field(default_factory=list)
    name: Optional[str] = None
    new_name: Optional[str] = None
    object_type: Optional[str] = None
    nullable: Optional[bool] = None
    old_nullable: Optional[bool] = None
    has_default: bool = False
    unique: Optional[bool] = None
    principal_table: Optional[str] = None
    principal_columns: List[str] = field(default_factory=list)
    suppress_transaction: bool = False
    clr_type: Optional[str] = None
    old_clr_type: Optional[str] = None
    store_type: Optional[str] = None
    old_store_type: Optional[str] = None
    max_length: Optional[int] = None
    old_max_length: Optional[int] = None
    precision: Optional[int] = None
    old_precision: Optional[int] = None
    scale: Optional[int] = None
    old_scale: Optional[int] = None
    raw: str = ""


@dataclass
class Finding:
    id: str
    rule_id: str
    severity: str
    confidence: str
    evidence_status: str
    gate: str
    hazard_type: str
    title: str
    files: List[str]
    operation_ids: List[str]
    evidence: str
    why: str
    recommendation: str
    validation: str
    uncertainty: str


def load_json_contract(relative: str, expected_name: Optional[str] = None) -> Tuple[Dict[str, Any], str, Path]:
    path = Path(__file__).resolve().parents[1] / relative
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    if expected_name and data.get("set_name") != expected_name:
        raise ValueError(f"invalid {relative} identity")
    return data, sha256_bytes(raw), path


def load_heuristic_set() -> Tuple[Dict[str, Any], str, Path]:
    data, digest, path = load_json_contract("references/heuristic-set.json", "migration-conflict-analyzer")
    if data.get("version") != "3.0.0" or not isinstance(data.get("rules"), dict):
        raise ValueError("invalid heuristic-set v3 contract")
    return data, digest, path


def load_provider_profiles() -> Tuple[Dict[str, Any], str, Path]:
    data, digest, path = load_json_contract("references/provider-profiles.json")
    if data.get("profile_version") != "1.0.0" or not isinstance(data.get("providers"), dict):
        raise ValueError("invalid provider-profile contract")
    return data, digest, path


def make_file_identity(path: Path, role: str, repo_root: Optional[Path] = None, git_status: Optional[str] = None) -> FileIdentity:
    data = read_bytes(path)
    return FileIdentity(logical_path(path, repo_root), role, sha256_bytes(data), len(data), git_status)


def git_run(args: Sequence[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy(); env["GIT_NO_REPLACE_OBJECTS"] = "1"
    return subprocess.run(["git", *args], cwd=cwd, env=env, check=check, text=True, capture_output=True)


def git_object_bytes(repo_root: Path, revision: str, relpath: str) -> Optional[bytes]:
    env = os.environ.copy(); env["GIT_NO_REPLACE_OBJECTS"] = "1"
    proc = subprocess.run(["git", "show", f"{revision}:{relpath}"], cwd=repo_root, env=env, check=False, capture_output=True, text=False)
    return proc.stdout if proc.returncode == 0 else None


def history_record(rel: str, data: bytes) -> Dict[str, Any]:
    try: text = data.decode("utf-8")
    except UnicodeDecodeError: text = data.decode("latin-1")
    name = Path(rel).name
    return {
        "path": rel,
        "directory": Path(rel).parent.as_posix(),
        "migration_id": migration_id_from_name(name),
        "timestamp": name[:14] if re.match(r"^\d{14}_", name) else None,
        "class_name": migration_name_from_text(name, strip_comments(text)),
        "sha256": sha256_bytes(data),
    }


def collect_git_sources(paths: Sequence[str], git_base: str) -> Tuple[List[Path], List[Path], Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]], List[str], Path]:
    start = Path(paths[0] if paths else ".").resolve()
    if start.is_file(): start = start.parent
    repo_root = Path(git_run(["rev-parse", "--show-toplevel"], start).stdout.strip()).resolve()
    base_sha = git_run(["rev-parse", f"{git_base}^{{commit}}"], repo_root).stdout.strip()
    head_sha = git_run(["rev-parse", "HEAD^{commit}"], repo_root).stdout.strip()
    merge_base_sha = git_run(["merge-base", base_sha, head_sha], repo_root).stdout.strip()
    dirty = bool(git_run(["status", "--porcelain"], repo_root).stdout.strip())
    changed: List[Dict[str, str]] = []
    main_files: List[Path] = []
    support_files: List[Path] = []
    for line in git_run(["diff", "--name-status", "--find-renames", f"{base_sha}...{head_sha}"], repo_root).stdout.splitlines():
        parts = line.split("\t")
        if not parts: continue
        status, rel = parts[0], parts[-1]
        changed.append({"status": status, "path": rel})
        path = repo_root / rel
        if status.startswith("D") or not path.exists(): continue
        role = role_for_path(path)
        if role == "migration": main_files.append(path)
        elif role in ("model_snapshot", "designer"): support_files.append(path)

    def collect_history(rev: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        history: List[Dict[str, Any]] = []; snapshots: List[Dict[str, Any]] = []
        for rel in sorted(git_run(["ls-tree", "-r", "--name-only", rev], repo_root).stdout.splitlines()):
            name = Path(rel).name
            if not is_main_migration_name(name) and not name.endswith("ModelSnapshot.cs"): continue
            data = git_object_bytes(repo_root, rev, rel)
            if data is None: continue
            if is_main_migration_name(name): history.append(history_record(rel, data))
            else: snapshots.append({"path": rel, "directory": Path(rel).parent.as_posix(), "sha256": sha256_bytes(data), "size": len(data)})
        return history, snapshots

    base_history, base_snapshots = collect_history(base_sha)
    head_history, head_snapshots = collect_history(head_sha)
    git_identity = {
        "repository_root": repo_root.as_posix(), "base_requested": git_base, "base_sha": base_sha,
        "head_sha": head_sha, "merge_base_sha": merge_base_sha, "working_tree_dirty": dirty,
        "changed_files": sorted(changed, key=lambda x: (x["path"], x["status"])),
        "base_snapshot_identity": base_snapshots, "head_snapshot_identity": head_snapshots,
        "base_history_digest": sha256_text(canonical_json(base_history)), "head_history_digest": sha256_text(canonical_json(head_history)),
    }
    return sorted(set(main_files)), sorted(set(support_files)), git_identity, base_history, head_history, [f"git diff identity: {base_sha}...{head_sha}"], repo_root


def collect_path_sources(paths: Sequence[str], include_support_files: bool, extra_snapshots: Sequence[str]) -> Tuple[List[Path], List[Path], List[str]]:
    main_files: List[Path] = []; support_files: List[Path] = []; notes: List[str] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            for child in sorted(path.rglob("*.cs")):
                role = role_for_path(child)
                if role == "migration": main_files.append(child)
                elif include_support_files and role in ("model_snapshot", "designer"): support_files.append(child)
        elif path.exists():
            role = role_for_path(path)
            if role == "migration": main_files.append(path)
            elif role in ("model_snapshot", "designer"): support_files.append(path)
            else: notes.append(f"ignored unsupported input: {raw}")
        else: notes.append(f"path not found: {raw}")
    for raw in extra_snapshots:
        path = Path(raw)
        if path.exists(): support_files.append(path)
        else: notes.append(f"snapshot not found: {raw}")
    unique_main = sorted({p.resolve(): p for p in main_files}.values(), key=lambda p: p.as_posix())
    unique_support = sorted({p.resolve(): p for p in support_files}.values(), key=lambda p: p.as_posix())
    return unique_main, unique_support, notes


def parse_designer_context(path: Path) -> Tuple[Optional[str], Optional[str]]:
    text = strip_comments(read_text(path))
    mid = None; context = None
    m = re.search(r"\[\s*Migration\s*\(\s*\"([^\"]+)\"\s*\)\s*\]", text)
    if m: mid = m.group(1)
    m = re.search(r"\[\s*DbContext\s*\(\s*typeof\s*\(\s*([A-Za-z_][A-Za-z0-9_\.]*)\s*\)\s*\)\s*\]", text)
    if m: context = m.group(1).split(".")[-1]
    return mid, context


def parse_snapshot_last_migration(path: Path) -> Optional[str]:
    m = re.search(r"LastMigrationId\s*=>\s*\"([^\"]+)\"", strip_comments(read_text(path)))
    return m.group(1) if m else None


def parse_file(path: Path, file_identity: FileIdentity, migration_order: int, dbcontext: Optional[str]) -> Tuple[List[Operation], Dict[str, Any]]:
    raw_text = read_text(path); text = strip_comments(raw_text)
    migration = migration_name_from_text(path.name, text)
    migration_id = migration_id_from_name(path.name)
    timestamp = path.name[:14] if migration_id else None
    parent_scope = str(Path(file_identity.path).parent.as_posix())
    scope_key = dbcontext or parent_scope
    up_body = extract_method_body(text, "Up"); down_body = extract_method_body(text, "Down")
    active_literals = sorted(set(re.findall(r"ActiveProvider[^\n\r\"]*\"([^\"]+)\"", text)))
    nondeterministic = [name for name, pattern in RUNTIME_DEPENDENCY_PATTERNS.items() if pattern.search(text)]
    metadata = {
        "file": file_identity.path, "file_sha256": file_identity.sha256, "migration": migration,
        "migration_id": migration_id, "timestamp": timestamp, "class_name": migration,
        "dbcontext": dbcontext, "scope_key": scope_key, "has_up": bool(up_body.strip()), "has_down": bool(down_body.strip()),
        "down_explicitly_unsupported": bool(re.search(r"throw\s+new\s+NotSupportedException", down_body)),
        "uses_active_provider": "ActiveProvider" in text, "active_provider_literals": active_literals,
        "runtime_dependency_signals": nondeterministic, "migration_order": migration_order,
    }
    operations: List[Operation] = []
    for method, body in (("Up", up_body), ("Down", down_body)):
        for ordinal, (op, generic, args) in enumerate(find_invocations(body), 1):
            table = None; column = None; columns: List[str] = []; name = None; new_name = None
            object_type = "unknown" if op not in KNOWN_OPS else "object"
            nullable = named_bool(args, "nullable"); old_nullable = named_bool(args, "oldNullable")
            has_default = has_named(args, "defaultValue") or has_named(args, "defaultValueSql") or has_named(args, "computedColumnSql")
            unique = named_bool(args, "unique"); principal_table = None; principal_columns: List[str] = []
            suppress_transaction = bool(named_bool(args, "suppressTransaction"))
            clr_type = generic; old_clr_type = named_typeof(args, "oldClrType")
            store_type = named_string(args, "type"); old_store_type = named_string(args, "oldType")
            max_length = named_int(args, "maxLength"); old_max_length = named_int(args, "oldMaxLength")
            precision = named_int(args, "precision"); old_precision = named_int(args, "oldPrecision")
            scale = named_int(args, "scale"); old_scale = named_int(args, "oldScale")
            raw = args[:1600]
            if op == "CreateTable":
                table = named_string(args, "name") or first_positional_string(args); name = table; object_type = "table"
            elif op in ("DropTable", "RenameTable", "AlterTable"):
                table = named_string(args, "name") or first_positional_string(args); name = table; new_name = named_string(args, "newName") or named_string(args, "newTable"); object_type = "table"
            elif op in ("AddColumn", "DropColumn", "AlterColumn", "RenameColumn"):
                table = named_string(args, "table"); column = named_string(args, "name") or named_string(args, "column") or first_positional_string(args); columns = [column] if column else []; name = column; new_name = named_string(args, "newName"); object_type = "column"
            elif op in ("CreateIndex", "DropIndex", "RenameIndex"):
                table = named_string(args, "table"); name = named_string(args, "name") or first_positional_string(args); new_name = named_string(args, "newName"); columns = named_string_list(args, "column", "columns"); column = columns[0] if len(columns)==1 else None; object_type = "index"
            elif op in ("AddForeignKey", "DropForeignKey"):
                table = named_string(args, "table"); name = named_string(args, "name") or first_positional_string(args); columns = named_string_list(args, "column", "columns"); column = columns[0] if len(columns)==1 else None; principal_table = named_string(args, "principalTable"); principal_columns = named_string_list(args, "principalColumn", "principalColumns"); object_type = "foreign_key"
            elif op in ("AddPrimaryKey", "DropPrimaryKey"):
                table = named_string(args, "table"); name = named_string(args, "name") or first_positional_string(args); columns = named_string_list(args, "column", "columns"); object_type = "primary_key"
            elif op in ("AddUniqueConstraint", "DropUniqueConstraint"):
                table = named_string(args, "table"); name = named_string(args, "name") or first_positional_string(args); columns = named_string_list(args, "column", "columns"); object_type = "unique_constraint"
            elif op in ("AddCheckConstraint", "DropCheckConstraint"):
                table = named_string(args, "table"); name = named_string(args, "name") or first_positional_string(args); object_type = "check_constraint"
            elif op in ("CreateSequence", "DropSequence", "RenameSequence", "AlterSequence"):
                name = named_string(args, "name") or first_positional_string(args); new_name = named_string(args, "newName"); object_type = "sequence"
            elif op in ("EnsureSchema", "DropSchema"):
                name = named_string(args, "name") or first_positional_string(args); object_type = "schema"
            elif op in DATA_OPS:
                table = named_string(args, "table") or first_positional_string(args); name = table; columns = named_string_list(args, "column", "columns"); object_type = "data"
            elif op == "Sql":
                name = "raw_sql"; object_type = "sql"; raw = first_positional_string(args) or args[:1600]
            else:
                table = named_string(args, "table"); name = named_string(args, "name") or first_positional_string(args); columns = named_string_list(args, "column", "columns"); column = columns[0] if len(columns)==1 else None
            payload = {"file_sha256": file_identity.sha256, "migration_id": migration_id, "scope_key": scope_key, "method": method, "migration_order": migration_order, "ordinal": ordinal, "op": op, "table": table, "column": column, "columns": columns, "name": name, "new_name": new_name, "nullable": nullable, "old_nullable": old_nullable, "has_default": has_default, "unique": unique, "principal_table": principal_table, "principal_columns": principal_columns, "suppress_transaction": suppress_transaction, "clr_type": clr_type, "old_clr_type": old_clr_type, "store_type": store_type, "old_store_type": old_store_type, "max_length": max_length, "old_max_length": old_max_length, "precision": precision, "old_precision": old_precision, "scale": scale, "old_scale": old_scale}
            oid = "op-" + sha256_text(canonical_json(payload))[:16]
            operations.append(Operation(oid,file_identity.path,file_identity.sha256,migration,migration_id,timestamp,scope_key,method,migration_order,ordinal,op,table,column,columns,name,new_name,object_type,nullable,old_nullable,has_default,unique,principal_table,principal_columns,suppress_transaction,clr_type,old_clr_type,store_type,old_store_type,max_length,old_max_length,precision,old_precision,scale,old_scale,raw))
            if op == "CreateTable" and table:
                for ci,(cn,cnul,cdef) in enumerate(extract_create_table_columns(args),1):
                    cp=dict(payload); cp.update({"op":"CreateTableColumn","column":cn,"columns":[cn],"ordinal":ordinal*1000+ci})
                    cid="op-"+sha256_text(canonical_json(cp))[:16]
                    operations.append(Operation(cid,file_identity.path,file_identity.sha256,migration,migration_id,timestamp,scope_key,method,migration_order,ordinal*1000+ci,"CreateTableColumn",table,cn,[cn],cn,None,"column",cnul,None,cdef,None,None,[],False,None,None,None,None,None,None,None,None,None,None,args[:1600]))
    return operations, metadata


def group_by_key(ops: Iterable[Operation], key_fn) -> Dict[Any, List[Operation]]:
    groups: Dict[Any,List[Operation]] = defaultdict(list)
    for op in ops:
        key=key_fn(op)
        if key is None: continue
        if isinstance(key,tuple) and any(part is None or part=="" or part==() for part in key): continue
        groups[key].append(op)
    return groups


class FindingBuilder:
    def __init__(self, heuristic_set: Dict[str,Any]): self.rules=heuristic_set["rules"]; self._items: Dict[str,Finding]={}
    def add(self, rule_id: str, ops: Sequence[Operation], evidence: str, why: str, recommendation: str, validation: str, uncertainty: str, evidence_status: str="observed", subject_tokens: Sequence[str]=()) -> None:
        rule=self.rules[rule_id]; op_ids=sorted({o.id for o in ops}); payload={"rule_id":rule_id,"operation_ids":op_ids,"subjects":sorted(set(subject_tokens))}; fid=f"mca:{rule_id}:{sha256_text(canonical_json(payload))[:16]}"; files=sorted({o.file for o in ops})
        self._items[fid]=Finding(fid,rule_id,rule["severity"],rule["confidence"],evidence_status,rule["gate"],rule["hazard_type"],rule["title"],files,op_ids,evidence,why,recommendation,validation,uncertainty)
    def values(self)->List[Finding]: return sorted(self._items.values(),key=lambda f:(-SEVERITY_ORDER.get(f.severity,0),f.rule_id,f.id))


def pseudo_operation(kind: str, token: str, file: str="context", sha: Optional[str]=None, scope_key: str="context") -> Operation:
    digest=sha or sha256_text(token)
    return Operation("meta-"+sha256_text(kind+token)[:16],file,digest,kind,None,None,scope_key,"meta",0,0,kind,name=token,object_type="meta")


def op_target(op: Operation)->str:
    if op.table and op.column: return f"{op.table}.{op.column}"
    if op.table and op.columns: return f"{op.table}({','.join(op.columns)})"
    return op.table or op.name or op.object_type or "unknown"


def evidence_for_ops(ops: Sequence[Operation])->str:
    return "; ".join(f"{o.file}:{o.migration}.{o.op}({op_target(o)})" for o in sorted(ops,key=lambda x:(x.migration_order,x.ordinal,x.file,x.id))[:8])


def operation_position(op: Operation)->Tuple[int,int,str]: return (op.migration_order,op.ordinal,op.id)


def provider_literal_matches(provider: str, literal: str)->bool:
    return normalize_provider(literal)==normalize_provider(provider)


def fingerprints(items: Sequence[FileIdentity])->List[str]: return sorted(i.sha256 for i in items)


def analyze(operations: List[Operation], metadata: List[Dict[str,Any]], heuristic_set: Dict[str,Any], base_history: List[Dict[str,Any]], head_history: List[Dict[str,Any]], model_snapshots: List[Tuple[FileIdentity,Optional[str]]], git_identity: Optional[Dict[str,Any]], runtime_sources: List[Tuple[FileIdentity,str]], context: Dict[str,Any], semantic: Dict[str,Any], provider_profile: Optional[Dict[str,Any]], generated_sql_sources: List[Tuple[FileIdentity,str]], reviewed_sql_ids: List[FileIdentity], deployment_sql_ids: List[FileIdentity]) -> Tuple[List[Finding],Dict[str,Any]]:
    b=FindingBuilder(heuristic_set); up=[o for o in operations if o.method=="Up"]; down=[o for o in operations if o.method=="Down"]; ordered_up=sorted(up,key=operation_position)
    major=parse_major(context.get("ef_core_version")); provider=normalize_provider(context.get("provider")); deployment_instances=context.get("deployment_instances","unknown")

    by_ts: Dict[Tuple[str,str],List[Dict[str,Any]]]=defaultdict(list); by_id: Dict[Tuple[str,str],List[Dict[str,Any]]]=defaultdict(list); by_class: Dict[Tuple[str,str],List[Dict[str,Any]]]=defaultdict(list)
    for m in metadata:
        if m.get("timestamp"): by_ts[(m["scope_key"],m["timestamp"])].append(m)
        if m.get("migration_id"): by_id[(m["scope_key"],m["migration_id"])].append(m)
        if m.get("class_name"): by_class[(m["scope_key"],m["class_name"])].append(m)
        if not m.get("has_up"):
            po=pseudo_operation("MissingUp",m["file_sha256"],m["file"],m["file_sha256"],m["scope_key"]); b.add("structure.missing-up",[po],canonical_json(m),"The standard EF Core migration entry point has no explicit Up body.","Regenerate or repair the migration so schema operations are explicit in Up().","Compile the project and generate migration SQL.","Custom infrastructure may route work elsewhere; static analysis cannot prove that intent.")
        if not m.get("has_down") and not m.get("down_explicitly_unsupported"):
            po=pseudo_operation("MissingDown",m["file_sha256"],m["file"],m["file_sha256"],m["scope_key"]); b.add("structure.missing-down",[po],canonical_json(m),"Rollback behavior is absent from the standard Down method.","Add a safe Down implementation or explicitly document irreversibility.","Review rollback expectations and generated rollback SQL if used.","A missing Down does not prove deployment failure; it limits rollback evidence.")
        if m.get("down_explicitly_unsupported"):
            po=pseudo_operation("UnsupportedDown",m["file_sha256"],m["file"],m["file_sha256"],m["scope_key"]); b.add("rollback.explicitly-unsupported",[po],canonical_json(m),"Down explicitly refuses rollback instead of pretending to reconstruct state.","Keep the irreversibility documented and provide a corrective-forward recovery path when required.","Generate/review deployment and recovery artifacts for the target environment.","Explicit refusal can be safer than a misleading rollback, but operational recovery still needs separate evidence.","observed",[m["file_sha256"]])
        if m.get("runtime_dependency_signals"):
            po=pseudo_operation("RuntimeDependentMigration",m["file_sha256"],m["file"],m["file_sha256"],m["scope_key"]); b.add("determinism.runtime-dependent-migration",[po],", ".join(m["runtime_dependency_signals"]),"Historical migration behavior depends on runtime/environment values that can change between executions.","Replace dynamic/environment-dependent values with frozen migration-time constants or an explicitly checkpointed external data-migration process.","Re-run the migration from clean and upgraded baselines and compare generated/executed effects.","Pattern matching cannot prove the value actually affects emitted migration operations; manual review remains required.","observed",m["runtime_dependency_signals"])
        if m.get("uses_active_provider") and context.get("provider"):
            if not any(provider_literal_matches(context["provider"],lit) for lit in m.get("active_provider_literals",[])):
                po=pseudo_operation("ProviderBranch",m["file_sha256"],m["file"],m["file_sha256"],m["scope_key"]); b.add("provider.branch-incomplete",[po],canonical_json({"provider":context["provider"],"branches":m.get("active_provider_literals",[])}),"The migration branches on ActiveProvider but the supplied provider is not represented by an observed branch literal.","Add an explicit branch for the supported provider or fail deliberately before executing incomplete provider-specific logic.","Generate provider-specific SQL for the supplied provider and execute it in a disposable target.","More complex provider checks may not use string literals and can evade static extraction.","inferred",[context["provider"],m["file_sha256"]])

    for (scope,ts),rows in sorted(by_ts.items()):
        if len(rows)>1:
            ops=[pseudo_operation("MigrationTimestamp",r["file_sha256"],r["file"],r["file_sha256"],scope) for r in rows]; b.add("history.duplicate-timestamp",ops,evidence_for_ops(ops),"Multiple migrations in the same resolved scope share a timestamp, which can signal parallel creation but is not a complete migration identity conflict.","Inspect lineage and full migration IDs; recreate a branch migration only when the migration tree actually diverged.","Compare full migration IDs, model snapshots/designer metadata, and the Git merge-base.","Different migration names can legitimately share a timestamp; timestamp reuse alone is not a blocker.","derived",[scope,ts])
    for (scope,mid),rows in sorted(by_id.items()):
        if len(rows)>1:
            ops=[pseudo_operation("MigrationId",r["file_sha256"],r["file"],r["file_sha256"],scope) for r in rows]; b.add("history.duplicate-full-id",ops,evidence_for_ops(ops),"The same full EF migration ID appears more than once in the same resolved scope.","Keep one canonical migration identity and regenerate/reconcile the conflicting branch migration.","Build the migrations assembly and list migrations for the target DbContext/provider.","The analyzer does not know whether separate physical files are intentionally isolated outside the supplied scope context.","derived",[scope,mid])
    for (scope,cls),rows in sorted(by_class.items()):
        if len(rows)>1:
            ops=[pseudo_operation("MigrationClass",r["file_sha256"],r["file"],r["file_sha256"],scope) for r in rows]; b.add("history.duplicate-class",ops,evidence_for_ops(ops),"The same migration class appears more than once in the same resolved scope.","Rename or regenerate one migration and rebuild the migrations assembly.","Run dotnet build and dotnet ef migrations list for the target context.","Compilation is not executed by the portable analyzer.","derived",[scope,cls])

    if base_history:
        base_ids=defaultdict(list); base_classes=defaultdict(list)
        for x in base_history:
            if x.get("migration_id"): base_ids[x["migration_id"]].append(x)
            if x.get("class_name"): base_classes[x["class_name"]].append(x)
        for m in metadata:
            collisions=[]
            collisions.extend(base_ids.get(m.get("migration_id"),[])); collisions.extend(base_classes.get(m.get("class_name"),[]))
            dedup={(x["path"],x["sha256"]):x for x in collisions}
            if dedup and any(x["sha256"]!=m["file_sha256"] for x in dedup.values()):
                po=pseudo_operation("BaseHistoryCollision",m["file_sha256"],m["file"],m["file_sha256"],m["scope_key"]); desc=", ".join(f"{x['path']}@{x['sha256'][:12]}" for x in sorted(dedup.values(),key=lambda y:y["path"])); b.add("history.base-collision",[po],f"changed={m['file']} base={desc}","A changed migration reuses a full migration/class identity already present in the resolved Git base with different bytes.","Rebase/reconcile history and regenerate the newer migration; do not silently rewrite a migration that may already be applied.","Compare migrations list and generated SQL from recorded base/head SHAs.","Whether the base migration was applied to a shared database is deployment evidence outside this static analysis.","derived",[m["file_sha256"],*[x["sha256"] for x in dedup.values()]])

    if major is not None and major>=11:
        current_history=head_history if head_history else [{"path":m["file"],"directory":Path(m["file"]).parent.as_posix(),"migration_id":m.get("migration_id")} for m in metadata]
        by_dir: Dict[str,List[str]]=defaultdict(list)
        for x in current_history:
            if x.get("migration_id"): by_dir[x.get("directory") or Path(x["path"]).parent.as_posix()].append(x["migration_id"])
        for identity,last_id in model_snapshots:
            if not last_id: continue
            directory=Path(identity.path).parent.as_posix(); ids=sorted(set(by_dir.get(directory,[])))
            if ids and (last_id not in ids or last_id!=ids[-1]):
                po=pseudo_operation("SnapshotLineage",identity.sha256,identity.path,identity.sha256,directory); b.add("history.diverged-lineage",[po],canonical_json({"snapshot_last_migration_id":last_id,"latest_observed_migration_id":ids[-1],"directory":directory}),"EF11 snapshot lineage does not point to the latest migration observed in the same migration set.","Recreate the divergent branch migration on top of the reconciled migration tree and regenerate the snapshot.","Build with EF11 tooling and inspect the snapshot LastMigrationId plus migrations list.","Directory grouping approximates migration-set scope when DbContext/assembly metadata is unavailable; unusual layouts may require semantic evidence.","derived",[identity.sha256,last_id,ids[-1]])

    created_tables={(o.scope_key,o.table,o.file) for o in up if o.op=="CreateTable" and o.table}
    for key,ops in sorted(group_by_key((o for o in up if o.op=="AddColumn"),lambda o:(o.scope_key,o.table,o.column)).items(),key=lambda x:str(x[0])):
        if len({o.file for o in ops})>1: b.add("duplicate.add-column",ops,evidence_for_ops(ops),"More than one changed migration adds the same scoped table/column.","Keep one AddColumn and regenerate the later branch migration after reconciliation.","Generate SQL and apply it to clean and upgraded test databases.","Out-of-band schema state can change runtime behavior, but the duplicate source operations are directly observed.","derived",list(map(str,key)))
    for key,ops in sorted(group_by_key((o for o in up if o.op=="CreateTable"),lambda o:(o.scope_key,o.table)).items(),key=lambda x:str(x[0])):
        if len({o.file for o in ops})>1: b.add("duplicate.create-table",ops,evidence_for_ops(ops),"More than one changed migration creates the same scoped table.","Keep one table creation and regenerate dependent migrations.","Generate SQL from an empty baseline.","Provider-specific conditional DDL is not assumed.","derived",list(map(str,key)))
    named=[o for o in up if o.op in ("CreateIndex","AddForeignKey","AddPrimaryKey","AddUniqueConstraint","AddCheckConstraint","CreateSequence") and o.name]
    for key,ops in sorted(group_by_key(named,lambda o:(o.scope_key,o.op,o.name)).items(),key=lambda x:str(x[0])):
        if len({o.file for o in ops})>1: b.add("duplicate.object-name",ops,evidence_for_ops(ops),"The same named database object is created by multiple changed migrations in one scope.","Consolidate operations or use distinct provider-valid identities.","Inspect provider-generated SQL/catalog state.","Database object-name scope varies by provider.","derived",list(map(str,key)))
    for key,ops in sorted(group_by_key((o for o in up if o.op=="CreateIndex" and o.columns),lambda o:(o.scope_key,o.table,tuple(o.columns))).items(),key=lambda x:str(x[0])):
        if len(ops)>1 and len({(o.name,o.unique) for o in ops})>1: b.add("conflict.index-definition",ops,evidence_for_ops(ops),"The same indexed column set has different index identity or uniqueness semantics.","Choose the intended definition or sequence replacement explicitly.","Generate provider SQL and inspect the final index catalog.","Multiple indexes over the same columns can be intentional.","inferred",[str(key)])
    for key,ops in sorted(group_by_key((o for o in up if o.op=="AddForeignKey" and o.columns),lambda o:(o.scope_key,o.table,tuple(o.columns))).items(),key=lambda x:str(x[0])):
        if len(ops)>1 and len({(o.principal_table,tuple(o.principal_columns)) for o in ops})>1: b.add("conflict.foreign-key-definition",ops,evidence_for_ops(ops),"The same local FK columns point to different principal targets.","Resolve the intended relationship and regenerate from the reconciled model.","Generate SQL and inspect the target provider FK catalog.","A relationship transition can be intentional.","inferred",[str(key)])

    for o in [x for x in up if x.op in ("DropColumn","DropTable")]:
        rule="destructive.drop-column" if o.op=="DropColumn" else "destructive.drop-table"; b.add(rule,[o],evidence_for_ops([o]),"The migration explicitly removes a schema object.","Verify consumer retirement/data retention and stage the contract step when app versions can overlap.","Inspect provider SQL and test upgraded data before the destructive step.","The analyzer does not know whether required data or active consumers exist.","observed",[op_target(o)])
        inverse="AddColumn" if o.op=="DropColumn" else "CreateTable"; matches=[d for d in down if d.op==inverse and d.table==o.table and (o.op=="DropTable" or d.column==o.column) and d.scope_key==o.scope_key]
        if matches:
            b.add("rollback.data-not-restorable",[o,*matches],evidence_for_ops([o,*matches]),"Down structurally recreates an object removed by Up, but the original dropped data is not reconstructed by that inverse operation.","Treat rollback as data-loss-sensitive; preserve data separately or prefer a corrective forward migration when original values cannot be reconstructed.","Generate the rollback SQL and test it against a representative upgraded database with data assertions.","Additional custom SQL/backups outside the parsed pair could restore data; this rule does not inspect external recovery systems.","derived",[o.id,*[x.id for x in matches]])

    drops=[o for o in up if o.op=="DropColumn" and o.table]; adds=[o for o in up if o.op=="AddColumn" and o.table]
    for table in sorted({o.table for o in drops}&{o.table for o in adds}):
        ds=[o for o in drops if o.table==table]; aa=[o for o in adds if o.table==table]
        b.add("rename.drop-add",ds+aa,evidence_for_ops(ds+aa),"The changed set drops and adds columns on the same table, which can represent a scaffolded rename that loses data.","If identity is preserved, use RenameColumn; otherwise use explicit copy/backfill/contract sequencing.","Inspect generated SQL and representative data preservation.","Drop/add can be an intentional replacement rather than a rename.","inferred",[str(table)])

    dropped=set(); renamed: Dict[Tuple[str,str,str],str]={}
    for o in ordered_up:
        if o.op=="DropColumn" and o.table and o.column: dropped.add((o.scope_key,o.table,o.column))
        elif o.op=="DropTable" and o.table: dropped.add((o.scope_key,o.table,"*"))
        elif o.op=="RenameColumn" and o.table and o.column and o.new_name: renamed[(o.scope_key,o.table,o.column)]=o.new_name
        elif o.table:
            refs=set((o.scope_key,o.table,c) for c in ([o.column] if o.column else o.columns))
            if (o.scope_key,o.table,"*") in dropped or any(r in dropped for r in refs): b.add("ordering.after-drop",[o],evidence_for_ops([o]),"A later structured operation references an object already dropped earlier in the ordered migration sequence.","Reorder or retarget operations so dependencies exist when referenced.","Generate ordered SQL and execute the upgrade path.","Custom SQL can recreate objects but is not assumed.","derived",[o.id])
            if any(k in refs for k in renamed): b.add("ordering.rename",[o],evidence_for_ops([o]),"A later operation still references the old column identity after RenameColumn.","Retarget dependent operations to the new name or place them before the rename.","Generate SQL and execute the migration sequence.","Complex provider name resolution can alter actual behavior.","inferred",[o.id])

    for o in [x for x in up if x.op=="AddColumn" and x.nullable is False and not x.has_default and (x.scope_key,x.table,x.file) not in created_tables]:
        b.add("column.required-without-backfill",[o],evidence_for_ops([o]),"A required column is added without default/computed/backfill evidence.","Add nullable first or provide a deliberate backfill/default before enforcing NOT NULL.","Apply generated SQL to an upgraded database with existing rows.","Out-of-band backfill or empty-table state can change the outcome.","observed",[op_target(o)])
    for o in [x for x in up if x.op=="AlterColumn"]:
        if o.old_nullable is True and o.nullable is False: b.add("column.nullability-tightening",[o],evidence_for_ops([o]),"AlterColumn changes a nullable column to non-nullable.","Backfill/validate null rows before enforcing NOT NULL.","Run a null-detection query and apply generated SQL to representative upgraded data.","No database rows were inspected.","observed",[op_target(o)])
        if o.old_max_length is not None and o.max_length is not None and o.max_length<o.old_max_length: b.add("column.length-narrowing",[o],evidence_for_ops([o]),"AlterColumn reduces the declared maximum length.","Validate existing values fit the narrower limit and define truncation/rejection behavior explicitly.","Query max data length and apply generated SQL on representative data.","Provider coercion/truncation behavior is not inferred.","observed",[op_target(o)])
        if ((o.old_precision is not None and o.precision is not None and o.precision<o.old_precision) or (o.old_scale is not None and o.scale is not None and o.scale<o.old_scale)):
            b.add("column.precision-narrowing",[o],evidence_for_ops([o]),"AlterColumn narrows numeric precision or scale.","Validate range/rounding impact before deployment.","Query min/max/scale distribution and test provider conversion behavior.","No production values were inspected.","observed",[op_target(o)])
        if o.old_store_type and o.store_type and o.old_store_type.lower()!=o.store_type.lower(): b.add("column.type-change",[o],evidence_for_ops([o]),"AlterColumn changes the provider store type.","Review conversion, index/constraint compatibility, and provider-generated SQL.","Apply generated SQL against representative upgraded data.","Type compatibility is provider/data dependent.","observed",[op_target(o),o.old_store_type,o.store_type])

    for o in [x for x in up if x.op in DATA_OPS]:
        b.add("data.structured-mutation",[o],evidence_for_ops([o]),"The migration mutates data through EF structured data operations.","Review key targeting, rerun/rollback behavior, and whether fixed-value data belongs in the migration.","Inspect provider-generated SQL and execute clean/upgrade/rollback paths as applicable.","Static source parsing does not inspect actual rows or prove rerun safety.","observed",[o.op,op_target(o)])
    for o in [x for x in up if x.op in CONSTRAINT_OPS]:
        b.add("constraint.existing-data-validation",[o],evidence_for_ops([o]),"A new constraint can reject pre-existing rows that violate the new condition.","Validate existing data before enforcing the constraint, or stage validation/provider-specific rollout when appropriate.","Run targeted data-quality queries and execute generated SQL on representative upgraded data.","The analyzer does not inspect existing rows.","inferred",[o.op,op_target(o)])
    for o in [x for x in up if x.op=="CreateIndex" and x.unique]:
        b.add("index.unique-data-check",[o],evidence_for_ops([o]),"A unique index is created over an existing table.","Check/repair duplicates before rollout.","Run duplicate-detection queries on representative data.","No database rows were inspected.","inferred",[op_target(o),o.name or ""])

    for o in [x for x in up if x.op=="Sql"]:
        raw=o.raw or ""; mutating=bool(MUTATING_SQL_RE.search(raw)); nonid=bool(NON_IDEMPOTENT_UPDATE_RE.search(raw)) or (bool(re.search(r"\binsert\s+into\b",raw,re.I)) and not bool(re.search(r"\b(on\s+conflict|where\s+not\s+exists|merge)\b",raw,re.I)))
        if nonid: b.add("raw-sql.non-idempotent-data",[o],evidence_for_ops([o]),"Raw SQL contains a rerun-sensitive data mutation pattern.","Make rerun behavior explicit and safe or use a checkpointed operational job.","Execute exact SQL twice in a disposable representative database and compare state.","The detector recognizes a narrow pattern set.","inferred",[sha256_text(raw)])
        if mutating: b.add("raw-sql.opaque-mutation",[o],evidence_for_ops([o]),"Raw SQL mutates schema/data outside EF structured operation semantics.","Review provider SQL, dependencies, transaction and rerun behavior explicitly.","Inspect final generated SQL and test clean/upgrade paths.","Regex inspection cannot prove SQL correctness or lock behavior.","observed",[sha256_text(raw)])
        else: b.add("raw-sql.manual-review",[o],evidence_for_ops([o]),"The analyzer cannot semantically interpret this raw SQL.","Document intent and validate it on the target provider.","Inspect/execute generated SQL in a representative environment.","No safety conclusion is derived from unrecognized SQL.","blocked",[sha256_text(raw)])
        if o.suppress_transaction: b.add("raw-sql.suppress-transaction",[o],evidence_for_ops([o]),"The source explicitly requests suppressTransaction: true.","Document the required transaction boundary plus interruption/retry recovery semantics.","Test interruption and rerun behavior on the target provider.","Provider transaction support differs; the source flag itself is directly observed.","observed",[sha256_text(raw)])
    if int(semantic.get("transaction_suppressed_command_count") or 0)>0:
        po=pseudo_operation("TransactionSuppressed",str(semantic.get("transaction_suppressed_command_count"))); b.add("transaction.suppressed-command",[po],canonical_json(semantic),"Supplied semantic evidence reports one or more transaction-suppressed migration commands.","Isolate operations requiring suppression and define interruption/retry/recovery behavior.","Execute exact provider commands with failure injection and verify post-failure state.","The analyzer trusts the supplied semantic-evidence artifact identity but does not independently regenerate commands.","supplied",[str(semantic.get("transaction_suppressed_command_count"))])
    if semantic.get("pending_model_changes") is True:
        po=pseudo_operation("PendingModelChanges","true"); b.add("semantic.pending-model-changes",[po],canonical_json(semantic),"Supplied semantic evidence reports pending model changes relative to the latest migration snapshot.","Generate/review the missing migration or fix nondeterministic/provider-mismatched model construction before deployment.","Run dotnet ef migrations has-pending-model-changes with the same context/provider and re-run the semantic probe.","The analyzer does not execute EF tooling; it relies on the supplied semantic evidence identity.","supplied",["pending-model-changes"])

    for o in [x for x in up if x.op not in KNOWN_OPS and x.op!="CreateTableColumn"]:
        b.add("unknown.operation",[o],evidence_for_ops([o]),"The migrationBuilder invocation is outside the frozen operation vocabulary.","Review the custom/provider operation and add a versioned parser/evaluator only when semantics are known.","Inspect generated SQL and provider documentation.","Semantics are intentionally blocked rather than guessed.","blocked",[o.op,op_target(o)])

    if git_identity is not None:
        changed=git_identity.get("changed_files",[]); migration_changed=any(is_main_migration_name(Path(x["path"]).name) and not str(x["status"]).startswith("D") for x in changed); snapshot_changed=any(Path(x["path"]).name.endswith("ModelSnapshot.cs") for x in changed)
        if snapshot_changed and not migration_changed and model_snapshots:
            ops=[pseudo_operation("ModelSnapshot",i.sha256,i.path,i.sha256,Path(i.path).parent.as_posix()) for i,_ in model_snapshots]; b.add("snapshot.divergence",ops,"; ".join(f"{i.path}@{i.sha256[:12]}" for i,_ in model_snapshots),"The snapshot changed without a corresponding changed migration in the Git diff.","Confirm whether a migration is missing or the snapshot-only change is intentional.","Run pending-model-changes and compare recorded base/head snapshots.","Snapshot-only change is a signal, not proof of migration failure.","inferred",[i.sha256 for i,_ in model_snapshots])
        elif migration_changed and not snapshot_changed:
            ops=[pseudo_operation("MissingSnapshot",m["file_sha256"],m["file"],m["file_sha256"],m["scope_key"]) for m in metadata]; b.add("snapshot.divergence",ops,evidence_for_ops(ops),"Changed migrations were detected without a changed ModelSnapshot.","Confirm the snapshot was generated from the same model state or document why no snapshot change is expected.","Run pending-model-changes and inspect base/head snapshot identities.","Some migrations legitimately leave snapshot state unchanged.","inferred",[m["file_sha256"] for m in metadata])
    elif model_snapshots and not metadata:
        ops=[pseudo_operation("ModelSnapshot",i.sha256,i.path,i.sha256,Path(i.path).parent.as_posix()) for i,_ in model_snapshots]; b.add("snapshot.divergence",ops,"; ".join(f"{i.path}@{i.sha256[:12]}" for i,_ in model_snapshots),"A snapshot was supplied without a migration input.","Confirm whether a migration is missing or the snapshot-only input is intentional.","Run pending-model-changes where supported.","A snapshot-only input is a signal, not proof of failure.","inferred",[i.sha256 for i,_ in model_snapshots])

    runtime_hits=[(i,t) for i,t in runtime_sources if STARTUP_MIGRATE_RE.search(t)]
    if runtime_hits:
        ops=[pseudo_operation("Database.Migrate",i.sha256,i.path,i.sha256,"runtime") for i,_ in runtime_hits]
        b.add("runtime.startup-migrate",ops,"; ".join(f"{i.path}@{i.sha256[:12]}" for i,_ in runtime_hits),"Application runtime code applies EF migrations during startup.","Prefer a controlled deployment migration step for production unless startup application is deliberately supported and evidenced.","Validate deployment sequencing, permissions, lock behavior, and app/schema overlap on the target platform.","Startup migration is not itself proof of concurrent failure.","observed",[i.sha256 for i,_ in runtime_hits])
        if deployment_instances=="multiple":
            if major is None: rule="runtime.concurrent-startup-version-unknown"; why="Multiple startup migrators are possible but the EF Core version is unknown, so migration-lock guarantees cannot be classified precisely."
            elif major<9: rule="runtime.concurrent-startup-unprotected"; why="Multiple startup migrators are possible on an EF Core major version before EF9 migration locking."
            else: rule="runtime.concurrent-startup-lock-aware"; why="Multiple startup migrators are possible on EF9+ where migration locking exists, but provider-specific locking and application/schema overlap still require review."
            b.add(rule,ops,"; ".join(f"{i.path}@{i.sha256[:12]}" for i,_ in runtime_hits),why,"Prefer one controlled migration executor and verify provider locking/rollout compatibility if startup migration is retained.","Exercise concurrent startup against a disposable target with the exact EF/provider version and deployment orchestrator.","Migration locks coordinate migration executors, not all old/new application compatibility or provider failure modes.","supplied",[deployment_instances,str(context.get("ef_core_version")),*(i.sha256 for i,_ in runtime_hits)])
        if major is not None and major>=9 and any(BEGIN_TRANSACTION_RE.search(t) for _,t in runtime_hits):
            b.add("runtime.explicit-migrate-transaction",ops,"; ".join(f"{i.path}@{i.sha256[:12]}" for i,_ in runtime_hits),"EF9+ startup migration code is combined with an explicit transaction pattern in the supplied runtime source.","Remove the external transaction around Migrate/MigrateAsync and let EF/provider migration transaction/lock behavior apply.","Execute the exact runtime path on the target EF/provider version.","Static co-location of transaction and Migrate calls does not prove the same control-flow path; review source flow.","inferred",[str(context.get("ef_core_version")),*(i.sha256 for i,_ in runtime_hits)])

    if provider_profile:
        if provider=="sqlite":
            rebuild=set(provider_profile.get("rebuild_operations",[]))
            for o in [x for x in up if x.op in rebuild]:
                b.add("provider.sqlite-rebuild-required",[o],evidence_for_ops([o]),"SQLite provider support for this operation is implemented through table rebuild semantics.","Review rebuild compatibility with manually-created artifacts/triggers and test the exact provider-generated SQL.","Apply the migration to a representative SQLite copy and verify schema/data/artifacts.","The rule identifies documented provider behavior; custom/manual database artifacts can change success/failure.","derived",[o.op,op_target(o)])
            if context.get("deployment_method")=="idempotent-script":
                po=pseudo_operation("SQLiteIdempotent","unsupported"); b.add("provider.sqlite-idempotent-script-unsupported",[po],"provider=sqlite deployment_method=idempotent-script","SQLite does not support EF idempotent migration script generation.","Use a versioned from/to script or another supported migration application method.","Generate the chosen artifact with SQLite provider tooling before deployment.","This is a provider capability constraint, not a statement about arbitrary hand-written idempotent SQL.","derived",["sqlite","idempotent-script"])

    for identity,text in generated_sql_sources:
        low=text.lower()
        lock_potential=False; detail=""
        if provider=="postgresql" and re.search(r"\bcreate\s+(?:unique\s+)?index\b",low) and "concurrently" not in low:
            lock_potential=True; detail="PostgreSQL CREATE INDEX without CONCURRENTLY"
        elif provider=="sqlserver" and re.search(r"\bcreate\s+(?:unique\s+)?(?:clustered\s+|nonclustered\s+)?index\b",low) and not re.search(r"online\s*=\s*on",low):
            lock_potential=True; detail="SQL Server CREATE INDEX without observed ONLINE = ON"
        if lock_potential:
            po=pseudo_operation("GeneratedSqlLockPotential",identity.sha256,identity.path,identity.sha256,"generated-sql"); b.add("operational.ddl-locking-potential",[po],detail,"Generated provider SQL contains DDL with documented potential to block concurrent access depending on provider/options/workload.","Review provider online/concurrent options and schedule/sequence the DDL based on table size and workload evidence.","Execute on representative data with lock/wait monitoring.","Static SQL text does not establish lock duration, outage, table size, or production workload impact.","inferred",[provider or "unknown",identity.sha256])

    if reviewed_sql_ids and deployment_sql_ids and fingerprints(reviewed_sql_ids)!=fingerprints(deployment_sql_ids):
        ops=[pseudo_operation("ReviewedSql",i.sha256,i.path,i.sha256,"artifact") for i in reviewed_sql_ids]+[pseudo_operation("DeploymentSql",i.sha256,i.path,i.sha256,"artifact") for i in deployment_sql_ids]
        b.add("artifact.review-execution-drift",ops,canonical_json({"reviewed":fingerprints(reviewed_sql_ids),"deployment":fingerprints(deployment_sql_ids)}),"The SQL artifact identified for deployment does not match the SQL artifact identified as reviewed/approved.","Deploy the exact reviewed bytes or restart review for the changed deployment artifact.","Recompute artifact hashes in the deployment stage and require exact match before execution.","File identity proves byte drift, not whether the changed SQL is semantically safer or worse.","derived",[*fingerprints(reviewed_sql_ids),*fingerprints(deployment_sql_ids)])

    table_ops: Dict[Tuple[str,str],List[Operation]]=defaultdict(list)
    for o in up:
        if o.table and o.op!="CreateTableColumn": table_ops[(o.scope_key,o.table)].append(o)
    for (scope,table),ops in sorted(table_ops.items()):
        if len({o.file for o in ops})>1 and not any(o.op in ("DropTable","RenameTable") for o in ops): b.add("hotspot.same-table",ops[:12],evidence_for_ops(ops[:12]),"Multiple changed migrations touch the same scoped table.","Review ordered integration and consolidate only when changes are inseparable.","Generate/inspect one ordered upgrade script.","Sharing a table is not itself a conflict.","inferred",[scope,table])

    adds_by=defaultdict(list); drops_by=defaultdict(list)
    for o in ordered_up:
        if o.op=="AddColumn" and o.table: adds_by[(o.scope_key,o.table)].append(o)
        if o.op=="DropColumn" and o.table: drops_by[(o.scope_key,o.table)].append(o)
    patterns={"expand_contract_candidates":[]}
    backfill_ops=[o for o in ordered_up if o.op=="Sql" or o.op in DATA_OPS]
    for key in sorted(set(adds_by)&set(drops_by)):
        adds2=adds_by[key]; drops2=drops_by[key]; backs=[o for o in backfill_ops if any(operation_position(a)<operation_position(o)<operation_position(d) for a in adds2 for d in drops2)]
        if backs: patterns["expand_contract_candidates"].append({"scope_key":key[0],"table":key[1],"add_operation_ids":[o.id for o in adds2],"backfill_operation_ids":[o.id for o in backs],"drop_operation_ids":[o.id for o in drops2],"confidence":"low","evidence_status":"inferred","uncertainty":"Sequence resembles expand/backfill/contract, but semantic mapping and old/new application compatibility are not proven by static parsing."})
    return b.values(),patterns


def load_semantic_evidence(paths: Sequence[str], repo_root: Optional[Path], notes: List[str]) -> Tuple[List[FileIdentity],Dict[str,Any],List[Path]]:
    ids=[]; merged: Dict[str,Any]={}; actual=[]
    for raw in paths:
        p=Path(raw)
        if not p.exists(): notes.append(f"semantic evidence not found: {raw}"); continue
        actual.append(p); identity=make_file_identity(p,"semantic_evidence",repo_root); ids.append(identity)
        try: data=json.loads(read_text(p))
        except Exception as exc: notes.append(f"invalid semantic evidence {raw}: {exc}"); continue
        if data.get("schema_version")!="1.0": notes.append(f"unsupported semantic evidence schema in {raw}: {data.get('schema_version')!r}"); continue
        for key in ("ef_core_version","provider","dbcontext","migrations_assembly","pending_model_changes","migration_lock_protected","transaction_suppressed_command_count"):
            if key in data:
                if key in merged and merged[key]!=data[key]: notes.append(f"semantic evidence conflict for {key}: {merged[key]!r} vs {data[key]!r}")
                merged[key]=data[key]
    return ids,merged,actual


def make_input_identity(file_ids: Sequence[FileIdentity], generated: Sequence[FileIdentity], reviewed: Sequence[FileIdentity], deployment: Sequence[FileIdentity], rollback: Sequence[FileIdentity], runtime: Sequence[FileIdentity], semantic: Sequence[FileIdentity], git_identity: Optional[Dict[str,Any]], provider_profile_sha: Optional[str]) -> Dict[str,Any]:
    def arr(items): return [asdict(x) for x in sorted(items,key=lambda y:(y.role,y.path,y.sha256))]
    payload={"files":arr(file_ids),"generated_sql":arr(generated),"reviewed_sql":arr(reviewed),"deployment_sql":arr(deployment),"rollback_sql":arr(rollback),"runtime_code":arr(runtime),"semantic_evidence":arr(semantic),"provider_profile_sha256":provider_profile_sha,"git":None if git_identity is None else {"base_requested":git_identity.get("base_requested"),"base_sha":git_identity.get("base_sha"),"head_sha":git_identity.get("head_sha"),"merge_base_sha":git_identity.get("merge_base_sha"),"changed_files":git_identity.get("changed_files",[]),"base_history_digest":git_identity.get("base_history_digest"),"head_history_digest":git_identity.get("head_history_digest")}}
    return {"digest":sha256_text(canonical_json(payload)),**payload}


def build_gates(findings: Sequence[Finding])->List[Dict[str,Any]]:
    groups=defaultdict(list)
    for f in findings:
        if f.gate!="none": groups[f.gate].append(f.id)
    return [{"gate":g,"status":"triggered","finding_ids":sorted(groups[g])} for g in ("block","review-required","manual-review") if groups.get(g)]


def build_summary(findings: Sequence[Finding])->Dict[str,Any]:
    counts={s:sum(1 for f in findings if f.severity==s) for s in SEVERITY_ORDER}
    decision="block" if any(f.gate=="block" for f in findings) else "changes-required" if counts["high"] else "review-required" if counts["medium"] else "no-static-blocker"
    return {"total_findings":len(findings),"by_severity":counts,"decision":decision,"decision_basis":"Derived from the frozen v3 heuristic/provider-profile contracts over supplied evidence; no static decision is a runtime migration safety guarantee."}


def build_report(files: List[Path], support_files: List[Path], notes: List[str], operations: List[Operation], metadata: List[Dict[str,Any]], findings: List[Finding], patterns: Dict[str,Any], heuristic_set: Dict[str,Any], heuristic_hash: str, provider_profiles: Dict[str,Any], provider_profiles_hash: str, selected_provider_profile: Optional[Dict[str,Any]], input_identity: Dict[str,Any], git_identity: Optional[Dict[str,Any]], context: Dict[str,Any], semantic: Dict[str,Any], repo_root: Optional[Path]) -> Dict[str,Any]:
    analysis_payload={"analysis_version":ANALYSIS_VERSION,"heuristic_set_sha256":heuristic_hash,"provider_profiles_sha256":provider_profiles_hash,"input_digest":input_identity["digest"],"context":context,"semantic_digest":sha256_text(canonical_json(semantic)) if semantic else None}
    analysis_id="analysis-"+sha256_text(canonical_json(analysis_payload))[:24]; summary=build_summary(findings)
    report={"schema_version":REPORT_SCHEMA_VERSION,"analysis_version":ANALYSIS_VERSION,"analysis_id":analysis_id,"heuristic_set":{"name":heuristic_set["set_name"],"version":heuristic_set["version"],"sha256":heuristic_hash,"path":"references/heuristic-set.json"},"provider_profiles":{"version":provider_profiles["profile_version"],"sha256":provider_profiles_hash,"selected":selected_provider_profile or {}},"input_identity":input_identity,"git_identity":git_identity or {},"context":context,"semantic_evidence":semantic,"scope":{"migration_files_analyzed":[logical_path(p,repo_root) for p in files],"support_files_observed":[logical_path(p,repo_root) for p in support_files],"notes":notes},"metadata":metadata,"operations":[asdict(o) for o in sorted(operations,key=lambda x:(x.migration_order,x.method!="Up",x.ordinal,x.id))],"patterns":patterns,"findings":[asdict(f) for f in findings],"gates":build_gates(findings),"summary":summary,"limitations":["Portable static parsing does not compile C#, execute custom migration helpers, or instantiate EF provider services.","Provider/version profiles and optional semantic evidence improve classification but do not replace execution against the exact provider/database/data/deployment topology.","Operational DDL findings describe potential blocking/compatibility hazards; table size, data distribution, workload, lock duration, and outage are not inferred.","Rollback structural inverses do not prove data recovery; dropped/transformed values may be unrecoverable without external evidence.","SQL artifacts are hashed and text-inspected when supplied but are not executed by this analyzer.","no-static-blocker means only that the frozen static/optional-evidence rules found no critical/high/medium issue in the supplied scope; it is not a production-safety guarantee."]}
    core_hash=sha256_text(canonical_json(report)); report["analysis_receipt"]={"receipt_version":2,"status":"complete","stage":"analysis","analysis_id":analysis_id,"analysis_core_sha256":core_hash,"input_digest":input_identity["digest"],"heuristic_set_sha256":heuristic_hash,"provider_profiles_sha256":provider_profiles_hash,"finding_ids":[f.id for f in findings],"counts":summary["by_severity"]}
    return report


def render_markdown(report: Dict[str,Any])->str:
    lines=["# EF Core Migration Conflict Report","","## Identity",f"- analysis id: `{report['analysis_id']}`",f"- analyzer version: `{report['analysis_version']}`",f"- heuristic set: `{report['heuristic_set']['version']}` @ `{report['heuristic_set']['sha256']}`",f"- provider profiles: `{report['provider_profiles']['version']}` @ `{report['provider_profiles']['sha256']}`",f"- input digest: `{report['input_identity']['digest']}`"]
    ctx=report.get("context",{}); lines += [f"- EF Core version: `{ctx.get('ef_core_version')}`",f"- provider: `{ctx.get('provider')}`",f"- DbContext: `{ctx.get('dbcontext')}`",f"- migrations assembly: `{ctx.get('migrations_assembly')}`",f"- deployment: `{ctx.get('deployment_instances')}` / `{ctx.get('deployment_method')}`"]
    git=report.get("git_identity") or {}
    if git: lines += [f"- git base: `{git.get('base_requested')}` -> `{git.get('base_sha')}`",f"- head SHA: `{git.get('head_sha')}`",f"- merge-base SHA: `{git.get('merge_base_sha')}`"]
    lines += ["","## Executive summary",f"- total findings: {report['summary']['total_findings']}"]
    for s in ("critical","high","medium","low","info"):
        if report['summary']['by_severity'].get(s): lines.append(f"- {s}: {report['summary']['by_severity'][s]}")
    lines += [f"- static decision: `{report['summary']['decision']}`",f"- basis: {report['summary']['decision_basis']}"]
    if report['findings']:
        lines += ["","## Findings"]
        for f in report['findings']:
            lines += ["",f"### {f['severity'].upper()}: {f['title']}",f"- Finding ID: `{f['id']}`",f"- Rule: `{f['rule_id']}`",f"- Confidence / evidence: `{f['confidence']}` / `{f['evidence_status']}`",f"- Gate: `{f['gate']}`",f"- Evidence: {f['evidence']}",f"- Why it matters: {f['why']}",f"- Smallest safe fix: {f['recommendation']}",f"- Validation: {f['validation']}",f"- Uncertainty: {f['uncertainty']}"]
    else: lines += ["","No conflicts or review hazards were emitted by the frozen v3 contracts."]
    if report.get('patterns',{}).get('expand_contract_candidates'):
        lines += ["","## Expand/contract signals"]
        for p in report['patterns']['expand_contract_candidates']: lines.append(f"- `{p['scope_key']}::{p['table']}`: candidate sequence; confidence `{p['confidence']}`. {p['uncertainty']}")
    lines += ["","## Validation limits"]+[f"- {x}" for x in report['limitations']]
    return "\n".join(lines)+"\n"


def fsync_write(path: Path,data: bytes)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("wb") as h: h.write(data); h.flush(); os.fsync(h.fileno())


def resolved_collision(paths: Sequence[Path])->Optional[Tuple[Path,Path]]:
    resolved=[(p,p.resolve(strict=False)) for p in paths]
    for idx,(a,ra) in enumerate(resolved):
        for b,rb in resolved[idx+1:]:
            if ra==rb: return a,b
            if a.exists() and b.exists():
                try:
                    if os.path.samefile(a,b): return a,b
                except OSError: pass
    return None


def deliver(rendered: str, output: Optional[str], receipt_path: Optional[str], report: Dict[str,Any], protected_inputs: Sequence[Path], output_format: str)->None:
    artifact_bytes=rendered.encode("utf-8"); artifact_hash=sha256_bytes(artifact_bytes)
    if not output:
        sys.stdout.write(rendered); sys.stdout.flush()
        if receipt_path:
            receipt={"receipt_version":2,"status":"pass","stage":"analysis-delivery","analysis_id":report["analysis_id"],"input_digest":report["input_identity"]["digest"],"heuristic_set_sha256":report["heuristic_set"]["sha256"],"provider_profiles_sha256":report["provider_profiles"]["sha256"],"artifact":{"destination":"stdout","format":output_format,"sha256":artifact_hash},"recovery":[]}
            target=Path(receipt_path); collision=resolved_collision([target,*protected_inputs])
            if collision: raise ValueError(f"receipt output aliases protected input: {collision[0]} == {collision[1]}")
            tmp=target.with_name(f".{target.name}.tmp-{os.getpid()}"); fsync_write(tmp,(json.dumps(receipt,indent=2,sort_keys=True)+"\n").encode()); os.replace(tmp,target)
        return
    out=Path(output); receipt_target=Path(receipt_path) if receipt_path else None; collision_paths=[out,*protected_inputs]+([receipt_target] if receipt_target else []); collision=resolved_collision(collision_paths)
    if collision: raise ValueError(f"output alias collision: {collision[0]} == {collision[1]}")
    staged_out=out.with_name(f".{out.name}.tmp-{os.getpid()}"); fsync_write(staged_out,artifact_bytes); staged_receipt=None
    if receipt_target:
        receipt={"receipt_version":2,"status":"pass","stage":"analysis-delivery","analysis_id":report["analysis_id"],"input_digest":report["input_identity"]["digest"],"heuristic_set_sha256":report["heuristic_set"]["sha256"],"provider_profiles_sha256":report["provider_profiles"]["sha256"],"artifact":{"destination":out.resolve(strict=False).as_posix(),"format":output_format,"sha256":artifact_hash},"recovery":[]}; staged_receipt=receipt_target.with_name(f".{receipt_target.name}.tmp-{os.getpid()}"); fsync_write(staged_receipt,(json.dumps(receipt,indent=2,sort_keys=True)+"\n").encode())
    backup_out=out.with_name(f".{out.name}.last-good-{os.getpid()}") if out.exists() else None; backup_receipt=receipt_target.with_name(f".{receipt_target.name}.last-good-{os.getpid()}") if receipt_target and receipt_target.exists() else None
    try:
        if backup_out: os.replace(out,backup_out)
        if backup_receipt and receipt_target: os.replace(receipt_target,backup_receipt)
        os.replace(staged_out,out)
        if staged_receipt and receipt_target: os.replace(staged_receipt,receipt_target)
        if backup_out and backup_out.exists(): backup_out.unlink()
        if backup_receipt and backup_receipt.exists(): backup_receipt.unlink()
    except Exception:
        recovery=[]
        if out.exists() and backup_out:
            failed=out.with_name(f".{out.name}.failed-candidate-{os.getpid()}"); shutil.copy2(out,failed); recovery.append(failed.as_posix()); out.unlink()
        if backup_out and backup_out.exists(): os.replace(backup_out,out)
        if receipt_target and receipt_target.exists() and backup_receipt:
            fr=receipt_target.with_name(f".{receipt_target.name}.failed-candidate-{os.getpid()}"); shutil.copy2(receipt_target,fr); recovery.append(fr.as_posix()); receipt_target.unlink()
        if backup_receipt and backup_receipt.exists() and receipt_target: os.replace(backup_receipt,receipt_target)
        if staged_out.exists(): recovery.append(staged_out.as_posix())
        if staged_receipt and staged_receipt.exists(): recovery.append(staged_receipt.as_posix())
        raise RuntimeError("atomic delivery failed; recovery paths: "+", ".join(recovery))


def main(argv: Optional[Sequence[str]]=None)->int:
    p=argparse.ArgumentParser(description="Analyze EF Core migration conflicts with reproducible version/provider/artifact evidence.")
    p.add_argument("paths",nargs="*",help="Migration files/directories, or repository root with --git-base.")
    p.add_argument("--git-base"); p.add_argument("--include-support-files",action="store_true"); p.add_argument("--snapshot",action="append",default=[])
    p.add_argument("--generated-sql",action="append",default=[]); p.add_argument("--reviewed-sql",action="append",default=[]); p.add_argument("--deployment-sql",action="append",default=[]); p.add_argument("--rollback-sql",action="append",default=[])
    p.add_argument("--runtime-code",action="append",default=[]); p.add_argument("--semantic-evidence",action="append",default=[])
    p.add_argument("--deployment-instances",choices=("unknown","single","multiple"),default="unknown"); p.add_argument("--deployment-method",choices=("unknown","runtime","sql-script","idempotent-script","bundle","deployment-job"),default="unknown")
    p.add_argument("--ef-core-version"); p.add_argument("--provider"); p.add_argument("--dbcontext"); p.add_argument("--migrations-assembly")
    p.add_argument("--format",choices=("markdown","json"),default="markdown"); p.add_argument("--output"); p.add_argument("--receipt")
    a=p.parse_args(argv)
    if not a.paths and not a.git_base and not a.snapshot: p.error("provide at least one path, --git-base, or --snapshot")
    hs,hhash,_=load_heuristic_set(); profiles,phash,_=load_provider_profiles(); git_identity=None; base_history=[]; head_history=[]; repo_root=None; notes=[]
    if a.git_base:
        main_files,support_files,git_identity,base_history,head_history,gn,repo_root=collect_git_sources(a.paths or ["."],a.git_base); notes.extend(gn)
        for raw in a.snapshot:
            ex=Path(raw)
            if ex.exists() and ex not in support_files: support_files.append(ex)
    else: main_files,support_files,pn=collect_path_sources(a.paths or [],a.include_support_files,a.snapshot); notes.extend(pn)
    file_ids=[]; by_resolved={}; git_status={x["path"]:x["status"] for x in (git_identity or {}).get("changed_files",[])}
    for path in sorted([*main_files,*support_files],key=lambda x:logical_path(x,repo_root)):
        ident=make_file_identity(path,role_for_path(path),repo_root,git_status.get(logical_path(path,repo_root))); file_ids.append(ident); by_resolved[path.resolve()]=ident
    designer_context={}
    for path in support_files:
        if role_for_path(path)=="designer":
            mid,ctx=parse_designer_context(path)
            if mid and ctx: designer_context[mid]=ctx
    semantic_ids,semantic,semantic_paths=load_semantic_evidence(a.semantic_evidence,repo_root,notes)
    ef_version=a.ef_core_version or semantic.get("ef_core_version"); provider_raw=a.provider or semantic.get("provider"); dbcontext=a.dbcontext or semantic.get("dbcontext"); migrations_assembly=a.migrations_assembly or semantic.get("migrations_assembly")
    context={"ef_core_version":ef_version,"provider":provider_raw,"provider_key":normalize_provider(provider_raw),"dbcontext":dbcontext,"migrations_assembly":migrations_assembly,"deployment_instances":a.deployment_instances,"deployment_method":a.deployment_method}
    provider_key=normalize_provider(provider_raw); selected_profile=profiles.get("providers",{}).get(provider_key) if provider_key else None
    sorted_main=sorted(main_files,key=lambda x:((x.name[:14] if re.match(r"^\d{14}_",x.name) else ""),logical_path(x,repo_root))); operations=[]; metadata=[]
    for order,path in enumerate(sorted_main,1):
        identity=by_resolved[path.resolve()]; mid=migration_id_from_name(path.name); ctx=dbcontext or designer_context.get(mid or ""); ops,meta=parse_file(path,identity,order,ctx); operations.extend(ops); metadata.append(meta)
    snapshots=[]
    for path in support_files:
        if role_for_path(path)=="model_snapshot": snapshots.append((by_resolved[path.resolve()],parse_snapshot_last_migration(path)))
    def collect_artifacts(values,role):
        ids=[]; paths=[]; sources=[]
        for raw in values:
            path=Path(raw)
            if not path.exists(): notes.append(f"{role} not found: {raw}"); continue
            paths.append(path); ident=make_file_identity(path,role,repo_root); ids.append(ident); sources.append((ident,read_text(path)))
        return ids,paths,sources
    generated_ids,generated_paths,generated_sources=collect_artifacts(a.generated_sql,"generated_sql"); reviewed_ids,reviewed_paths,_=collect_artifacts(a.reviewed_sql,"reviewed_sql"); deployment_ids,deployment_paths,_=collect_artifacts(a.deployment_sql,"deployment_sql"); rollback_ids,rollback_paths,_=collect_artifacts(a.rollback_sql,"rollback_sql")
    runtime_ids=[]; runtime_sources=[]; runtime_paths=[]
    for raw in a.runtime_code:
        path=Path(raw)
        if not path.exists(): notes.append(f"runtime code not found: {raw}"); continue
        runtime_paths.append(path); ident=make_file_identity(path,"runtime_code",repo_root); runtime_ids.append(ident); runtime_sources.append((ident,read_text(path)))
    findings,patterns=analyze(operations,metadata,hs,base_history,head_history,snapshots,git_identity,runtime_sources,context,semantic,selected_profile,generated_sources,reviewed_ids,deployment_ids)
    # artifact generated->reviewed drift is distinct from reviewed->deployment drift and does not imply rejection by itself.
    if generated_ids and reviewed_ids and fingerprints(generated_ids)!=fingerprints(reviewed_ids):
        fb=FindingBuilder(hs); ops=[pseudo_operation("GeneratedSql",i.sha256,i.path,i.sha256,"artifact") for i in generated_ids]+[pseudo_operation("ReviewedSql",i.sha256,i.path,i.sha256,"artifact") for i in reviewed_ids]; fb.add("artifact.generated-reviewed-drift",ops,canonical_json({"generated":fingerprints(generated_ids),"reviewed":fingerprints(reviewed_ids)}),"The reviewed SQL differs from the originally supplied generated SQL.","Treat the reviewed artifact as a deliberate modified artifact and ensure review rationale plus deployment identity bind to those reviewed bytes.","Compare reviewed and deployment SHA-256; regenerate review if changes were not intentional.","A reviewed edit can be intentional and safer; this is a traceability signal, not a blocker.","derived",[*fingerprints(generated_ids),*fingerprints(reviewed_ids)]); findings=sorted([*findings,*fb.values()],key=lambda f:(-SEVERITY_ORDER.get(f.severity,0),f.rule_id,f.id))
    input_identity=make_input_identity(file_ids,generated_ids,reviewed_ids,deployment_ids,rollback_ids,runtime_ids,semantic_ids,git_identity,phash)
    report=build_report(main_files,support_files,notes,operations,metadata,findings,patterns,hs,hhash,profiles,phash,selected_profile,input_identity,git_identity,context,semantic,repo_root)
    rendered=json.dumps(report,indent=2,sort_keys=True)+"\n" if a.format=="json" else render_markdown(report)
    protected=[*main_files,*support_files,*generated_paths,*reviewed_paths,*deployment_paths,*rollback_paths,*runtime_paths,*semantic_paths]
    deliver(rendered,a.output,a.receipt,report,protected,a.format)
    return 2 if report["summary"]["decision"]=="block" else 0


if __name__=="__main__": raise SystemExit(main())
