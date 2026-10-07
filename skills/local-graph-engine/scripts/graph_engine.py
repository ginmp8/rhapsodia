#!/usr/bin/env python3
"""Portable local graph engine backed by SQLite.

Stdlib-only baseline. The database is the source of truth. Agents and parsers submit
versioned GraphPatch documents; this script validates and applies them transactionally,
then exposes deterministic query and GraphView export operations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from collections import deque
from pathlib import Path
from typing import Any, Iterable

PACKAGE_VERSION = "2.1.0"
SCHEMA_VERSION = 1
PATCH_VERSION = "graph-patch-v1"
VIEW_VERSION = "graph-view-v1"
PROVENANCE = {"EXTRACTED", "DERIVED", "INFERRED", "MANUAL"}
EVIDENCE_STATUS = {"accepted", "ambiguous", "rejected", "stale"}
ACTIVE_EVIDENCE_STATUS = {"accepted", "ambiguous", "stale"}

SCHEMA_SQL = r"""
CREATE TABLE IF NOT EXISTS graph_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY,
  uri TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL,
  content_hash TEXT,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  indexed_at TEXT
);

CREATE TABLE IF NOT EXISTS nodes (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  label TEXT NOT NULL,
  properties_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS node_aliases (
  alias TEXT NOT NULL,
  node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  PRIMARY KEY (alias, node_id, source_id)
);

CREATE TABLE IF NOT EXISTS edges (
  id TEXT PRIMARY KEY,
  source_node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  target_node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  relation TEXT NOT NULL,
  directed INTEGER NOT NULL CHECK (directed IN (0, 1)),
  properties_json TEXT NOT NULL DEFAULT '{}',
  UNIQUE(source_node_id, target_node_id, relation, directed)
);

CREATE TABLE IF NOT EXISTS node_evidence (
  id TEXT PRIMARY KEY,
  node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  provenance TEXT NOT NULL CHECK (provenance IN ('EXTRACTED','DERIVED','INFERRED','MANUAL')),
  confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
  locator TEXT,
  status TEXT NOT NULL CHECK (status IN ('accepted','ambiguous','rejected','stale')),
  details_json TEXT NOT NULL DEFAULT '{}',
  UNIQUE(node_id, source_id, provenance, locator, status)
);

CREATE TABLE IF NOT EXISTS edge_evidence (
  id TEXT PRIMARY KEY,
  edge_id TEXT NOT NULL REFERENCES edges(id) ON DELETE CASCADE,
  source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  provenance TEXT NOT NULL CHECK (provenance IN ('EXTRACTED','DERIVED','INFERRED','MANUAL')),
  confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
  locator TEXT,
  status TEXT NOT NULL CHECK (status IN ('accepted','ambiguous','rejected','stale')),
  details_json TEXT NOT NULL DEFAULT '{}',
  UNIQUE(edge_id, source_id, provenance, locator, status)
);

CREATE TABLE IF NOT EXISTS analysis_runs (
  id TEXT PRIMARY KEY,
  algorithm TEXT NOT NULL,
  version TEXT,
  parameters_json TEXT NOT NULL DEFAULT '{}',
  input_hash TEXT,
  status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS node_metrics (
  run_id TEXT NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
  node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  metric TEXT NOT NULL,
  value REAL NOT NULL,
  PRIMARY KEY (run_id, node_id, metric)
);

CREATE TABLE IF NOT EXISTS communities (
  run_id TEXT NOT NULL REFERENCES analysis_runs(id) ON DELETE CASCADE,
  id TEXT NOT NULL,
  label TEXT,
  properties_json TEXT NOT NULL DEFAULT '{}',
  PRIMARY KEY (run_id, id)
);

CREATE TABLE IF NOT EXISTS community_members (
  run_id TEXT NOT NULL,
  community_id TEXT NOT NULL,
  node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
  PRIMARY KEY (run_id, community_id, node_id),
  FOREIGN KEY (run_id, community_id) REFERENCES communities(run_id, id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_node_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_node_id);
CREATE INDEX IF NOT EXISTS idx_edges_relation ON edges(relation);
CREATE INDEX IF NOT EXISTS idx_node_evidence_node ON node_evidence(node_id);
CREATE INDEX IF NOT EXISTS idx_node_evidence_source ON node_evidence(source_id);
CREATE INDEX IF NOT EXISTS idx_edge_evidence_edge ON edge_evidence(edge_id);
CREATE INDEX IF NOT EXISTS idx_edge_evidence_source ON edge_evidence(source_id);
CREATE INDEX IF NOT EXISTS idx_alias_lookup ON node_aliases(alias);

CREATE VIEW IF NOT EXISTS active_edges AS
SELECT e.*
FROM edges e
WHERE EXISTS (
  SELECT 1 FROM edge_evidence ee
  WHERE ee.edge_id = e.id AND ee.status IN ('accepted','ambiguous','stale')
);

CREATE VIEW IF NOT EXISTS active_nodes AS
SELECT n.*
FROM nodes n
WHERE EXISTS (
  SELECT 1 FROM node_evidence ne
  WHERE ne.node_id = n.id AND ne.status IN ('accepted','ambiguous','stale')
)
OR EXISTS (SELECT 1 FROM active_edges ae WHERE ae.source_node_id = n.id OR ae.target_node_id = n.id);
"""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_id(prefix: str, *parts: Any, length: int = 24) -> str:
    payload = canonical_json(parts)
    return f"{prefix}:{sha256_text(payload)[:length]}"


def source_id(uri: str) -> str:
    return stable_id("source", uri)


def edge_id(source: str, target: str, relation: str, directed: bool) -> str:
    return stable_id("edge", source, target, relation, bool(directed))


def evidence_id(kind: str, entity_id: str, src_id: str, evidence: dict[str, Any]) -> str:
    return stable_id(
        "ev",
        kind,
        entity_id,
        src_id,
        evidence.get("provenance"),
        evidence.get("confidence"),
        evidence.get("locator"),
        evidence.get("status"),
        evidence.get("details", {}),
    )


def normalized_indexed_at(source: dict[str, Any]) -> str | None:
    supplied = source.get("indexed_at")
    if supplied is not None:
        return str(supplied)
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch:
        try:
            import datetime as _dt

            return _dt.datetime.fromtimestamp(int(epoch), tz=_dt.timezone.utc).isoformat().replace("+00:00", "Z")
        except Exception:
            return None
    return None


def connect(db_path: Path, *, create: bool = False) -> sqlite3.Connection:
    if not create and not db_path.exists():
        raise FileNotFoundError(f"database does not exist: {db_path}")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA busy_timeout=5000")
    try:
        from graph_journal import guard_writer
        guard_writer(con)
    except Exception:
        con.close()
        raise
    return con


def init_db(db_path: Path) -> dict[str, Any]:
    if db_path.exists():
        probe = sqlite3.connect(str(db_path))
        try:
            version = probe.execute("PRAGMA user_version").fetchone()[0]
            tables = probe.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            if (tables and version != SCHEMA_VERSION) or version not in (0, SCHEMA_VERSION):
                raise ValueError("refusing to initialize an unrelated or newer database")
            if tables and not probe.execute("SELECT 1 FROM sqlite_master WHERE name='graph_meta'").fetchone():
                raise ValueError("refusing to initialize a non-graph database")
        finally:
            probe.close()
    con = connect(db_path, create=True)
    try:
        mode = con.execute("PRAGMA journal_mode").fetchone()[0]
        con.executescript(SCHEMA_SQL)
        con.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
        con.execute(
            "INSERT INTO graph_meta(key,value) VALUES('schema_version',?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (str(SCHEMA_VERSION),),
        )
        con.execute(
            "INSERT INTO graph_meta(key,value) VALUES('graph_contract',?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ("local-graph-sqlite-v1",),
        )
        fts = ensure_fts(con)
        con.commit()
        return {"status": "pass", "db": str(db_path), "schema_version": SCHEMA_VERSION, "journal_mode": mode, "fts5": fts}
    finally:
        con.close()


def ensure_fts(con: sqlite3.Connection) -> bool:
    try:
        con.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS node_search USING fts5(node_id UNINDEXED, label, kind, aliases)"
        )
        return True
    except sqlite3.OperationalError:
        return False


def rebuild_fts(con: sqlite3.Connection) -> bool:
    if not ensure_fts(con):
        return False
    con.execute("DELETE FROM node_search")
    rows = con.execute(
        """
        SELECT n.id, n.label, n.kind, COALESCE(group_concat(na.alias, ' '), '') aliases
        FROM active_nodes n
        LEFT JOIN node_aliases na ON na.node_id=n.id
        GROUP BY n.id, n.label, n.kind
        ORDER BY n.id
        """
    ).fetchall()
    con.executemany(
        "INSERT INTO node_search(node_id,label,kind,aliases) VALUES(?,?,?,?)",
        [(r["id"], r["label"], r["kind"], r["aliases"]) for r in rows],
    )
    return True


def require_nonempty_str(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: expected non-empty string")


def validate_evidence(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{path}: expected a non-empty evidence array")
        return
    for i, ev in enumerate(value):
        p = f"{path}[{i}]"
        if not isinstance(ev, dict):
            errors.append(f"{p}: expected object")
            continue
        if ev.get("provenance") not in PROVENANCE:
            errors.append(f"{p}.provenance: expected one of {sorted(PROVENANCE)}")
        confidence = ev.get("confidence")
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= float(confidence) <= 1:
            errors.append(f"{p}.confidence: expected number in [0,1]")
        if ev.get("status") not in EVIDENCE_STATUS:
            errors.append(f"{p}.status: expected one of {sorted(EVIDENCE_STATUS)}")
        if "locator" in ev and ev["locator"] is not None and not isinstance(ev["locator"], str):
            errors.append(f"{p}.locator: expected string or null")
        if "details" in ev and not isinstance(ev["details"], dict):
            errors.append(f"{p}.details: expected object")


def validate_patch_data(data: Any, existing_node_ids: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    from graph_common import finite_tree
    try:
        finite_tree(data)
    except ValueError as exc:
        return [str(exc)]
    if not isinstance(data, dict):
        return ["root: expected object"]
    if data.get("schema_version") != PATCH_VERSION:
        errors.append(f"schema_version: expected {PATCH_VERSION!r}")
    source = data.get("source")
    if not isinstance(source, dict):
        errors.append("source: expected object")
        source = {}
    require_nonempty_str(source.get("uri"), "source.uri", errors)
    require_nonempty_str(source.get("kind"), "source.kind", errors)
    if source.get("content_hash") is not None and not isinstance(source.get("content_hash"), str):
        errors.append("source.content_hash: expected string or null")
    if source.get("metadata") is not None and not isinstance(source.get("metadata"), dict):
        errors.append("source.metadata: expected object")

    nodes = data.get("nodes")
    edges = data.get("edges")
    if not isinstance(nodes, list):
        errors.append("nodes: expected array")
        nodes = []
    if not isinstance(edges, list):
        errors.append("edges: expected array")
        edges = []

    node_ids: set[str] = set()
    for i, node in enumerate(nodes):
        p = f"nodes[{i}]"
        if not isinstance(node, dict):
            errors.append(f"{p}: expected object")
            continue
        require_nonempty_str(node.get("id"), f"{p}.id", errors)
        require_nonempty_str(node.get("kind"), f"{p}.kind", errors)
        require_nonempty_str(node.get("label"), f"{p}.label", errors)
        if isinstance(node.get("id"), str):
            if node["id"] in node_ids:
                errors.append(f"{p}.id: duplicate node id {node['id']!r}")
            node_ids.add(node["id"])
        if node.get("properties") is not None and not isinstance(node.get("properties"), dict):
            errors.append(f"{p}.properties: expected object")
        aliases = node.get("aliases", [])
        if not isinstance(aliases, list) or any(not isinstance(a, str) or not a.strip() for a in aliases):
            errors.append(f"{p}.aliases: expected array of non-empty strings")
        validate_evidence(node.get("evidence"), f"{p}.evidence", errors)

    edge_keys: set[tuple[str, str, str, bool]] = set()
    known = set(existing_node_ids or set()) | node_ids
    for i, edge in enumerate(edges):
        p = f"edges[{i}]"
        if not isinstance(edge, dict):
            errors.append(f"{p}: expected object")
            continue
        if "id" in edge: require_nonempty_str(edge.get("id"), f"{p}.id", errors)
        require_nonempty_str(edge.get("source"), f"{p}.source", errors)
        require_nonempty_str(edge.get("target"), f"{p}.target", errors)
        require_nonempty_str(edge.get("relation"), f"{p}.relation", errors)
        directed = edge.get("directed", True)
        if not isinstance(directed, bool):
            errors.append(f"{p}.directed: expected boolean")
        if edge.get("properties") is not None and not isinstance(edge.get("properties"), dict):
            errors.append(f"{p}.properties: expected object")
        validate_evidence(edge.get("evidence"), f"{p}.evidence", errors)
        s, t, rel = edge.get("source"), edge.get("target"), edge.get("relation")
        if isinstance(s, str) and s not in known:
            errors.append(f"{p}.source: unknown node {s!r}")
        if isinstance(t, str) and t not in known:
            errors.append(f"{p}.target: unknown node {t!r}")
        if isinstance(s, str) and isinstance(t, str) and isinstance(rel, str) and isinstance(directed, bool):
            a, b = (s, t) if directed else tuple(sorted((s, t)))
            key = (a, b, rel, directed)
            if key in edge_keys:
                errors.append(f"{p}: duplicate canonical edge {key!r}")
            edge_keys.add(key)
    return errors


def load_json(path: Path) -> Any:
    from graph_common import read_json
    return read_json(path)


def validate_patch_file(db_path: Path | None, patch_path: Path) -> dict[str, Any]:
    data = load_json(patch_path)
    existing: set[str] = set()
    if db_path and db_path.exists():
        con = connect(db_path)
        try:
            existing = {r[0] for r in con.execute("SELECT id FROM nodes")}
        finally:
            con.close()
    errors = validate_patch_data(data, existing)
    return {"status": "pass" if not errors else "fail", "errors": errors, "patch": str(patch_path)}


def apply_patch(db_path: Path, patch_path: Path, *, prune_orphans: bool = True) -> dict[str, Any]:
    from graph_store import apply_patches
    from graph_common import read_json
    try:
        return apply_patches(db_path, [read_json(patch_path)], prune=prune_orphans)
    except (ValueError, TypeError, KeyError, sqlite3.Error) as exc:
        return {"status": "fail", "errors": [str(exc)], "mutated": False}


def evidence_sort_key(ev: dict[str, Any]) -> tuple[str, str, str, float, str]:
    return (
        str(ev.get("provenance", "")),
        str(ev.get("status", "")),
        str(ev.get("locator", "")),
        float(ev.get("confidence", 0.0)),
        canonical_json(ev.get("details", {})),
    )


def active_edge_rows(con: sqlite3.Connection, relation: str | None = None) -> list[sqlite3.Row]:
    if relation:
        return con.execute("SELECT * FROM active_edges WHERE relation=? ORDER BY id", (relation,)).fetchall()
    return con.execute("SELECT * FROM active_edges ORDER BY id").fetchall()


def adjacency_from_rows(rows: Iterable[sqlite3.Row]) -> tuple[dict[str, list[tuple[str, str]]], dict[str, list[tuple[str, str]]]]:
    outgoing: dict[str, list[tuple[str, str]]] = {}
    incoming: dict[str, list[tuple[str, str]]] = {}
    for r in rows:
        s, t, eid, directed = r["source_node_id"], r["target_node_id"], r["id"], bool(r["directed"])
        outgoing.setdefault(s, []).append((t, eid))
        incoming.setdefault(t, []).append((s, eid))
        if not directed:
            outgoing.setdefault(t, []).append((s, eid))
            incoming.setdefault(s, []).append((t, eid))
    for mapping in (outgoing, incoming):
        for key in mapping:
            mapping[key].sort(key=lambda x: (x[0], x[1]))
    return outgoing, incoming


def resolve_node(con: sqlite3.Connection, token: str) -> str:
    exact = con.execute("SELECT id FROM active_nodes WHERE id=?", (token,)).fetchone()
    if exact:
        return exact["id"]
    rows = con.execute(
        """
        SELECT DISTINCT n.id
        FROM active_nodes n
        LEFT JOIN node_aliases a ON a.node_id=n.id
        WHERE lower(n.label)=lower(?) OR lower(a.alias)=lower(?)
        ORDER BY n.id
        LIMIT 3
        """,
        (token, token),
    ).fetchall()
    if not rows:
        raise KeyError(f"node not found: {token}")
    if len(rows) > 1:
        raise KeyError(f"node token is ambiguous: {token}; matches {[r['id'] for r in rows]}")
    return rows[0]["id"]


def find_nodes(con: sqlite3.Connection, query: str, limit: int) -> list[dict[str, Any]]:
    rows: list[sqlite3.Row] = []
    try:
        rows = con.execute(
            """
            SELECT n.id,n.kind,n.label, bm25(node_search) rank
            FROM node_search s JOIN active_nodes n ON n.id=s.node_id
            WHERE node_search MATCH ?
            ORDER BY rank, n.id LIMIT ?
            """,
            (query, limit),
        ).fetchall()
    except sqlite3.OperationalError:
        pass
    if not rows:
        like = f"%{query.lower()}%"
        rows = con.execute(
            """
            SELECT DISTINCT n.id,n.kind,n.label,0.0 rank
            FROM active_nodes n LEFT JOIN node_aliases a ON a.node_id=n.id
            WHERE lower(n.id) LIKE ? OR lower(n.label) LIKE ? OR lower(a.alias) LIKE ?
            ORDER BY CASE WHEN lower(n.label)=lower(?) THEN 0 ELSE 1 END, n.label, n.id
            LIMIT ?
            """,
            (like, like, like, query, limit),
        ).fetchall()
    return [{"id": r["id"], "kind": r["kind"], "label": r["label"]} for r in rows]


def evidence_summary(con: sqlite3.Connection, kind: str, entity_id: str) -> dict[str, Any]:
    table, col = ("node_evidence", "node_id") if kind == "node" else ("edge_evidence", "edge_id")
    rows = con.execute(
        f"SELECT provenance,confidence,status FROM {table} WHERE {col}=? ORDER BY provenance,status,confidence DESC",
        (entity_id,),
    ).fetchall()
    active = [r for r in rows if r["status"] in ACTIVE_EVIDENCE_STATUS]
    return {
        "count": len(rows),
        "active_count": len(active),
        "provenance": sorted({r["provenance"] for r in rows}),
        "max_confidence": max((float(r["confidence"]) for r in active), default=None),
        "ambiguous_count": sum(1 for r in rows if r["status"] == "ambiguous"),
        "stale_count": sum(1 for r in rows if r["status"] == "stale"),
    }


def node_record(con: sqlite3.Connection, node_id: str) -> dict[str, Any]:
    row = con.execute("SELECT * FROM active_nodes WHERE id=?", (node_id,)).fetchone()
    if not row:
        raise KeyError(f"active node not found: {node_id}")
    aliases = [r[0] for r in con.execute("SELECT DISTINCT alias FROM node_aliases WHERE node_id=? ORDER BY alias", (node_id,))]
    degree = con.execute(
        """
        SELECT
          SUM(CASE WHEN target_node_id=? THEN 1 ELSE 0 END) AS incoming,
          SUM(CASE WHEN source_node_id=? THEN 1 ELSE 0 END) AS outgoing,
          COUNT(*) AS total
        FROM active_edges WHERE source_node_id=? OR target_node_id=?
        """,
        (node_id, node_id, node_id, node_id),
    ).fetchone()
    return {
        "id": row["id"],
        "kind": row["kind"],
        "label": row["label"],
        "properties": json.loads(row["properties_json"]),
        "aliases": aliases,
        "degree": {"in": int(degree["incoming"] or 0), "out": int(degree["outgoing"] or 0), "total": int(degree["total"] or 0)},
        "evidence_summary": evidence_summary(con, "node", node_id),
    }


def edge_record(con: sqlite3.Connection, row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "source": row["source_node_id"],
        "target": row["target_node_id"],
        "relation": row["relation"],
        "directed": bool(row["directed"]),
        "properties": json.loads(row["properties_json"]),
        "evidence_summary": evidence_summary(con, "edge", row["id"]),
    }


def bfs_path(con: sqlite3.Connection, start: str, goal: str, max_depth: int, undirected: bool, relation: str | None) -> dict[str, Any]:
    rows = active_edge_rows(con, relation)
    outgoing, incoming = adjacency_from_rows(rows)
    if start == goal:
        return {"nodes": [start], "edges": [], "hops": 0}
    q: deque[tuple[str, list[str], list[str]]] = deque([(start, [start], [])])
    seen = {start}
    while q:
        node, path_nodes, path_edges = q.popleft()
        if len(path_edges) >= max_depth:
            continue
        candidates = list(outgoing.get(node, []))
        if undirected:
            candidates += incoming.get(node, [])
        for nxt, eid in sorted(set(candidates), key=lambda x: (x[0], x[1])):
            if nxt in seen:
                continue
            n_nodes, n_edges = path_nodes + [nxt], path_edges + [eid]
            if nxt == goal:
                return {"nodes": n_nodes, "edges": n_edges, "hops": len(n_edges)}
            seen.add(nxt)
            q.append((nxt, n_nodes, n_edges))
    return {"nodes": [], "edges": [], "hops": None}


def reach(con: sqlite3.Connection, start: str, direction: str, depth: int, relation: str | None) -> dict[str, Any]:
    rows = active_edge_rows(con, relation)
    outgoing, incoming = adjacency_from_rows(rows)
    mapping = incoming if direction == "dependents" else outgoing
    distance = {start: 0}
    steps: list[list[str]] = [[] for _ in range(depth)]
    beyond = 0
    frontier = [start]
    d = 0
    while frontier:
        d += 1
        found: list[str] = []
        for node in sorted(frontier):
            for other, _eid in mapping.get(node, []):
                if other in distance:
                    continue
                distance[other] = d
                found.append(other)
        found = sorted(set(found))
        if d <= depth:
            steps[d - 1] = found
        else:
            beyond += len(found)
        frontier = found
    return {"direction": direction, "depth": depth, "steps": steps, "beyond": beyond}


def collect_subgraph(
    con: sqlite3.Connection,
    seed: str | None,
    direction: str,
    depth: int,
    relation: str | None,
    max_nodes: int,
) -> tuple[list[str], list[sqlite3.Row], bool]:
    rows = active_edge_rows(con, relation)
    if seed is None:
        node_ids = [r[0] for r in con.execute("SELECT id FROM active_nodes ORDER BY id")]
        if len(node_ids) > max_nodes:
            raise ValueError(f"graph has {len(node_ids)} active nodes; specify --seed or raise --max-nodes explicitly")
        return node_ids, rows, False

    outgoing, incoming = adjacency_from_rows(rows)
    q: deque[tuple[str, int]] = deque([(seed, 0)])
    seen = {seed}
    truncated = False
    while q:
        node, d = q.popleft()
        if d >= depth:
            continue
        if direction == "outgoing":
            candidates = outgoing.get(node, [])
        elif direction == "incoming":
            candidates = incoming.get(node, [])
        else:
            candidates = sorted(set(outgoing.get(node, []) + incoming.get(node, [])), key=lambda x: (x[0], x[1]))
        for nxt, _eid in candidates:
            if nxt in seen:
                continue
            if len(seen) >= max_nodes:
                truncated = True
                continue
            seen.add(nxt)
            q.append((nxt, d + 1))
    selected_rows = [r for r in rows if r["source_node_id"] in seen and r["target_node_id"] in seen]
    return sorted(seen), selected_rows, truncated


def latest_community_map(con: sqlite3.Connection, node_ids: set[str]) -> tuple[str | None, dict[str, str], list[dict[str, Any]]]:
    from graph_store import logical_hash
    pointer = con.execute("SELECT value FROM graph_meta WHERE key='current_analysis'").fetchone()
    if not pointer:
        return None, {}, []
    row = con.execute("SELECT id FROM analysis_runs WHERE id=? AND status='pass' AND input_hash=?", (pointer[0], logical_hash(con))).fetchone()
    if not row:
        return None, {}, []
    run_id = row[0]
    members = con.execute(
        """
        SELECT cm.node_id,cm.community_id,c.label
        FROM community_members cm JOIN communities c
        ON c.run_id=cm.run_id AND c.id=cm.community_id
        WHERE cm.run_id=? ORDER BY cm.community_id,cm.node_id
        """,
        (run_id,),
    ).fetchall()
    cmap: dict[str, str] = {}
    grouped: dict[str, dict[str, Any]] = {}
    for r in members:
        if r["node_id"] not in node_ids:
            continue
        cmap[r["node_id"]] = r["community_id"]
        g = grouped.setdefault(r["community_id"], {"id": r["community_id"], "label": r["label"], "nodes": []})
        g["nodes"].append(r["node_id"])
    return run_id, cmap, [grouped[k] for k in sorted(grouped)]


def export_view(
    con: sqlite3.Connection,
    db_path: Path,
    output: Path,
    seed_token: str | None,
    direction: str,
    depth: int,
    relation: str | None,
    max_nodes: int,
    layout_hint: str | None,
) -> dict[str, Any]:
    from graph_common import integer
    integer(depth, "depth", 0, 100)
    integer(max_nodes, "max_nodes", 1, 100000)
    seed = resolve_node(con, seed_token) if seed_token else None
    node_ids, rows, truncated = collect_subgraph(con, seed, direction, depth, relation, max_nodes)
    node_set = set(node_ids)
    run_id, cmap, communities = latest_community_map(con, node_set)
    nodes = []
    for node_id in node_ids:
        rec = node_record(con, node_id)
        rec["community"] = cmap.get(node_id)
        nodes.append(rec)
    edges = [edge_record(con, r) for r in rows]
    payload: dict[str, Any] = {
        "schema_version": VIEW_VERSION,
        "graph": {
            "contract": "local-graph-sqlite-v1",
            "node_count": len(nodes),
            "edge_count": len(edges),
            "directed_mixed": any(e["directed"] for e in edges) and any(not e["directed"] for e in edges),
        },
        "query": {
            "seed": seed,
            "direction": direction,
            "depth": depth,
            "relation": relation,
            "max_nodes": max_nodes,
        },
        "nodes": nodes,
        "edges": edges,
        "communities": communities,
        "metadata": {
            "truncated": truncated,
            "community_run_id": run_id,
            "source_graph_sha256": __import__("graph_store").logical_hash(con),
            "layout_hint": layout_hint,
        },
    }
    from graph_common import write_json
    write_json(output, payload, inputs=[db_path])
    return {"status": "pass", "output": str(output), "sha256": sha256_file(output), "nodes": len(nodes), "edges": len(edges), "truncated": truncated}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def db_stats(con: sqlite3.Connection) -> dict[str, Any]:
    scalar = lambda sql: int(con.execute(sql).fetchone()[0])
    provenance = {
        r["provenance"]: int(r["n"])
        for r in con.execute(
            "SELECT provenance,COUNT(*) n FROM (SELECT provenance FROM node_evidence UNION ALL SELECT provenance FROM edge_evidence) GROUP BY provenance ORDER BY provenance"
        )
    }
    return {
        "sources": scalar("SELECT COUNT(*) FROM sources"),
        "nodes": scalar("SELECT COUNT(*) FROM nodes"),
        "active_nodes": scalar("SELECT COUNT(*) FROM active_nodes"),
        "edges": scalar("SELECT COUNT(*) FROM edges"),
        "active_edges": scalar("SELECT COUNT(*) FROM active_edges"),
        "node_evidence": scalar("SELECT COUNT(*) FROM node_evidence"),
        "edge_evidence": scalar("SELECT COUNT(*) FROM edge_evidence"),
        "ambiguous_evidence": scalar("SELECT (SELECT COUNT(*) FROM node_evidence WHERE status='ambiguous') + (SELECT COUNT(*) FROM edge_evidence WHERE status='ambiguous')"),
        "stale_evidence": scalar("SELECT (SELECT COUNT(*) FROM node_evidence WHERE status='stale') + (SELECT COUNT(*) FROM edge_evidence WHERE status='stale')"),
        "provenance": provenance,
    }


def validate_db(con: sqlite3.Connection) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    quick = con.execute("PRAGMA quick_check").fetchall()
    if [r[0] for r in quick] != ["ok"]:
        errors.extend(f"quick_check: {r[0]}" for r in quick)
    fk = con.execute("PRAGMA foreign_key_check").fetchall()
    errors.extend(f"foreign_key_check: {tuple(r)}" for r in fk)
    user_version = int(con.execute("PRAGMA user_version").fetchone()[0])
    if user_version != SCHEMA_VERSION:
        errors.append(f"user_version={user_version}, expected {SCHEMA_VERSION}")
    meta = con.execute("SELECT value FROM graph_meta WHERE key='schema_version'").fetchone()
    if not meta or meta["value"] != str(SCHEMA_VERSION):
        errors.append("graph_meta.schema_version missing or mismatched")
    for table, col in [("nodes", "properties_json"), ("edges", "properties_json"), ("sources", "metadata_json"), ("node_evidence", "details_json"), ("edge_evidence", "details_json")]:
        for r in con.execute(f"SELECT rowid,{col} v FROM {table}"):
            try:
                json.loads(r["v"])
            except Exception as exc:
                errors.append(f"{table} rowid={r['rowid']} invalid JSON: {exc}")
    inactive_endpoints = con.execute(
        """
        SELECT ae.id FROM active_edges ae
        LEFT JOIN active_nodes s ON s.id=ae.source_node_id
        LEFT JOIN active_nodes t ON t.id=ae.target_node_id
        WHERE s.id IS NULL OR t.id IS NULL ORDER BY ae.id
        """
    ).fetchall()
    if inactive_endpoints:
        errors.append(f"active edges with inactive endpoints: {[r['id'] for r in inactive_endpoints]}")
    try:
        fts_count = int(con.execute("SELECT COUNT(*) FROM node_search").fetchone()[0])
        active_count = int(con.execute("SELECT COUNT(*) FROM active_nodes").fetchone()[0])
        if fts_count != active_count:
            warnings.append(f"FTS row count {fts_count} differs from active node count {active_count}; apply a patch or rebuild search")
    except sqlite3.OperationalError:
        warnings.append("FTS5 unavailable; LIKE search fallback will be used")
    return {"status": "pass" if not errors else "fail", "errors": errors, "warnings": warnings, "stats": db_stats(con)}


def json_print(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Local provenance-first graph engine backed by SQLite")
    p.add_argument("--db", default=".local-graph/graph.db", help="SQLite graph database path")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("init")

    vp = sub.add_parser("validate-patch")
    vp.add_argument("patch")

    ap = sub.add_parser("apply-patch")
    ap.add_argument("patch")
    ap.add_argument("--keep-orphans", action="store_true")

    fn = sub.add_parser("find")
    fn.add_argument("query")
    fn.add_argument("--limit", type=int, default=20)

    nd = sub.add_parser("node")
    nd.add_argument("node")

    nb = sub.add_parser("neighbors")
    nb.add_argument("node")
    nb.add_argument("--direction", choices=["incoming", "outgoing", "both"], default="both")
    nb.add_argument("--relation")

    pa = sub.add_parser("path")
    pa.add_argument("source")
    pa.add_argument("target")
    pa.add_argument("--max-depth", type=int, default=8)
    pa.add_argument("--undirected", action="store_true")
    pa.add_argument("--relation")

    im = sub.add_parser("impact")
    im.add_argument("node")
    im.add_argument("--direction", choices=["dependents", "dependencies"], default="dependents")
    im.add_argument("--depth", type=int, default=2)
    im.add_argument("--relation")

    sub.add_parser("stats")
    sub.add_parser("validate-db")

    ex = sub.add_parser("export-view")
    ex.add_argument("output")
    ex.add_argument("--seed")
    ex.add_argument("--direction", choices=["incoming", "outgoing", "both"], default="both")
    ex.add_argument("--depth", type=int, default=2)
    ex.add_argument("--relation")
    ex.add_argument("--max-nodes", type=int, default=500)
    ex.add_argument("--layout-hint", choices=["dagre", "radial", "circular", "grid", "force"])
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    db = Path(args.db).expanduser().resolve()
    try:
        if args.command == "init":
            json_print(init_db(db))
            return 0
        if args.command == "validate-patch":
            result = validate_patch_file(db if db.exists() else None, Path(args.patch).expanduser().resolve())
            json_print(result)
            return 0 if result["status"] == "pass" else 1
        if args.command == "apply-patch":
            result = apply_patch(db, Path(args.patch).expanduser().resolve(), prune_orphans=not args.keep_orphans)
            json_print(result)
            return 0 if result["status"] == "pass" else 1

        con = connect(db)
        try:
            if args.command == "find":
                json_print({"status": "pass", "results": find_nodes(con, args.query, args.limit)})
            elif args.command == "node":
                node_id = resolve_node(con, args.node)
                json_print({"status": "pass", "node": node_record(con, node_id)})
            elif args.command == "neighbors":
                node_id = resolve_node(con, args.node)
                rows = active_edge_rows(con, args.relation)
                items = []
                for row in rows:
                    if args.direction in ("outgoing", "both") and row["source_node_id"] == node_id:
                        items.append({"direction": "outgoing", "neighbor": row["target_node_id"], "edge": edge_record(con, row)})
                    if args.direction in ("incoming", "both") and row["target_node_id"] == node_id:
                        items.append({"direction": "incoming", "neighbor": row["source_node_id"], "edge": edge_record(con, row)})
                    if not bool(row["directed"]):
                        if args.direction in ("outgoing", "both") and row["target_node_id"] == node_id:
                            items.append({"direction": "outgoing", "neighbor": row["source_node_id"], "edge": edge_record(con, row)})
                        if args.direction in ("incoming", "both") and row["source_node_id"] == node_id:
                            items.append({"direction": "incoming", "neighbor": row["target_node_id"], "edge": edge_record(con, row)})
                items.sort(key=lambda x: (x["direction"], x["neighbor"], x["edge"]["id"]))
                json_print({"status": "pass", "node": node_id, "neighbors": items})
            elif args.command == "path":
                start, goal = resolve_node(con, args.source), resolve_node(con, args.target)
                json_print({"status": "pass", "source": start, "target": goal, "path": bfs_path(con, start, goal, args.max_depth, args.undirected, args.relation)})
            elif args.command == "impact":
                start = resolve_node(con, args.node)
                json_print({"status": "pass", "node": start, "impact": reach(con, start, args.direction, args.depth, args.relation)})
            elif args.command == "stats":
                json_print({"status": "pass", "stats": db_stats(con)})
            elif args.command == "validate-db":
                result = validate_db(con)
                json_print(result)
                return 0 if result["status"] == "pass" else 1
            elif args.command == "export-view":
                result = export_view(
                    con,
                    db,
                    Path(args.output).expanduser().resolve(),
                    args.seed,
                    args.direction,
                    args.depth,
                    args.relation,
                    args.max_nodes,
                    args.layout_hint,
                )
                json_print(result)
            else:
                raise ValueError(f"unsupported command: {args.command}")
        finally:
            con.close()
        return 0
    except (ValueError, KeyError, FileNotFoundError, json.JSONDecodeError, sqlite3.Error) as exc:
        json_print({"status": "fail", "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
