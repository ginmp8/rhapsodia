#!/usr/bin/env python3
"""
Static EF Core migration conflict analyzer.

This parser is intentionally conservative. It detects common EF Core migration
operations from C# source using brace matching and regex extraction; it does not
compile C# or understand arbitrary custom helper methods.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}

MAIN_MIGRATION_RE = re.compile(r"^\d{14}_.+\.cs$")
EXCLUDED_RE = re.compile(r"(\.Designer\.cs$|ModelSnapshot\.cs$)")
DDL_SQL_RE = re.compile(r"\b(create|alter|drop|truncate|merge|update|delete|insert|exec|execute)\b", re.I)


@dataclass
class Operation:
    file: str
    migration: str
    method: str
    op: str
    table: Optional[str] = None
    column: Optional[str] = None
    name: Optional[str] = None
    new_name: Optional[str] = None
    object_type: Optional[str] = None
    nullable: Optional[bool] = None
    has_default: bool = False
    raw: str = ""


@dataclass
class Finding:
    severity: str
    title: str
    files: List[str]
    evidence: str
    why: str
    recommendation: str
    validation: str


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def is_main_migration(path: Path) -> bool:
    name = path.name
    return bool(MAIN_MIGRATION_RE.match(name)) and not EXCLUDED_RE.search(name)


def migration_name(path: Path, text: str) -> str:
    m = re.search(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*Migration\b", text)
    if m:
        return m.group(1)
    return path.stem.split("_", 1)[-1]


def strip_comments(text: str) -> str:
    text = re.sub(r"//.*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return text


def extract_method_body(text: str, method_name: str) -> str:
    marker = re.search(r"protected\s+override\s+void\s+" + re.escape(method_name) + r"\s*\([^)]*\)\s*\{", text)
    if not marker:
        return ""
    start = marker.end() - 1
    depth = 0
    for idx in range(start, len(text)):
        ch = text[idx]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:idx]
    return text[start + 1:]


def find_invocations(body: str) -> List[Tuple[str, str]]:
    calls: List[Tuple[str, str]] = []
    token = "migrationBuilder."
    i = 0
    while True:
        start = body.find(token, i)
        if start < 0:
            break
        op_start = start + len(token)
        m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)(?:\s*<[^>]+>)?\s*\(", body[op_start:])
        if not m:
            i = op_start
            continue
        op = m.group(1)
        paren_start = op_start + m.end() - 1
        depth = 0
        in_string = False
        string_char = ""
        escape = False
        end = paren_start
        for j in range(paren_start, len(body)):
            ch = body[j]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == string_char:
                    in_string = False
                continue
            if ch in ("'", '"'):
                in_string = True
                string_char = ch
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    end = j
                    break
        args = body[paren_start + 1:end]
        calls.append((op, args))
        i = end + 1
    return calls


def named_string(args: str, key: str) -> Optional[str]:
    patterns = [
        rf"\b{re.escape(key)}\s*:\s*@?\"([^\"]*)\"",
        rf"\b{re.escape(key)}\s*=\s*@?\"([^\"]*)\"",
    ]
    for pattern in patterns:
        m = re.search(pattern, args, flags=re.S)
        if m:
            return m.group(1)
    return None


def first_positional_string(args: str) -> Optional[str]:
    m = re.search(r"^\s*@?\"([^\"]*)\"", args, flags=re.S)
    if m:
        return m.group(1)
    return None


def named_bool(args: str, key: str) -> Optional[bool]:
    m = re.search(rf"\b{re.escape(key)}\s*:\s*(true|false)", args, flags=re.I)
    if not m:
        return None
    return m.group(1).lower() == "true"


def has_named(args: str, key: str) -> bool:
    return re.search(rf"\b{re.escape(key)}\s*:", args) is not None


def extract_columns_from_create_table(args: str) -> List[Tuple[str, Optional[bool], bool]]:
    columns: List[Tuple[str, Optional[bool], bool]] = []
    for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*table\.Column(?:<[^>]+>)?\s*\((.*?)\)", args, flags=re.S):
        col_name = m.group(1)
        col_args = m.group(2)
        nullable = named_bool(col_args, "nullable")
        has_default_value = has_named(col_args, "defaultValue") or has_named(col_args, "defaultValueSql") or has_named(col_args, "computedColumnSql")
        columns.append((col_name, nullable, has_default_value))
    return columns


def parse_file(path: Path) -> Tuple[List[Operation], Dict[str, object]]:
    text = strip_comments(read_text(path))
    migration = migration_name(path, text)
    metadata = {
        "file": str(path),
        "migration": migration,
        "timestamp": path.name[:14] if re.match(r"^\d{14}_", path.name) else None,
        "class_name": migration,
        "has_up": bool(extract_method_body(text, "Up")),
        "has_down": bool(extract_method_body(text, "Down")),
    }
    operations: List[Operation] = []
    for method in ("Up", "Down"):
        body = extract_method_body(text, method)
        for op, args in find_invocations(body):
            op_lower = op.lower()
            table = named_string(args, "table") or named_string(args, "name") if op in ("CreateTable", "DropTable") else named_string(args, "table")
            column = named_string(args, "column") or named_string(args, "name") if op in ("AddColumn", "DropColumn", "AlterColumn", "RenameColumn") else named_string(args, "column")
            name = named_string(args, "name") or first_positional_string(args)
            new_name = named_string(args, "newName") or named_string(args, "newTable")
            nullable = named_bool(args, "nullable")
            has_default_value = has_named(args, "defaultValue") or has_named(args, "defaultValueSql") or has_named(args, "computedColumnSql")
            if op == "CreateTable":
                create_table = named_string(args, "name") or first_positional_string(args)
                operations.append(Operation(str(path), migration, method, op, table=create_table, name=create_table, object_type="table", raw=args[:500]))
                for col_name, col_nullable, col_has_default in extract_columns_from_create_table(args):
                    operations.append(Operation(str(path), migration, method, "CreateTableColumn", table=create_table, column=col_name, name=col_name, object_type="column", nullable=col_nullable, has_default=col_has_default, raw=args[:500]))
                continue
            if op == "DropTable":
                drop_table = named_string(args, "name") or first_positional_string(args)
                operations.append(Operation(str(path), migration, method, op, table=drop_table, name=drop_table, object_type="table", raw=args[:500]))
                continue
            if op == "RenameTable":
                old_table = named_string(args, "name") or first_positional_string(args)
                operations.append(Operation(str(path), migration, method, op, table=old_table, name=old_table, new_name=new_name, object_type="table", raw=args[:500]))
                continue
            if op == "Sql":
                sql_text = first_positional_string(args) or args[:300]
                operations.append(Operation(str(path), migration, method, op, name="raw_sql", object_type="sql", raw=sql_text[:500]))
                continue
            object_type = "object"
            if op in ("AddColumn", "DropColumn", "AlterColumn", "RenameColumn"):
                object_type = "column"
            elif op in ("CreateIndex", "DropIndex"):
                object_type = "index"
            elif op in ("AddForeignKey", "DropForeignKey"):
                object_type = "foreign_key"
            elif op in ("AddPrimaryKey", "DropPrimaryKey"):
                object_type = "primary_key"
            elif op in ("AddUniqueConstraint", "DropUniqueConstraint"):
                object_type = "unique_constraint"
            elif op in ("AddCheckConstraint", "DropCheckConstraint"):
                object_type = "check_constraint"
            operations.append(Operation(str(path), migration, method, op, table=table, column=column, name=name, new_name=new_name, object_type=object_type, nullable=nullable, has_default=has_default_value, raw=args[:500]))
    return operations, metadata


def collect_paths(paths: Sequence[str], git_base: Optional[str]) -> Tuple[List[Path], List[str]]:
    notes: List[str] = []
    candidates: List[Path] = []
    if git_base:
        cmd = ["git", "diff", "--name-only", "--diff-filter=AMR", f"{git_base}...HEAD"]
        try:
            proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
            for line in proc.stdout.splitlines():
                p = Path(line.strip())
                if p.exists():
                    candidates.append(p)
            notes.append(f"git diff source: {' '.join(cmd)}")
        except Exception as exc:
            notes.append(f"git diff failed: {exc}")
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            candidates.extend(x for x in p.rglob("*.cs"))
        elif p.exists():
            candidates.append(p)
        else:
            notes.append(f"path not found: {raw}")
    seen = set()
    files: List[Path] = []
    for p in candidates:
        try:
            rp = p.resolve()
        except Exception:
            rp = p
        if rp in seen:
            continue
        seen.add(rp)
        if is_main_migration(p):
            files.append(p)
    return files, notes


def add_finding(findings: List[Finding], severity: str, title: str, ops: Sequence[Operation], why: str, recommendation: str, validation: str) -> None:
    files = sorted({op.file for op in ops})
    evidence_bits = []
    for op in ops[:5]:
        target = op.table or op.name or op.object_type or "unknown"
        if op.column:
            target = f"{target}.{op.column}"
        evidence_bits.append(f"{Path(op.file).name}:{op.migration}.{op.op}({target})")
    findings.append(Finding(severity, title, files, "; ".join(evidence_bits), why, recommendation, validation))


def analyze(operations: List[Operation], metadata: List[Dict[str, object]]) -> List[Finding]:
    findings: List[Finding] = []
    up_ops = [op for op in operations if op.method == "Up"]

    # duplicate migration metadata
    by_timestamp = defaultdict(list)
    by_class = defaultdict(list)
    for meta in metadata:
        if meta.get("timestamp"):
            by_timestamp[meta["timestamp"]].append(meta)
        if meta.get("class_name"):
            by_class[meta["class_name"]].append(meta)
        if not meta.get("has_up"):
            findings.append(Finding("high", "migration has no Up() body", [str(meta["file"])], str(meta), "EF cannot apply schema changes that are absent or hidden from the standard migration method.", "Regenerate or repair the migration so operations are explicit in Up().", "Run dotnet ef migrations script and compile the project."))
        if not meta.get("has_down"):
            findings.append(Finding("low", "migration has no Down() body", [str(meta["file"])], str(meta), "Rollback may not be possible or may be opaque during incident response.", "Add a safe Down() implementation or document why rollback is intentionally unsupported.", "Review rollback script generation."))
    for timestamp, metas in by_timestamp.items():
        if len(metas) > 1:
            ops = [Operation(str(m["file"]), str(m["migration"]), "meta", "MigrationId", name=str(timestamp)) for m in metas]
            add_finding(findings, "critical", f"duplicate migration timestamp {timestamp}", ops, "EF migration IDs must be unique and chronologically ordered. Duplicate IDs can corrupt history or make ordering ambiguous.", "Regenerate one migration with a unique timestamp after rebasing on the latest branch.", "Run dotnet ef migrations list and inspect __EFMigrationsHistory in target environments.")
    for cls, metas in by_class.items():
        if len(metas) > 1:
            ops = [Operation(str(m["file"]), str(m["migration"]), "meta", "MigrationClass", name=str(cls)) for m in metas]
            add_finding(findings, "critical", f"duplicate migration class {cls}", ops, "Duplicate migration classes can fail compilation or confuse migration discovery.", "Rename/regenerate one migration and validate the project builds.", "Run dotnet build and dotnet ef migrations list.")

    created_tables = {(op.table, op.file) for op in up_ops if op.op == "CreateTable" and op.table}
    tables_created_any = {op.table for op in up_ops if op.op == "CreateTable" and op.table}

    # duplicate object creation
    def group_by_key(filter_ops: Iterable[Operation], key_fn):
        groups = defaultdict(list)
        for op in filter_ops:
            key = key_fn(op)
            if key and all(key):
                groups[key].append(op)
        return groups

    for (table, column), ops in group_by_key((o for o in up_ops if o.op == "AddColumn"), lambda o: (o.table, o.column)).items():
        if len({o.file for o in ops}) > 1:
            add_finding(findings, "critical", f"duplicate AddColumn for {table}.{column}", ops, "The second migration normally fails because the column already exists, or a manual partial apply can desynchronize migration history.", "Merge the duplicate column addition into one migration or regenerate the later branch migration after rebase.", "Generate an idempotent SQL script and apply it to a clean database and an upgraded database.")

    for table, ops in group_by_key((o for o in up_ops if o.op == "CreateTable"), lambda o: (o.table,)).items():
        if len({o.file for o in ops}) > 1:
            add_finding(findings, "critical", f"duplicate CreateTable for {table[0]}", ops, "The second table creation normally fails because the table already exists.", "Keep one table creation migration and regenerate dependent migrations.", "Run dotnet ef migrations script from an empty database baseline.")

    for name, ops in group_by_key((o for o in up_ops if o.op in ("CreateIndex", "AddForeignKey", "AddPrimaryKey", "AddUniqueConstraint", "AddCheckConstraint") and o.name), lambda o: (o.op, o.name)).items():
        if len({o.file for o in ops}) > 1:
            add_finding(findings, "critical", f"duplicate {name[0]} name {name[1]}", ops, "Database object names must be unique within their provider-specific scope.", "Rename one object or consolidate the operations.", "Generate provider-specific SQL and verify object names.")

    # table drops/renames with other operations
    for drop in [o for o in up_ops if o.op == "DropTable" and o.table]:
        related = [o for o in up_ops if o is not drop and o.table == drop.table]
        if related:
            add_finding(findings, "critical", f"DropTable conflicts with other operations on {drop.table}", [drop] + related, "A migration drops a table while another changed migration still touches it.", "Split into expand-contract releases or remove dependent operations from the same PR.", "Apply generated SQL to an upgraded database copy.")

    for ren in [o for o in up_ops if o.op == "RenameTable" and o.table]:
        related = [o for o in up_ops if o is not ren and (o.table == ren.table or (ren.new_name and o.table == ren.new_name))]
        if related:
            add_finding(findings, "high", f"RenameTable order dependency for {ren.table}", [ren] + related, "Other operations touch the old or new table name and may fail if ordered incorrectly.", "Keep rename and dependent operations in one migration or make order explicit after rebase.", "Generate SQL and verify operation order.")

    # column drops/renames with other operations
    for drop in [o for o in up_ops if o.op == "DropColumn" and o.table and o.column]:
        related = [o for o in up_ops if o is not drop and o.table == drop.table and o.column == drop.column]
        if related:
            add_finding(findings, "high", f"DropColumn conflicts with other operations on {drop.table}.{drop.column}", [drop] + related, "A column is dropped while another operation still references it.", "Use expand-contract or remove the dependency before dropping the column.", "Run generated SQL against an upgraded database copy.")

    for ren in [o for o in up_ops if o.op == "RenameColumn" and o.table and o.name]:
        old_col = ren.name
        new_col = ren.new_name
        related = [o for o in up_ops if o is not ren and o.table == ren.table and (o.column == old_col or (new_col and o.column == new_col) or o.name == old_col or (new_col and o.name == new_col))]
        if related:
            add_finding(findings, "high", f"RenameColumn order dependency for {ren.table}.{old_col}", [ren] + related, "Other operations touch the old or new column name and may fail depending on migration order.", "Place rename and dependent operations in one migration or regenerate migrations after rebase.", "Inspect generated SQL order and run it on an upgraded database copy.")

    # unsafe rename heuristic: drop/add in same table, same file or same PR
    drops_by_table = defaultdict(list)
    adds_by_table = defaultdict(list)
    for op in up_ops:
        if op.op == "DropColumn" and op.table:
            drops_by_table[op.table].append(op)
        if op.op == "AddColumn" and op.table:
            adds_by_table[op.table].append(op)
    for table, drops in drops_by_table.items():
        adds = adds_by_table.get(table, [])
        if drops and adds:
            severity = "high" if any(d.file == a.file for d in drops for a in adds) else "medium"
            add_finding(findings, severity, f"drop/add column pattern on {table}", drops + adds, "This can be an unsafe rename pattern that loses data if EF scaffolded a drop plus add instead of RenameColumn/backfill.", "Replace with RenameColumn when it is a rename, or add explicit backfill before dropping source columns.", "Review generated SQL and verify data preservation on a copy.")

    # repeated alter column
    for (table, column), ops in group_by_key((o for o in up_ops if o.op == "AlterColumn"), lambda o: (o.table, o.name or o.column)).items():
        if len({o.file for o in ops}) > 1:
            add_finding(findings, "medium", f"multiple AlterColumn operations for {table}.{column}", ops, "Repeated column alterations across migrations can depend on order and provider-specific conversion rules.", "Consolidate the final desired column shape or document the staged transition.", "Generate SQL and test with representative existing data.")

    # non-null add without default on existing table
    for op in [o for o in up_ops if o.op == "AddColumn" and o.nullable is False and not o.has_default]:
        table_created_same_file = (op.table, op.file) in created_tables
        if not table_created_same_file and op.table not in tables_created_any:
            add_finding(findings, "high", f"NOT NULL AddColumn without default/backfill for {op.table}.{op.column}", [op], "Adding a required column to an existing populated table can fail because existing rows have no value.", "Add the column nullable first, add a default/backfill, or split the NOT NULL constraint into a later migration.", "Apply generated SQL to a database copy with existing rows.")

    # unique index risk
    for op in [o for o in up_ops if o.op == "CreateIndex" and "unique: true" in op.raw]:
        add_finding(findings, "medium", f"unique index requires existing data validation: {op.name}", [op], "Unique index creation can fail if existing rows contain duplicates.", "Run a duplicate-detection query or backfill/clean data before creating the unique index.", "Validate against production-like data before deploy.")

    # raw SQL risks
    for op in [o for o in up_ops if o.op == "Sql"]:
        if DDL_SQL_RE.search(op.raw):
            add_finding(findings, "medium", "raw SQL contains DDL or data mutation", [op], "Raw SQL is opaque to EF's model diff and static parsing; it may be non-idempotent or depend on operation order.", "Review provider-specific SQL, make it idempotent when possible, and keep dependent schema operations nearby.", "Generate final SQL and apply it to clean and upgraded database copies.")
        else:
            add_finding(findings, "low", "raw SQL requires manual review", [op], "The analyzer cannot prove whether custom SQL is safe.", "Document the intent and test provider-specific execution.", "Inspect generated SQL.")

    # same table hotspot warning for disjoint additions/changes
    table_to_files = defaultdict(list)
    for op in up_ops:
        if op.table and op.op not in ("CreateTableColumn",):
            table_to_files[op.table].append(op)
    for table, ops in table_to_files.items():
        files = {o.file for o in ops}
        op_names = {o.op for o in ops}
        if len(files) > 1 and not any(o.op in ("DropTable", "RenameTable") for o in ops):
            # Avoid duplicating obvious critical duplicate cases; still useful as PR hotspot.
            add_finding(findings, "low", f"multiple migrations touch table {table}", ops[:8], "This is not automatically a conflict, but it is a PR integration and deployment hotspot, especially with runtime migration application.", "Review operation order, consider consolidating closely related changes, and apply migrations once in deployment rather than from every app instance.", "Generate an idempotent SQL script and inspect order.")

    findings.sort(key=lambda f: (-SEVERITY_ORDER.get(f.severity, 0), f.title))
    return findings


def render_markdown(files: List[Path], notes: List[str], operations: List[Operation], metadata: List[Dict[str, object]], findings: List[Finding]) -> str:
    counts = defaultdict(int)
    for f in findings:
        counts[f.severity] += 1
    blocking = counts["critical"] > 0 or counts["high"] > 0
    lines = []
    lines.append("# EF Core Migration Conflict Report")
    lines.append("")
    lines.append("## Scope")
    lines.append(f"- migration files analyzed: {len(files)}")
    for p in files:
        lines.append(f"  - `{p}`")
    if notes:
        lines.append("- notes:")
        for note in notes:
            lines.append(f"  - {note}")
    lines.append("")
    lines.append("## Executive summary")
    lines.append(f"- total findings: {len(findings)}")
    for sev in ("critical", "high", "medium", "low", "info"):
        if counts[sev]:
            lines.append(f"- {sev}: {counts[sev]}")
    lines.append(f"- recommendation: {'block/request changes before merge or deploy' if blocking else 'no blocking findings from static analysis'}")
    lines.append("")
    if not findings:
        lines.append("No conflicts were detected by static analysis. This does not replace generated SQL review or provider-specific testing.")
    else:
        lines.append("## Findings")
        for idx, f in enumerate(findings, 1):
            lines.append("")
            lines.append(f"### {idx}. {f.severity.upper()}: {f.title}")
            lines.append(f"- Evidence: {f.evidence}")
            lines.append(f"- Files: {', '.join('`' + x + '`' for x in f.files)}")
            lines.append(f"- Why it matters: {f.why}")
            lines.append(f"- Smallest fix: {f.recommendation}")
            lines.append(f"- Validation: {f.validation}")
    lines.append("")
    lines.append("## Safe deployment notes")
    lines.append("- Prefer generated SQL scripts or migration bundles for production review and rollout.")
    lines.append("- Avoid applying migrations from every normal application instance at startup; use a single deployment job when possible.")
    lines.append("- Use expand-contract for rolling deployments and destructive changes.")
    lines.append("")
    lines.append("## Analyzer limits")
    lines.append("- This analyzer uses static parsing, not a C# compiler.")
    lines.append("- Provider-specific SQL, custom helper methods, conditional code, and data volume are not fully evaluated.")
    lines.append("- Review generated SQL before production deployment.")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze EF Core migration files for conflicts and deployment hazards.")
    parser.add_argument("paths", nargs="*", help="Migration files, directories, or repository root paths.")
    parser.add_argument("--git-base", help="Base ref for PR mode, e.g. origin/main. Uses git diff base...HEAD to discover changed files.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", help="Output file path. Defaults to stdout.")
    args = parser.parse_args(argv)

    if not args.paths and not args.git_base:
        parser.error("provide at least one path or --git-base")

    files, notes = collect_paths(args.paths or ["."], args.git_base)
    operations: List[Operation] = []
    metadata: List[Dict[str, object]] = []
    for path in files:
        ops, meta = parse_file(path)
        operations.extend(ops)
        metadata.append(meta)

    findings = analyze(operations, metadata)

    if args.format == "json":
        payload = {
            "files": [str(p) for p in files],
            "notes": notes,
            "metadata": metadata,
            "operations": [asdict(op) for op in operations],
            "findings": [asdict(f) for f in findings],
            "summary": {"total_findings": len(findings), "by_severity": {sev: sum(1 for f in findings if f.severity == sev) for sev in SEVERITY_ORDER}},
        }
        rendered = json.dumps(payload, indent=2, sort_keys=True)
    else:
        rendered = render_markdown(files, notes, operations, metadata, findings)

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return 2 if any(f.severity == "critical" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
