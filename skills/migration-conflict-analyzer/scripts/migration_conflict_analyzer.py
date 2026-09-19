#!/usr/bin/env python3
"""Deterministic static analyzer for EF Core migration conflicts and hazards.

The analyzer intentionally does not compile C# and does not claim provider/runtime
certainty from source heuristics. Objective mechanics (identity, extraction,
ordering, rule selection, finding IDs, receipts) are deterministic. Conclusions
that depend on intent, data, provider behavior, or deployment topology carry an
explicit confidence/evidence status and uncertainty statement.
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
import tempfile
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

ANALYSIS_VERSION = "2.0.0"
REPORT_SCHEMA_VERSION = "2.0"
SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
MAIN_MIGRATION_RE = re.compile(r"^\d{14}_.+\.cs$")
EXCLUDED_RE = re.compile(r"(\.Designer\.cs$|ModelSnapshot\.cs$)")
MUTATING_SQL_RE = re.compile(r"\b(create|alter|drop|truncate|merge|update|delete|insert|exec|execute)\b", re.I)
NON_IDEMPOTENT_UPDATE_RE = re.compile(r"\bset\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\1\s*[+\-]", re.I)
STARTUP_MIGRATE_RE = re.compile(r"\bDatabase\s*\.\s*(?:Migrate|MigrateAsync)\s*\(", re.I)
KNOWN_OPS = {
    "AddColumn", "DropColumn", "AlterColumn", "RenameColumn",
    "CreateTable", "DropTable", "RenameTable",
    "CreateIndex", "DropIndex",
    "AddForeignKey", "DropForeignKey",
    "AddPrimaryKey", "DropPrimaryKey",
    "AddUniqueConstraint", "DropUniqueConstraint",
    "AddCheckConstraint", "DropCheckConstraint",
    "Sql",
}


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


def find_invocations(body: str) -> List[Tuple[str, str]]:
    calls: List[Tuple[str, str]] = []
    token = "migrationBuilder."
    cursor = 0
    while True:
        start = body.find(token, cursor)
        if start < 0:
            break
        op_start = start + len(token)
        match = re.match(r"([A-Za-z_][A-Za-z0-9_]*)(?:\s*<[^>]+>)?\s*\(", body[op_start:])
        if not match:
            cursor = op_start
            continue
        op = match.group(1)
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
        calls.append((op, body[paren_start + 1:end]))
        cursor = end + 1
    return calls


def named_string(args: str, key: str) -> Optional[str]:
    for pattern in (
        rf"\b{re.escape(key)}\s*:\s*@?\"([^\"]*)\"",
        rf"\b{re.escape(key)}\s*=\s*@?\"([^\"]*)\"",
    ):
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


def has_named(args: str, key: str) -> bool:
    return re.search(rf"\b{re.escape(key)}\s*:", args) is not None


def named_string_list(args: str, singular: str, plural: str) -> List[str]:
    one = named_string(args, singular)
    if one is not None:
        return [one]
    match = re.search(rf"\b{re.escape(plural)}\s*:\s*new(?:\s+[A-Za-z0-9_<>\[\]]+)?\s*\[?\]?\s*\{{(.*?)\}}", args, flags=re.S)
    if not match:
        match = re.search(rf"\b{re.escape(plural)}\s*:\s*new\[\]\s*\{{(.*?)\}}", args, flags=re.S)
    if not match:
        return []
    return re.findall(r"@?\"([^\"]+)\"", match.group(1))


def extract_create_table_columns(args: str) -> List[Tuple[str, Optional[bool], bool]]:
    result: List[Tuple[str, Optional[bool], bool]] = []
    pattern = r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*table\.Column(?:<[^>]+>)?\s*\((.*?)\)"
    for match in re.finditer(pattern, args, flags=re.S):
        col_args = match.group(2)
        result.append((
            match.group(1),
            named_bool(col_args, "nullable"),
            has_named(col_args, "defaultValue") or has_named(col_args, "defaultValueSql") or has_named(col_args, "computedColumnSql"),
        ))
    return result


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
    timestamp: Optional[str]
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
    has_default: bool = False
    unique: Optional[bool] = None
    principal_table: Optional[str] = None
    principal_columns: List[str] = field(default_factory=list)
    suppress_transaction: bool = False
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


def load_heuristic_set() -> Tuple[Dict[str, Any], str, Path]:
    path = Path(__file__).resolve().parents[1] / "references" / "heuristic-set.json"
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    if data.get("set_name") != "migration-conflict-analyzer" or not data.get("version"):
        raise ValueError("invalid heuristic-set identity")
    if not isinstance(data.get("rules"), dict) or not data["rules"]:
        raise ValueError("heuristic-set has no rules")
    return data, sha256_bytes(raw), path


def make_file_identity(path: Path, role: str, repo_root: Optional[Path] = None, git_status: Optional[str] = None) -> FileIdentity:
    data = read_bytes(path)
    return FileIdentity(logical_path(path, repo_root), role, sha256_bytes(data), len(data), git_status)


def git_run(args: Sequence[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    return subprocess.run(["git", *args], cwd=cwd, env=env, check=check, text=True, capture_output=True)


def git_object_bytes(repo_root: Path, revision: str, relpath: str) -> Optional[bytes]:
    env = os.environ.copy()
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    proc = subprocess.run(
        ["git", "show", f"{revision}:{relpath}"],
        cwd=repo_root,
        env=env,
        check=False,
        capture_output=True,
        text=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def collect_git_sources(paths: Sequence[str], git_base: str) -> Tuple[List[Path], List[Path], Dict[str, Any], List[Dict[str, Any]], List[str], Path]:
    start = Path(paths[0] if paths else ".").resolve()
    if start.is_file():
        start = start.parent
    repo_root = Path(git_run(["rev-parse", "--show-toplevel"], start).stdout.strip()).resolve()
    base_sha = git_run(["rev-parse", f"{git_base}^{{commit}}"], repo_root).stdout.strip()
    head_sha = git_run(["rev-parse", "HEAD^{commit}"], repo_root).stdout.strip()
    merge_base_sha = git_run(["merge-base", base_sha, head_sha], repo_root).stdout.strip()
    dirty = bool(git_run(["status", "--porcelain"], repo_root).stdout.strip())
    diff_proc = git_run(["diff", "--name-status", "--find-renames", f"{base_sha}...{head_sha}"], repo_root)
    changed: List[Dict[str, str]] = []
    main_files: List[Path] = []
    support_files: List[Path] = []
    notes: List[str] = []
    for line in diff_proc.stdout.splitlines():
        parts = line.split("\t")
        if not parts:
            continue
        status = parts[0]
        rel = parts[-1]
        changed.append({"status": status, "path": rel})
        path = repo_root / rel
        if status.startswith("D") or not path.exists():
            continue
        role = role_for_path(path)
        if role == "migration":
            main_files.append(path)
        elif role in ("model_snapshot", "designer"):
            support_files.append(path)
    tree = git_run(["ls-tree", "-r", "--name-only", base_sha], repo_root).stdout.splitlines()
    base_history: List[Dict[str, Any]] = []
    base_snapshots: List[Dict[str, Any]] = []
    for rel in sorted(tree):
        name = Path(rel).name
        if not is_main_migration_name(name) and not name.endswith("ModelSnapshot.cs"):
            continue
        data = git_object_bytes(repo_root, base_sha, rel)
        if data is None:
            continue
        digest = sha256_bytes(data)
        if is_main_migration_name(name):
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = data.decode("latin-1")
            base_history.append({
                "path": rel,
                "timestamp": name[:14],
                "class_name": migration_name_from_text(name, strip_comments(text)),
                "sha256": digest,
            })
        else:
            base_snapshots.append({"path": rel, "sha256": digest, "size": len(data)})
    git_identity = {
        "repository_root": repo_root.as_posix(),
        "base_requested": git_base,
        "base_sha": base_sha,
        "head_sha": head_sha,
        "merge_base_sha": merge_base_sha,
        "working_tree_dirty": dirty,
        "changed_files": sorted(changed, key=lambda x: (x["path"], x["status"])),
        "base_snapshot_identity": base_snapshots,
    }
    notes.append(f"git diff identity: {base_sha}...{head_sha}")
    return sorted(set(main_files)), sorted(set(support_files)), git_identity, base_history, notes, repo_root


def collect_path_sources(paths: Sequence[str], include_support_files: bool, extra_snapshots: Sequence[str]) -> Tuple[List[Path], List[Path], List[str]]:
    main_files: List[Path] = []
    support_files: List[Path] = []
    notes: List[str] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            for child in sorted(path.rglob("*.cs")):
                role = role_for_path(child)
                if role == "migration":
                    main_files.append(child)
                elif include_support_files and role in ("model_snapshot", "designer"):
                    support_files.append(child)
        elif path.exists():
            role = role_for_path(path)
            if role == "migration":
                main_files.append(path)
            elif role in ("model_snapshot", "designer"):
                support_files.append(path)
            else:
                notes.append(f"ignored unsupported input: {raw}")
        else:
            notes.append(f"path not found: {raw}")
    for raw in extra_snapshots:
        path = Path(raw)
        if path.exists():
            support_files.append(path)
        else:
            notes.append(f"snapshot not found: {raw}")
    unique_main = sorted({p.resolve(): p for p in main_files}.values(), key=lambda p: p.as_posix())
    unique_support = sorted({p.resolve(): p for p in support_files}.values(), key=lambda p: p.as_posix())
    return unique_main, unique_support, notes


def parse_file(path: Path, file_identity: FileIdentity, migration_order: int) -> Tuple[List[Operation], Dict[str, Any]]:
    text = strip_comments(read_text(path))
    migration = migration_name_from_text(path.name, text)
    timestamp = path.name[:14] if re.match(r"^\d{14}_", path.name) else None
    up_body = extract_method_body(text, "Up")
    down_body = extract_method_body(text, "Down")
    metadata = {
        "file": file_identity.path,
        "file_sha256": file_identity.sha256,
        "migration": migration,
        "timestamp": timestamp,
        "class_name": migration,
        "has_up": bool(up_body.strip()),
        "has_down": bool(down_body.strip()),
        "migration_order": migration_order,
    }
    operations: List[Operation] = []
    for method, body in (("Up", up_body), ("Down", down_body)):
        for ordinal, (op, args) in enumerate(find_invocations(body), 1):
            table: Optional[str] = None
            column: Optional[str] = None
            columns: List[str] = []
            name: Optional[str] = None
            new_name: Optional[str] = None
            object_type = "unknown" if op not in KNOWN_OPS else "object"
            nullable = named_bool(args, "nullable")
            has_default = has_named(args, "defaultValue") or has_named(args, "defaultValueSql") or has_named(args, "computedColumnSql")
            unique = named_bool(args, "unique")
            principal_table: Optional[str] = None
            principal_columns: List[str] = []
            suppress_transaction = bool(named_bool(args, "suppressTransaction"))
            raw = args[:1200]

            if op == "CreateTable":
                table = named_string(args, "name") or first_positional_string(args)
                name = table
                object_type = "table"
            elif op in ("DropTable", "RenameTable"):
                table = named_string(args, "name") or first_positional_string(args)
                name = table
                new_name = named_string(args, "newName") or named_string(args, "newTable")
                object_type = "table"
            elif op in ("AddColumn", "DropColumn", "AlterColumn", "RenameColumn"):
                table = named_string(args, "table")
                column = named_string(args, "name") or named_string(args, "column") or first_positional_string(args)
                columns = [column] if column else []
                name = column
                new_name = named_string(args, "newName")
                object_type = "column"
            elif op in ("CreateIndex", "DropIndex"):
                table = named_string(args, "table")
                name = named_string(args, "name") or first_positional_string(args)
                columns = named_string_list(args, "column", "columns")
                column = columns[0] if len(columns) == 1 else None
                object_type = "index"
            elif op in ("AddForeignKey", "DropForeignKey"):
                table = named_string(args, "table")
                name = named_string(args, "name") or first_positional_string(args)
                columns = named_string_list(args, "column", "columns")
                column = columns[0] if len(columns) == 1 else None
                principal_table = named_string(args, "principalTable")
                principal_columns = named_string_list(args, "principalColumn", "principalColumns")
                object_type = "foreign_key"
            elif op in ("AddPrimaryKey", "DropPrimaryKey"):
                table = named_string(args, "table")
                name = named_string(args, "name") or first_positional_string(args)
                columns = named_string_list(args, "column", "columns")
                object_type = "primary_key"
            elif op in ("AddUniqueConstraint", "DropUniqueConstraint"):
                table = named_string(args, "table")
                name = named_string(args, "name") or first_positional_string(args)
                columns = named_string_list(args, "column", "columns")
                object_type = "unique_constraint"
            elif op in ("AddCheckConstraint", "DropCheckConstraint"):
                table = named_string(args, "table")
                name = named_string(args, "name") or first_positional_string(args)
                object_type = "check_constraint"
            elif op == "Sql":
                name = "raw_sql"
                object_type = "sql"
                raw = first_positional_string(args) or args[:1200]
            else:
                table = named_string(args, "table")
                name = named_string(args, "name") or first_positional_string(args)
                columns = named_string_list(args, "column", "columns")
                column = columns[0] if len(columns) == 1 else None

            op_payload = {
                "file_sha256": file_identity.sha256,
                "migration": migration,
                "timestamp": timestamp,
                "method": method,
                "migration_order": migration_order,
                "ordinal": ordinal,
                "op": op,
                "table": table,
                "column": column,
                "columns": columns,
                "name": name,
                "new_name": new_name,
                "nullable": nullable,
                "has_default": has_default,
                "unique": unique,
                "principal_table": principal_table,
                "principal_columns": principal_columns,
                "suppress_transaction": suppress_transaction,
            }
            operation_id = "op-" + sha256_text(canonical_json(op_payload))[:16]
            operations.append(Operation(
                operation_id,
                file_identity.path,
                file_identity.sha256,
                migration,
                timestamp,
                method,
                migration_order,
                ordinal,
                op,
                table,
                column,
                columns,
                name,
                new_name,
                object_type,
                nullable,
                has_default,
                unique,
                principal_table,
                principal_columns,
                suppress_transaction,
                raw,
            ))

            if op == "CreateTable" and table:
                for col_index, (col_name, col_nullable, col_has_default) in enumerate(extract_create_table_columns(args), 1):
                    payload = dict(op_payload)
                    payload.update({"op": "CreateTableColumn", "column": col_name, "columns": [col_name], "ordinal": ordinal * 1000 + col_index})
                    child_id = "op-" + sha256_text(canonical_json(payload))[:16]
                    operations.append(Operation(
                        child_id,
                        file_identity.path,
                        file_identity.sha256,
                        migration,
                        timestamp,
                        method,
                        migration_order,
                        ordinal * 1000 + col_index,
                        "CreateTableColumn",
                        table,
                        col_name,
                        [col_name],
                        col_name,
                        None,
                        "column",
                        col_nullable,
                        col_has_default,
                        None,
                        None,
                        [],
                        False,
                        args[:1200],
                    ))
    return operations, metadata


def group_by_key(ops: Iterable[Operation], key_fn) -> Dict[Any, List[Operation]]:
    groups: Dict[Any, List[Operation]] = defaultdict(list)
    for op in ops:
        key = key_fn(op)
        if key is None:
            continue
        if isinstance(key, tuple) and any(part is None or part == "" or part == () for part in key):
            continue
        groups[key].append(op)
    return groups


class FindingBuilder:
    def __init__(self, heuristic_set: Dict[str, Any]):
        self.rules = heuristic_set["rules"]
        self._items: Dict[str, Finding] = {}

    def add(
        self,
        rule_id: str,
        ops: Sequence[Operation],
        evidence: str,
        why: str,
        recommendation: str,
        validation: str,
        uncertainty: str,
        evidence_status: str = "observed",
        subject_tokens: Sequence[str] = (),
    ) -> None:
        rule = self.rules[rule_id]
        op_ids = sorted({op.id for op in ops})
        identity_payload = {"rule_id": rule_id, "operation_ids": op_ids, "subjects": sorted(set(subject_tokens))}
        finding_id = f"mca:{rule_id}:{sha256_text(canonical_json(identity_payload))[:16]}"
        files = sorted({op.file for op in ops})
        self._items[finding_id] = Finding(
            finding_id,
            rule_id,
            rule["severity"],
            rule["confidence"],
            evidence_status,
            rule["gate"],
            rule["hazard_type"],
            rule["title"],
            files,
            op_ids,
            evidence,
            why,
            recommendation,
            validation,
            uncertainty,
        )

    def values(self) -> List[Finding]:
        return sorted(
            self._items.values(),
            key=lambda f: (-SEVERITY_ORDER.get(f.severity, 0), f.rule_id, f.id),
        )


def op_target(op: Operation) -> str:
    if op.table and op.column:
        return f"{op.table}.{op.column}"
    if op.table and op.columns:
        return f"{op.table}({','.join(op.columns)})"
    return op.table or op.name or op.object_type or "unknown"


def evidence_for_ops(ops: Sequence[Operation]) -> str:
    ordered = sorted(ops, key=lambda o: (o.migration_order, o.ordinal, o.file, o.id))
    return "; ".join(f"{op.file}:{op.migration}.{op.op}({op_target(op)})" for op in ordered[:8])


def operation_position(op: Operation) -> Tuple[int, int, str]:
    return (op.migration_order, op.ordinal, op.id)


def analyze(
    operations: List[Operation],
    metadata: List[Dict[str, Any]],
    heuristic_set: Dict[str, Any],
    base_history: List[Dict[str, Any]],
    model_snapshots: List[FileIdentity],
    git_identity: Optional[Dict[str, Any]],
    runtime_sources: List[Tuple[FileIdentity, str]],
    deployment_instances: str,
) -> Tuple[List[Finding], Dict[str, Any]]:
    builder = FindingBuilder(heuristic_set)
    up_ops = [op for op in operations if op.method == "Up"]

    by_timestamp: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    by_class: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for meta in metadata:
        if meta.get("timestamp"):
            by_timestamp[str(meta["timestamp"])].append(meta)
        if meta.get("class_name"):
            by_class[str(meta["class_name"])].append(meta)
        if not meta.get("has_up"):
            pseudo = Operation("meta-" + sha256_text(canonical_json(meta))[:16], meta["file"], meta["file_sha256"], meta["migration"], meta.get("timestamp"), "meta", int(meta["migration_order"]), 0, "MissingUp")
            builder.add("structure.missing-up", [pseudo], canonical_json(meta), "The standard EF Core migration entry point has no explicit Up body.", "Regenerate or repair the migration so schema operations are explicit in Up().", "Compile the project and generate the migration SQL.", "Custom migration infrastructure could intentionally route work elsewhere; static analysis cannot prove that intent.")
        if not meta.get("has_down"):
            pseudo = Operation("meta-" + sha256_text(canonical_json({"down": meta}))[:16], meta["file"], meta["file_sha256"], meta["migration"], meta.get("timestamp"), "meta", int(meta["migration_order"]), 0, "MissingDown")
            builder.add("structure.missing-down", [pseudo], canonical_json(meta), "Rollback behavior is absent from the standard Down method.", "Add a safe Down implementation or document why rollback is intentionally unsupported.", "Review rollback expectations and generated down-script behavior if used.", "A missing Down method does not prove deployment failure; it limits rollback evidence.")

    for timestamp, metas in sorted(by_timestamp.items()):
        if len(metas) > 1:
            ops = [Operation("meta-" + sha256_text(canonical_json(m))[:16], m["file"], m["file_sha256"], m["migration"], m.get("timestamp"), "meta", int(m["migration_order"]), 0, "MigrationId", name=timestamp) for m in metas]
            builder.add("history.duplicate-timestamp", ops, evidence_for_ops(ops), "The changed migration set contains the same migration timestamp more than once.", "Regenerate one migration after rebasing on the current history.", "Run dotnet ef migrations list and inspect the generated SQL/history ordering.", "Provider-specific migration discovery may add context, but the duplicate timestamp is directly observed.", "derived", [timestamp])
    for class_name, metas in sorted(by_class.items()):
        if len(metas) > 1:
            ops = [Operation("meta-" + sha256_text(canonical_json({"class": m}))[:16], m["file"], m["file_sha256"], m["migration"], m.get("timestamp"), "meta", int(m["migration_order"]), 0, "MigrationClass", name=class_name) for m in metas]
            builder.add("history.duplicate-class", ops, evidence_for_ops(ops), "The changed migration set contains the same migration class more than once.", "Rename or regenerate one migration and rebuild the project.", "Run dotnet build and dotnet ef migrations list.", "Compilation outcome is not executed by this analyzer.", "derived", [class_name])

    if base_history:
        base_by_timestamp: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        base_by_class: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for item in base_history:
            base_by_timestamp[item["timestamp"]].append(item)
            base_by_class[item["class_name"]].append(item)
        for meta in metadata:
            collisions: List[Dict[str, Any]] = []
            if meta.get("timestamp"):
                collisions.extend(base_by_timestamp.get(str(meta["timestamp"]), []))
            collisions.extend(base_by_class.get(str(meta.get("class_name")), []))
            dedup = {(c["path"], c["sha256"]): c for c in collisions}
            if dedup:
                pseudo = Operation("meta-" + sha256_text(canonical_json({"base": meta}))[:16], meta["file"], meta["file_sha256"], meta["migration"], meta.get("timestamp"), "meta", int(meta["migration_order"]), 0, "BaseHistoryCollision", name=str(meta.get("timestamp")))
                base_desc = ", ".join(f"{c['path']}@{c['sha256'][:12]}" for c in sorted(dedup.values(), key=lambda x: x["path"]))
                builder.add("history.base-collision", [pseudo], f"changed={meta['file']} base={base_desc}", "A changed migration reuses an identity already present in the resolved git base history.", "Rebase on the base history and regenerate the newer migration; do not silently rewrite an applied migration.", "Compare dotnet ef migrations list and generated SQL from the recorded base/head SHAs.", "Whether a same-path edit is intentionally safe depends on whether that migration has ever been applied; that deployment fact is not inferred.", "derived", [meta["file_sha256"], *[c["sha256"] for c in dedup.values()]])

    created_tables_same_file = {(op.table, op.file) for op in up_ops if op.op == "CreateTable" and op.table}

    for (table, column), ops in sorted(group_by_key((o for o in up_ops if o.op == "AddColumn"), lambda o: (o.table, o.column)).items()):
        if len({o.file for o in ops}) > 1:
            builder.add("duplicate.add-column", ops, evidence_for_ops(ops), "More than one changed migration adds the same table/column.", "Keep one AddColumn and regenerate the later branch migration after rebase.", "Generate SQL and apply it to clean and upgraded test databases.", "Manual out-of-band schema changes can alter runtime behavior, but the duplicate source operations are directly observed.", "derived", [str(table), str(column)])

    for (table,), ops in sorted(group_by_key((o for o in up_ops if o.op == "CreateTable"), lambda o: (o.table,)).items()):
        if len({o.file for o in ops}) > 1:
            builder.add("duplicate.create-table", ops, evidence_for_ops(ops), "More than one changed migration creates the same table.", "Keep one table creation and regenerate dependent migrations.", "Generate SQL from an empty database baseline.", "Provider-specific IF NOT EXISTS behavior is not assumed.", "derived", [str(table)])

    named_creation_ops = [o for o in up_ops if o.op in ("CreateIndex", "AddForeignKey", "AddPrimaryKey", "AddUniqueConstraint", "AddCheckConstraint") and o.name]
    for (op_name, object_name), ops in sorted(group_by_key(named_creation_ops, lambda o: (o.op, o.name)).items()):
        if len({o.file for o in ops}) > 1:
            builder.add("duplicate.object-name", ops, evidence_for_ops(ops), "The same named database object is created by multiple changed migrations.", "Consolidate the operations or use distinct provider-valid object names.", "Inspect provider-specific generated SQL.", "Name scope can vary by provider; the duplicate source name is observed but provider enforcement is not assumed.", "derived", [str(op_name), str(object_name)])

    for (table, columns), ops in sorted(group_by_key((o for o in up_ops if o.op == "CreateIndex" and o.columns), lambda o: (o.table, tuple(o.columns))).items(), key=lambda item: str(item[0])):
        signatures = {(o.name, o.unique) for o in ops}
        if len(ops) > 1 and len(signatures) > 1:
            builder.add("conflict.index-definition", ops, evidence_for_ops(ops), "The same indexed column set is declared with different index identity or uniqueness semantics.", "Choose one intended index definition or sequence the replacement explicitly.", "Generate provider SQL and verify the resulting index catalog.", "Multiple indexes over the same columns can be intentional; this rule identifies conflicting definitions for review rather than proving invalidity.", "inferred", [str(table), canonical_json(list(columns))])

    for (table, columns), ops in sorted(group_by_key((o for o in up_ops if o.op == "AddForeignKey" and o.columns), lambda o: (o.table, tuple(o.columns))).items(), key=lambda item: str(item[0])):
        destinations = {(o.principal_table, tuple(o.principal_columns)) for o in ops}
        if len(ops) > 1 and len(destinations) > 1:
            builder.add("conflict.foreign-key-definition", ops, evidence_for_ops(ops), "The same local foreign-key column set points at different principal targets.", "Resolve the intended relationship and regenerate the migration from the reconciled model.", "Generate SQL and inspect the final FK catalog on the target provider.", "The model may intentionally transition between relationships; static analysis cannot establish business intent.", "inferred", [str(table), canonical_json(list(columns))])

    destructive_drops = [o for o in up_ops if o.op in ("DropColumn", "DropTable")]
    for op in destructive_drops:
        if op.op == "DropColumn":
            builder.add("destructive.drop-column", [op], evidence_for_ops([op]), "The migration explicitly removes a column.", "Verify all readers/writers are migrated, preserve/backfill required data, and use expand-contract when versions can overlap.", "Inspect generated SQL and validate against representative upgraded data before the destructive step.", "The analyzer does not know whether the column contains data or whether all consumers have stopped using it; it flags the destructive operation itself, not guaranteed data loss.", "observed", [op_target(op)])
        else:
            builder.add("destructive.drop-table", [op], evidence_for_ops([op]), "The migration explicitly removes a table.", "Verify consumer retirement and data-retention requirements; use a staged contract release when versions can overlap.", "Inspect generated SQL and validate on an upgraded database copy.", "The analyzer does not know data-retention policy or consumer state; it does not claim runtime failure.", "observed", [op_target(op)])

    ordered_up = sorted(up_ops, key=operation_position)
    for drop in [o for o in ordered_up if o.op == "DropColumn" and o.table and o.column]:
        later = []
        for op in ordered_up:
            if operation_position(op) <= operation_position(drop) or op is drop or op.table != drop.table:
                continue
            refs = set(op.columns)
            if op.column:
                refs.add(op.column)
            if op.name and op.object_type == "column":
                refs.add(op.name)
            if drop.column in refs and op.op not in ("AddColumn",):
                later.append(op)
        if later:
            builder.add("ordering.after-drop", [drop, *later], evidence_for_ops([drop, *later]), "A later changed operation still references a column after the recorded migration order drops it.", "Reorder or split the migrations so dependent operations complete before the drop, or remove the stale dependency.", "Generate SQL from the recorded migration order and apply it to an upgraded database copy.", "Custom SQL or provider-specific rewriting outside the parsed operations could change execution details; the source ordering dependency is directly derived.", "derived", [drop.table, drop.column])

    for drop in [o for o in ordered_up if o.op == "DropTable" and o.table]:
        later = [o for o in ordered_up if operation_position(o) > operation_position(drop) and o.table == drop.table and o is not drop]
        if later:
            builder.add("ordering.after-drop", [drop, *later], evidence_for_ops([drop, *later]), "A later changed operation references a table after the recorded migration order drops it.", "Move dependent work before the drop or stage the contract change in a later release.", "Generate and execute the ordered SQL against an upgraded database copy.", "Raw SQL or custom helpers outside parsed operations may add additional dependencies not seen here.", "derived", [drop.table])

    for rename in [o for o in ordered_up if o.op == "RenameColumn" and o.table and o.column and o.new_name]:
        stale_later = []
        for op in ordered_up:
            if operation_position(op) <= operation_position(rename) or op is rename or op.table != rename.table:
                continue
            refs = set(op.columns)
            if op.column:
                refs.add(op.column)
            if rename.column in refs:
                stale_later.append(op)
        if stale_later:
            builder.add("ordering.rename", [rename, *stale_later], evidence_for_ops([rename, *stale_later]), "Later operations still reference the pre-rename column identity.", "Update dependent operations to the new name or keep the rename and dependencies in one coherent migration.", "Inspect generated SQL ordering and run the upgrade path.", "Custom helper behavior is not compiled by this analyzer.", "derived", [rename.table, rename.column, rename.new_name])

    drops_by_table: Dict[str, List[Operation]] = defaultdict(list)
    adds_by_table: Dict[str, List[Operation]] = defaultdict(list)
    for op in up_ops:
        if op.op == "DropColumn" and op.table:
            drops_by_table[op.table].append(op)
        elif op.op == "AddColumn" and op.table:
            adds_by_table[op.table].append(op)
    for table in sorted(set(drops_by_table) & set(adds_by_table)):
        ops = drops_by_table[table] + adds_by_table[table]
        builder.add("rename.drop-add", ops, evidence_for_ops(ops), "The changed set drops and adds columns on the same table, which can be scaffolded when a rename was not recognized.", "If this is a rename, use RenameColumn or an explicit copy/backfill sequence before dropping the source column.", "Inspect generated SQL and verify data preservation with representative rows.", "Drop/add can be intentional replacement rather than rename; this is a medium-confidence intent heuristic and must not be treated as proof of data loss.", "inferred", [table])

    for op in [o for o in up_ops if o.op == "AddColumn" and o.nullable is False and not o.has_default]:
        if (op.table, op.file) not in created_tables_same_file:
            builder.add("column.required-without-backfill", [op], evidence_for_ops([op]), "A required column is added without a default/computed value in the parsed operation and the table is not created in the same migration file.", "Add it nullable first, provide a deliberate default/backfill, then enforce NOT NULL in a later step.", "Apply generated SQL to an upgraded database with existing rows.", "An earlier out-of-band backfill or provider behavior may change the outcome; no database contents were inspected.", "observed", [op_target(op)])

    for (table, column), ops in sorted(group_by_key((o for o in up_ops if o.op == "AlterColumn"), lambda o: (o.table, o.column)).items()):
        if len({o.file for o in ops}) > 1:
            builder.add("column.multiple-alter", ops, evidence_for_ops(ops), "The same column is altered in multiple changed migrations, making ordering and conversion semantics material.", "Consolidate the final shape where possible or document the staged transition and order.", "Generate provider-specific SQL and test with representative existing data.", "Some staged transitions are intentional; this rule requests ordering review rather than declaring a conflict.", "inferred", [str(table), str(column)])

    for op in [o for o in up_ops if o.op == "CreateIndex" and o.unique is True]:
        if (op.table, op.file) in created_tables_same_file:
            continue
        builder.add("index.unique-data-check", [op], evidence_for_ops([op]), "The migration creates a unique index over an existing table in the analyzed migration file.", "Check for duplicates before rollout or clean/backfill data before enforcing uniqueness.", "Run a duplicate-detection query on representative production-like data.", "No database rows were inspected; uniqueness failure is not asserted.", "inferred", [op_target(op), op.name or ""])

    for op in [o for o in up_ops if o.op == "Sql"]:
        raw = op.raw or ""
        mutating = bool(MUTATING_SQL_RE.search(raw))
        likely_non_idempotent = bool(NON_IDEMPOTENT_UPDATE_RE.search(raw)) or (bool(re.search(r"\binsert\s+into\b", raw, re.I)) and not bool(re.search(r"\b(on\s+conflict|where\s+not\s+exists|merge)\b", raw, re.I)))
        if likely_non_idempotent:
            builder.add("raw-sql.non-idempotent-data", [op], evidence_for_ops([op]), "The raw SQL contains a rerun-sensitive data mutation pattern such as self-increment or unguarded insert.", "Make rerun behavior explicit and safe, or move the data change to an idempotent operational job with its own checkpointing.", "Execute the exact generated SQL twice against a disposable representative database and compare state.", "The detector recognizes only a narrow set of SQL patterns; provider semantics and surrounding guards can change actual idempotency.", "inferred", [sha256_text(raw)])
        if mutating:
            builder.add("raw-sql.opaque-mutation", [op], evidence_for_ops([op]), "Raw SQL mutates schema or data outside EF's structured operation model.", "Review provider-specific SQL, dependencies, transaction semantics, and rerun behavior explicitly.", "Inspect the final generated SQL and test clean plus upgrade paths.", "Static regex inspection cannot prove SQL correctness, lock behavior, or provider-specific effects.", "observed", [sha256_text(raw)])
        else:
            builder.add("raw-sql.manual-review", [op], evidence_for_ops([op]), "The analyzer cannot semantically interpret this raw SQL.", "Document intent and validate it on the target provider.", "Inspect generated SQL and execute it in a representative environment.", "No safety conclusion is derived from unrecognized SQL text.", "blocked", [sha256_text(raw)])
        if op.suppress_transaction:
            builder.add("raw-sql.suppress-transaction", [op], evidence_for_ops([op]), "The raw SQL explicitly requests suppressTransaction: true.", "Document why transactional execution is unsafe or unsupported and define recovery/idempotency behavior.", "Test interruption and rerun behavior on the target provider.", "Transaction support differs by provider; the suppression flag itself is directly observed.", "observed", [sha256_text(raw)])

    for op in [o for o in up_ops if o.op not in KNOWN_OPS and o.op != "CreateTableColumn"]:
        builder.add("unknown.operation", [op], evidence_for_ops([op]), "The migrationBuilder invocation is outside the analyzer's frozen operation vocabulary.", "Review the custom/provider operation manually and, if recurring, add a versioned parser rule plus regression scenario.", "Inspect generated SQL and provider documentation for this operation.", "The analyzer intentionally does not infer semantics for unknown operations.", "blocked", [op.op, op_target(op)])

    if git_identity is not None:
        changed = git_identity.get("changed_files", [])
        migration_changed = any(is_main_migration_name(Path(item["path"]).name) and not str(item["status"]).startswith("D") for item in changed)
        snapshot_changed = any(Path(item["path"]).name.endswith("ModelSnapshot.cs") for item in changed)
        if snapshot_changed and not migration_changed and model_snapshots:
            snapshot_tokens = [s.sha256 for s in model_snapshots]
            pseudo_ops = [Operation("snapshot-" + s.sha256[:16], s.path, s.sha256, "model-snapshot", None, "meta", 0, 0, "ModelSnapshot", object_type="snapshot") for s in model_snapshots]
            builder.add("snapshot.divergence", pseudo_ops, "; ".join(f"{s.path}@{s.sha256[:12]}" for s in model_snapshots), "The model snapshot changed without a corresponding changed migration in the analyzed Git diff.", "Confirm whether a migration is missing or whether the snapshot change is intentional; regenerate from the reconciled model if needed.", "Run dotnet ef migrations has-pending-model-changes where supported and compare the recorded base/head snapshots.", "Snapshot-only change is a divergence signal, not proof that current migrations fail.", "inferred", snapshot_tokens)
        elif migration_changed and not snapshot_changed:
            changed_migration_tokens = [m["file_sha256"] for m in metadata]
            pseudo_ops = [Operation("snapshot-missing-" + m["file_sha256"][:16], m["file"], m["file_sha256"], m["migration"], m.get("timestamp"), "meta", int(m["migration_order"]), 0, "MissingSnapshotChange", object_type="snapshot") for m in metadata]
            builder.add("snapshot.divergence", pseudo_ops, evidence_for_ops(pseudo_ops), "Changed migrations were detected in Git mode without a changed ModelSnapshot file.", "Confirm the DbContext snapshot was regenerated from the same model state or document why no snapshot change is expected.", "Run dotnet ef migrations has-pending-model-changes and inspect the resolved base/head snapshot identities.", "Some migrations can legitimately leave the snapshot unchanged; this is a review signal only.", "inferred", changed_migration_tokens)
    elif model_snapshots and not metadata:
        snapshot_tokens = [s.sha256 for s in model_snapshots]
        pseudo_ops = [Operation("snapshot-" + s.sha256[:16], s.path, s.sha256, "model-snapshot", None, "meta", 0, 0, "ModelSnapshot", object_type="snapshot") for s in model_snapshots]
        builder.add("snapshot.divergence", pseudo_ops, "; ".join(f"{s.path}@{s.sha256[:12]}" for s in model_snapshots), "A model snapshot was supplied without a corresponding migration in the analyzed input set.", "Confirm whether a migration is missing or whether the snapshot-only input is intentional.", "Run dotnet ef migrations has-pending-model-changes where supported.", "A snapshot-only input is a divergence signal, not proof of migration failure.", "inferred", snapshot_tokens)

    runtime_hits: List[Tuple[FileIdentity, str]] = []
    for identity, text in runtime_sources:
        if STARTUP_MIGRATE_RE.search(text):
            runtime_hits.append((identity, text))
    if runtime_hits:
        pseudo_ops = [Operation("runtime-" + item.sha256[:16], item.path, item.sha256, "runtime", None, "runtime", 0, 0, "Database.Migrate", object_type="runtime") for item, _ in runtime_hits]
        if deployment_instances == "multiple":
            builder.add("runtime.concurrent-startup-migrate", pseudo_ops, "; ".join(f"{item.path}@{item.sha256[:12]}" for item, _ in runtime_hits), "Explicit runtime code applies migrations during startup and the supplied deployment topology says multiple instances may start.", "Apply migrations once in a deployment job/bundle/script before rolling out application instances, or use a provider-supported coordination mechanism with explicit guarantees.", "Exercise concurrent startup against a disposable target and verify the deployment orchestrator's sequencing.", "The analyzer does not claim a failure will occur; actual behavior depends on provider locking, EF version, orchestration, and timing.", "supplied", [deployment_instances, *[item.sha256 for item, _ in runtime_hits]])
        else:
            builder.add("runtime.startup-migrate", pseudo_ops, "; ".join(f"{item.path}@{item.sha256[:12]}" for item, _ in runtime_hits), "Explicit runtime code applies EF migrations during application startup.", "Prefer a single controlled migration step for production and document startup ordering if runtime application is retained.", "Validate deployment sequencing and startup behavior on the target platform.", "Concurrency is unknown unless deployment instance count/topology is supplied; startup migration alone is not treated as a guaranteed failure.", "observed", [deployment_instances, *[item.sha256 for item, _ in runtime_hits]])

    table_to_ops: Dict[str, List[Operation]] = defaultdict(list)
    for op in up_ops:
        if op.table and op.op != "CreateTableColumn":
            table_to_ops[op.table].append(op)
    for table, ops in sorted(table_to_ops.items()):
        if len({o.file for o in ops}) > 1 and not any(o.op in ("DropTable", "RenameTable") for o in ops):
            builder.add("hotspot.same-table", ops[:12], evidence_for_ops(ops[:12]), "Multiple changed migrations touch the same table.", "Review the recorded order and consolidate only when the changes are inseparable.", "Generate the ordered SQL and inspect it as one upgrade path.", "Sharing a table is not itself a conflict; this is an integration hotspot signal.", "inferred", [table])

    patterns: Dict[str, Any] = {"expand_contract_candidates": []}
    raw_positions = [o for o in ordered_up if o.op == "Sql"]
    for table in sorted(set(adds_by_table) & set(drops_by_table)):
        adds = sorted(adds_by_table[table], key=operation_position)
        drops = sorted(drops_by_table[table], key=operation_position)
        backfills = [o for o in raw_positions if any(operation_position(a) < operation_position(o) < operation_position(d) for a in adds for d in drops)]
        if backfills:
            patterns["expand_contract_candidates"].append({
                "table": table,
                "add_operation_ids": [o.id for o in adds],
                "backfill_operation_ids": [o.id for o in backfills],
                "drop_operation_ids": [o.id for o in drops],
                "confidence": "low",
                "evidence_status": "inferred",
                "uncertainty": "The sequence resembles expand/backfill/contract, but consumer compatibility and semantic column mapping are not proven by static source parsing."
            })

    return builder.values(), patterns


def make_input_identity(
    file_ids: Sequence[FileIdentity],
    generated_sql_ids: Sequence[FileIdentity],
    runtime_ids: Sequence[FileIdentity],
    git_identity: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    payload = {
        "files": [asdict(item) for item in sorted(file_ids, key=lambda x: (x.role, x.path, x.sha256))],
        "generated_sql": [asdict(item) for item in sorted(generated_sql_ids, key=lambda x: x.path)],
        "runtime_code": [asdict(item) for item in sorted(runtime_ids, key=lambda x: x.path)],
        "git": None if git_identity is None else {
            "base_requested": git_identity.get("base_requested"),
            "base_sha": git_identity.get("base_sha"),
            "head_sha": git_identity.get("head_sha"),
            "merge_base_sha": git_identity.get("merge_base_sha"),
            "changed_files": git_identity.get("changed_files", []),
        },
    }
    return {"digest": sha256_text(canonical_json(payload)), **payload}


def build_gates(findings: Sequence[Finding]) -> List[Dict[str, Any]]:
    groups: Dict[str, List[str]] = defaultdict(list)
    for finding in findings:
        if finding.gate != "none":
            groups[finding.gate].append(finding.id)
    order = ["block", "review-required", "manual-review"]
    return [{"gate": gate, "status": "triggered", "finding_ids": sorted(groups[gate])} for gate in order if groups.get(gate)]


def build_summary(findings: Sequence[Finding]) -> Dict[str, Any]:
    counts = {severity: sum(1 for f in findings if f.severity == severity) for severity in SEVERITY_ORDER}
    if any(f.gate == "block" for f in findings):
        decision = "block"
    elif counts["high"]:
        decision = "changes-required"
    elif counts["medium"]:
        decision = "review-required"
    else:
        decision = "no-static-blocker"
    return {
        "total_findings": len(findings),
        "by_severity": counts,
        "decision": decision,
        "decision_basis": "Derived only from the frozen static heuristic set; runtime safety is not guaranteed by this decision."
    }


def build_report(
    files: List[Path],
    support_files: List[Path],
    notes: List[str],
    operations: List[Operation],
    metadata: List[Dict[str, Any]],
    findings: List[Finding],
    patterns: Dict[str, Any],
    heuristic_set: Dict[str, Any],
    heuristic_hash: str,
    input_identity: Dict[str, Any],
    git_identity: Optional[Dict[str, Any]],
    provider: Optional[str],
    dbcontext: Optional[str],
    deployment_instances: str,
) -> Dict[str, Any]:
    context = {
        "provider": provider,
        "dbcontext": dbcontext,
        "deployment_instances": deployment_instances,
    }
    analysis_identity_payload = {
        "analysis_version": ANALYSIS_VERSION,
        "heuristic_set_sha256": heuristic_hash,
        "input_digest": input_identity["digest"],
        "context": context,
    }
    analysis_id = "analysis-" + sha256_text(canonical_json(analysis_identity_payload))[:24]
    summary = build_summary(findings)
    report: Dict[str, Any] = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "analysis_version": ANALYSIS_VERSION,
        "analysis_id": analysis_id,
        "heuristic_set": {
            "name": heuristic_set["set_name"],
            "version": heuristic_set["version"],
            "sha256": heuristic_hash,
            "path": "references/heuristic-set.json",
        },
        "input_identity": input_identity,
        "git_identity": git_identity or {},
        "context": context,
        "scope": {
            "migration_files_analyzed": [logical_path(p, Path(git_identity["repository_root"]) if git_identity else None) for p in files],
            "support_files_observed": [logical_path(p, Path(git_identity["repository_root"]) if git_identity else None) for p in support_files],
            "notes": notes,
        },
        "metadata": metadata,
        "operations": [asdict(op) for op in sorted(operations, key=lambda o: (o.migration_order, o.method != "Up", o.ordinal, o.id))],
        "patterns": patterns,
        "findings": [asdict(f) for f in findings],
        "gates": build_gates(findings),
        "summary": summary,
        "limitations": [
            "Static C# parsing uses deterministic brace/regex extraction; it does not compile C# or execute custom migration helpers.",
            "Raw SQL heuristics do not prove provider-specific correctness, idempotency, lock behavior, or transaction semantics.",
            "Destructive-operation findings identify source operations; they do not assert data exists or consumers still depend on the object.",
            "Runtime deployment hazards are emitted only when explicit runtime code/deployment evidence is supplied; absence of a finding is not proof of safe rollout.",
            "Generated SQL is identity-tracked when supplied but is not semantically executed by this analyzer."
        ],
    }
    core_hash = sha256_text(canonical_json(report))
    report["analysis_receipt"] = {
        "receipt_version": 1,
        "status": "complete",
        "stage": "analysis",
        "analysis_id": analysis_id,
        "analysis_core_sha256": core_hash,
        "input_digest": input_identity["digest"],
        "heuristic_set_sha256": heuristic_hash,
        "finding_ids": [f.id for f in findings],
        "counts": summary["by_severity"],
    }
    return report


def render_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = ["# EF Core Migration Conflict Report", ""]
    lines += [
        "## Identity",
        f"- analysis id: `{report['analysis_id']}`",
        f"- analyzer version: `{report['analysis_version']}`",
        f"- heuristic set: `{report['heuristic_set']['version']}` @ `{report['heuristic_set']['sha256']}`",
        f"- input digest: `{report['input_identity']['digest']}`",
    ]
    git_id = report.get("git_identity") or {}
    if git_id:
        lines += [
            f"- git base: `{git_id.get('base_requested')}` -> `{git_id.get('base_sha')}`",
            f"- head SHA: `{git_id.get('head_sha')}`",
            f"- merge-base SHA: `{git_id.get('merge_base_sha')}`",
        ]
    lines += ["", "## Scope", f"- migration files analyzed: {len(report['scope']['migration_files_analyzed'])}"]
    for path in report["scope"]["migration_files_analyzed"]:
        lines.append(f"  - `{path}`")
    if report["scope"]["support_files_observed"]:
        lines.append("- support files observed:")
        for path in report["scope"]["support_files_observed"]:
            lines.append(f"  - `{path}`")
    lines += ["", "## Executive summary", f"- total findings: {report['summary']['total_findings']}"]
    for severity in ("critical", "high", "medium", "low", "info"):
        count = report["summary"]["by_severity"].get(severity, 0)
        if count:
            lines.append(f"- {severity}: {count}")
    lines.append(f"- static decision: `{report['summary']['decision']}`")
    lines.append(f"- basis: {report['summary']['decision_basis']}")
    if report["findings"]:
        lines += ["", "## Findings"]
        for finding in report["findings"]:
            lines += [
                "",
                f"### {finding['severity'].upper()}: {finding['title']}",
                f"- Finding ID: `{finding['id']}`",
                f"- Rule: `{finding['rule_id']}`",
                f"- Confidence / evidence: `{finding['confidence']}` / `{finding['evidence_status']}`",
                f"- Gate: `{finding['gate']}`",
                f"- Evidence: {finding['evidence']}",
                f"- Why it matters: {finding['why']}",
                f"- Smallest safe fix: {finding['recommendation']}",
                f"- Validation: {finding['validation']}",
                f"- Uncertainty: {finding['uncertainty']}",
            ]
    else:
        lines += ["", "No conflicts or review hazards were emitted by the frozen static heuristic set."]
    if report["patterns"]["expand_contract_candidates"]:
        lines += ["", "## Expand/contract signals"]
        for item in report["patterns"]["expand_contract_candidates"]:
            lines.append(f"- `{item['table']}`: candidate sequence; confidence `{item['confidence']}`. {item['uncertainty']}")
    lines += ["", "## Validation limits"]
    for item in report["limitations"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def fsync_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def resolved_collision(paths: Sequence[Path]) -> Optional[Tuple[Path, Path]]:
    resolved: List[Tuple[Path, Path]] = []
    for path in paths:
        resolved.append((path, path.resolve(strict=False)))
    for idx, (raw_a, resolved_a) in enumerate(resolved):
        for raw_b, resolved_b in resolved[idx + 1:]:
            if resolved_a == resolved_b:
                return raw_a, raw_b
            if raw_a.exists() and raw_b.exists():
                try:
                    if os.path.samefile(raw_a, raw_b):
                        return raw_a, raw_b
                except OSError:
                    pass
    return None


def deliver(rendered: str, output: Optional[str], receipt_path: Optional[str], report: Dict[str, Any], protected_inputs: Sequence[Path], output_format: str) -> None:
    artifact_bytes = rendered.encode("utf-8")
    artifact_hash = sha256_bytes(artifact_bytes)
    if not output:
        sys.stdout.write(rendered)
        sys.stdout.flush()
        if receipt_path:
            receipt = {
                "receipt_version": 1,
                "status": "pass",
                "stage": "analysis-delivery",
                "analysis_id": report["analysis_id"],
                "input_digest": report["input_identity"]["digest"],
                "heuristic_set_sha256": report["heuristic_set"]["sha256"],
                "artifact": {"destination": "stdout", "format": output_format, "sha256": artifact_hash},
                "recovery": [],
            }
            target = Path(receipt_path)
            collision = resolved_collision([target, *protected_inputs])
            if collision:
                raise ValueError(f"receipt output aliases protected input: {collision[0]} == {collision[1]}")
            tmp = target.with_name(f".{target.name}.tmp-{os.getpid()}")
            fsync_write(tmp, (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8"))
            os.replace(tmp, target)
        return

    out = Path(output)
    receipt_target = Path(receipt_path) if receipt_path else None
    collision_paths = [out, *protected_inputs]
    if receipt_target:
        collision_paths.append(receipt_target)
    collision = resolved_collision(collision_paths)
    if collision:
        raise ValueError(f"output alias collision: {collision[0]} == {collision[1]}")

    out.parent.mkdir(parents=True, exist_ok=True)
    staged_out = out.with_name(f".{out.name}.tmp-{os.getpid()}")
    fsync_write(staged_out, artifact_bytes)
    staged_receipt: Optional[Path] = None
    receipt_obj: Optional[Dict[str, Any]] = None
    if receipt_target:
        receipt_target.parent.mkdir(parents=True, exist_ok=True)
        receipt_obj = {
            "receipt_version": 1,
            "status": "pass",
            "stage": "analysis-delivery",
            "analysis_id": report["analysis_id"],
            "input_digest": report["input_identity"]["digest"],
            "heuristic_set_sha256": report["heuristic_set"]["sha256"],
            "artifact": {"destination": out.resolve(strict=False).as_posix(), "format": output_format, "sha256": artifact_hash},
            "recovery": [],
        }
        staged_receipt = receipt_target.with_name(f".{receipt_target.name}.tmp-{os.getpid()}")
        fsync_write(staged_receipt, (json.dumps(receipt_obj, indent=2, sort_keys=True) + "\n").encode("utf-8"))

    backup_out = out.with_name(f".{out.name}.last-good-{os.getpid()}") if out.exists() else None
    backup_receipt = receipt_target.with_name(f".{receipt_target.name}.last-good-{os.getpid()}") if receipt_target and receipt_target.exists() else None
    recovery: List[str] = []
    try:
        if backup_out:
            os.replace(out, backup_out)
        if backup_receipt and receipt_target:
            os.replace(receipt_target, backup_receipt)
        os.replace(staged_out, out)
        if staged_receipt and receipt_target:
            os.replace(staged_receipt, receipt_target)
        if backup_out and backup_out.exists():
            backup_out.unlink()
        if backup_receipt and backup_receipt.exists():
            backup_receipt.unlink()
    except Exception:
        if out.exists() and backup_out:
            failed = out.with_name(f".{out.name}.failed-candidate-{os.getpid()}")
            shutil.copy2(out, failed)
            recovery.append(failed.as_posix())
            out.unlink()
        if backup_out and backup_out.exists():
            os.replace(backup_out, out)
        if receipt_target and receipt_target.exists() and backup_receipt:
            failed_receipt = receipt_target.with_name(f".{receipt_target.name}.failed-candidate-{os.getpid()}")
            shutil.copy2(receipt_target, failed_receipt)
            recovery.append(failed_receipt.as_posix())
            receipt_target.unlink()
        if backup_receipt and backup_receipt.exists() and receipt_target:
            os.replace(backup_receipt, receipt_target)
        if staged_out.exists():
            recovery.append(staged_out.as_posix())
        if staged_receipt and staged_receipt.exists():
            recovery.append(staged_receipt.as_posix())
        raise RuntimeError("atomic delivery failed; recovery paths: " + ", ".join(recovery))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze EF Core migration conflicts with reproducible input identity and versioned heuristics.")
    parser.add_argument("paths", nargs="*", help="Migration files/directories, or repository root when --git-base is used.")
    parser.add_argument("--git-base", help="Base ref for PR mode. The analyzer records resolved base/head/merge-base SHAs.")
    parser.add_argument("--include-support-files", action="store_true", help="Include ModelSnapshot/Designer files found under path inputs as supporting evidence.")
    parser.add_argument("--snapshot", action="append", default=[], help="Additional ModelSnapshot file to identity-track. Repeatable.")
    parser.add_argument("--generated-sql", action="append", default=[], help="Generated SQL artifact to hash and bind to the analysis. Repeatable.")
    parser.add_argument("--runtime-code", action="append", default=[], help="Runtime code file to scan for Database.Migrate/MigrateAsync evidence. Repeatable.")
    parser.add_argument("--deployment-instances", choices=("unknown", "single", "multiple"), default="unknown", help="Deployment topology evidence for runtime migration classification.")
    parser.add_argument("--provider", help="Optional EF Core provider identity for report context; no provider behavior is inferred from the name alone.")
    parser.add_argument("--dbcontext", help="Optional DbContext identity for report context.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", help="Report output path. Defaults to stdout.")
    parser.add_argument("--receipt", help="Optional standalone machine-readable analysis delivery receipt path.")
    args = parser.parse_args(argv)

    if not args.paths and not args.git_base and not args.snapshot:
        parser.error("provide at least one path, --git-base, or --snapshot")

    heuristic_set, heuristic_hash, _ = load_heuristic_set()
    git_identity: Optional[Dict[str, Any]] = None
    base_history: List[Dict[str, Any]] = []
    repo_root: Optional[Path] = None
    notes: List[str] = []
    if args.git_base:
        main_files, support_files, git_identity, base_history, git_notes, repo_root = collect_git_sources(args.paths or ["."], args.git_base)
        notes.extend(git_notes)
        for raw in args.snapshot:
            extra = Path(raw)
            if extra.exists() and extra not in support_files:
                support_files.append(extra)
    else:
        main_files, support_files, path_notes = collect_path_sources(args.paths or [], args.include_support_files, args.snapshot)
        notes.extend(path_notes)

    file_ids: List[FileIdentity] = []
    identities_by_resolved: Dict[Path, FileIdentity] = {}
    git_status_by_path = {item["path"]: item["status"] for item in (git_identity or {}).get("changed_files", [])}
    for path in sorted([*main_files, *support_files], key=lambda p: logical_path(p, repo_root)):
        logical = logical_path(path, repo_root)
        identity = make_file_identity(path, role_for_path(path), repo_root, git_status_by_path.get(logical))
        file_ids.append(identity)
        identities_by_resolved[path.resolve()] = identity

    generated_sql_ids: List[FileIdentity] = []
    generated_sql_paths: List[Path] = []
    for raw in args.generated_sql:
        path = Path(raw)
        if not path.exists():
            notes.append(f"generated SQL not found: {raw}")
            continue
        generated_sql_paths.append(path)
        generated_sql_ids.append(make_file_identity(path, "generated_sql", repo_root))

    runtime_ids: List[FileIdentity] = []
    runtime_sources: List[Tuple[FileIdentity, str]] = []
    runtime_paths: List[Path] = []
    for raw in args.runtime_code:
        path = Path(raw)
        if not path.exists():
            notes.append(f"runtime code not found: {raw}")
            continue
        runtime_paths.append(path)
        identity = make_file_identity(path, "runtime_code", repo_root)
        runtime_ids.append(identity)
        runtime_sources.append((identity, read_text(path)))

    sorted_main = sorted(main_files, key=lambda p: ((p.name[:14] if re.match(r"^\d{14}_", p.name) else ""), logical_path(p, repo_root)))
    operations: List[Operation] = []
    metadata: List[Dict[str, Any]] = []
    for order, path in enumerate(sorted_main, 1):
        identity = identities_by_resolved[path.resolve()]
        ops, meta = parse_file(path, identity, order)
        operations.extend(ops)
        metadata.append(meta)

    snapshot_ids = [item for item in file_ids if item.role == "model_snapshot"]
    findings, patterns = analyze(operations, metadata, heuristic_set, base_history, snapshot_ids, git_identity, runtime_sources, args.deployment_instances)
    input_identity = make_input_identity(file_ids, generated_sql_ids, runtime_ids, git_identity)
    report = build_report(main_files, support_files, notes, operations, metadata, findings, patterns, heuristic_set, heuristic_hash, input_identity, git_identity, args.provider, args.dbcontext, args.deployment_instances)

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n" if args.format == "json" else render_markdown(report)
    protected_inputs = [*main_files, *support_files, *generated_sql_paths, *runtime_paths]
    deliver(rendered, args.output, args.receipt, report, protected_inputs, args.format)
    return 2 if report["summary"]["decision"] == "block" else 0


if __name__ == "__main__":
    raise SystemExit(main())
