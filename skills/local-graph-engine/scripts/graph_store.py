"""Transactional source claims, immutable revision history and safe snapshots.

The v1 public contracts remain valid. Extension tables are additive. Source data
is never modified; all changes occur in the selected graph database.
"""
from __future__ import annotations
import json
import os
import sqlite3
import tempfile
from pathlib import Path
from typing import Any
import graph_engine as ge
from graph_common import canonical, digest, finite_tree, read_json, safe_output

EXTENSIONS = (
 "CREATE TABLE IF NOT EXISTS source_revisions (source_id TEXT NOT NULL, revision TEXT NOT NULL, patch_json TEXT NOT NULL, PRIMARY KEY(source_id,revision))",
 "CREATE TABLE IF NOT EXISTS current_revisions (source_id TEXT PRIMARY KEY REFERENCES sources(id), revision TEXT NOT NULL)",
 "CREATE TABLE IF NOT EXISTS node_claims (node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE, source_id TEXT NOT NULL REFERENCES sources(id), payload_json TEXT NOT NULL, rank_json TEXT NOT NULL, PRIMARY KEY(node_id,source_id))",
 "CREATE TABLE IF NOT EXISTS edge_claims (edge_id TEXT NOT NULL REFERENCES edges(id) ON DELETE CASCADE, source_id TEXT NOT NULL REFERENCES sources(id), payload_json TEXT NOT NULL, rank_json TEXT NOT NULL, PRIMARY KEY(edge_id,source_id))",
 "CREATE TABLE IF NOT EXISTS graph_changes (sequence INTEGER PRIMARY KEY AUTOINCREMENT, source_id TEXT NOT NULL, previous_revision TEXT, revision TEXT NOT NULL, action TEXT NOT NULL)",
 "CREATE TABLE IF NOT EXISTS graph_memory (id TEXT PRIMARY KEY, question TEXT NOT NULL, node_ids_json TEXT NOT NULL, outcome TEXT NOT NULL CHECK(outcome IN ('useful','dead_end','corrected')), note TEXT NOT NULL, graph_hash TEXT NOT NULL)",
 "CREATE TABLE IF NOT EXISTS saved_queries (name TEXT PRIMARY KEY, request_json TEXT NOT NULL)",
 "CREATE INDEX IF NOT EXISTS idx_node_claims_source ON node_claims(source_id)",
 "CREATE INDEX IF NOT EXISTS idx_edge_claims_source ON edge_claims(source_id)",
)

def check_schema(con: sqlite3.Connection) -> None:
    if con.execute("PRAGMA user_version").fetchone()[0] != 1:
        raise ValueError("unsupported database schema; initialize a new graph or use the documented migration")
    row = con.execute("SELECT value FROM graph_meta WHERE key='graph_contract'").fetchone()
    if not row or row[0] != "local-graph-sqlite-v1": raise ValueError("not a Local Graph database")

def readonly(path: Path) -> sqlite3.Connection:
    path = Path(path).resolve()
    if not path.is_file(): raise FileNotFoundError(str(path))
    con = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=5)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA query_only=ON")
    con.execute("PRAGMA trusted_schema=OFF")
    try:
        check_schema(con)
    except Exception:
        con.close()
        raise
    return con

def ensure_extensions(con: sqlite3.Connection) -> None:
    check_schema(con)
    row = con.execute("SELECT value FROM graph_meta WHERE key='extension_version'").fetchone()
    if row and row[0] != "2": raise ValueError("unsupported extension version")
    for sql in EXTENSIONS: con.execute(sql)
    con.execute("INSERT OR IGNORE INTO graph_meta(key,value) VALUES('extension_version','2')")

def normalized_patch(patch: dict) -> dict:
    finite_tree(patch)
    value = json.loads(canonical(patch))
    if isinstance(value.get("source"),dict) and value["source"].get("metadata") is None:
        value["source"]["metadata"]={}
    for node in value.get("nodes", []):
        if not isinstance(node, dict): continue
        if node.get("properties") is None: node["properties"]={}
        if isinstance(node.get("aliases"), list): node["aliases"] = sorted(set(node["aliases"]))
        if isinstance(node.get("evidence"), list): node["evidence"] = sorted(node["evidence"], key=canonical)
    for edge in value.get("edges", []):
        if not isinstance(edge, dict): continue
        if edge.get("properties") is None: edge["properties"]={}
        if edge.get("directed") is False and isinstance(edge.get("source"), str) and isinstance(edge.get("target"), str):
            edge["source"], edge["target"] = sorted((edge["source"], edge["target"]))
        if isinstance(edge.get("evidence"), list): edge["evidence"] = sorted(edge["evidence"], key=canonical)
    value["nodes"] = sorted(value.get("nodes", []), key=lambda x: canonical(x))
    value["edges"] = sorted(value.get("edges", []), key=lambda x: canonical(x))
    return value

def rank(evidence: list[dict], uri: str) -> list:
    strength = {"accepted": 0, "ambiguous": 1, "stale": 2, "rejected": 3}
    best = min((strength[e["status"]], -float(e["confidence"])) for e in evidence)
    return [*best, uri]

def reconstruct_sources(con: sqlite3.Connection) -> list[dict]:
    """Recover v1 rows without inventing attributes lost before this release."""
    result = []
    has_revisions = con.execute("SELECT 1 FROM sqlite_master WHERE name='current_revisions'").fetchone()
    for source in con.execute("SELECT * FROM sources ORDER BY uri").fetchall():
        sid = source["id"]
        if has_revisions:
            current = con.execute("SELECT r.patch_json FROM source_revisions r JOIN current_revisions c ON c.source_id=r.source_id AND c.revision=r.revision WHERE c.source_id=?", (sid,)).fetchone()
            if current:
                result.append(json.loads(current[0]))
                continue
        patch = {"schema_version": ge.PATCH_VERSION,
                 "source": {"uri": source["uri"], "kind": source["kind"], "content_hash": source["content_hash"], "metadata": json.loads(source["metadata_json"])},
                 "nodes": [], "edges": []}
        for table, etable, key in [("nodes", "node_evidence", "node_id"), ("edges", "edge_evidence", "edge_id")]:
            ids = [r[0] for r in con.execute(f"SELECT DISTINCT {key} FROM {etable} WHERE source_id=? ORDER BY {key}", (sid,))]
            for entity_id in ids:
                r = con.execute(f"SELECT * FROM {table} WHERE id=?", (entity_id,)).fetchone()
                ev = [{"provenance": e["provenance"], "confidence": e["confidence"], "locator": e["locator"], "status": e["status"], "details": json.loads(e["details_json"])} for e in con.execute(f"SELECT * FROM {etable} WHERE source_id=? AND {key}=? ORDER BY id", (sid,entity_id))]
                if table == "nodes":
                    record = {"id": r["id"], "kind": r["kind"], "label": r["label"], "properties": json.loads(r["properties_json"]), "aliases": [a[0] for a in con.execute("SELECT alias FROM node_aliases WHERE node_id=? AND source_id=? ORDER BY alias", (entity_id,sid))], "evidence": ev}
                else:
                    record = {"id": r["id"], "source": r["source_node_id"], "target": r["target_node_id"], "relation": r["relation"], "directed": bool(r["directed"]), "properties": json.loads(r["properties_json"]), "evidence": ev}
                patch[table].append(record)
        result.append(patch)
    return result

def bootstrap_claims(con: sqlite3.Connection) -> None:
    # Only source snapshots missing from the extension are initialized. Original
    # v1 current fields are recoverable, older overwritten fields are not.
    missing = {r[0] for r in con.execute("SELECT id FROM sources WHERE id NOT IN (SELECT source_id FROM current_revisions)")}
    if not missing: return
    for patch in reconstruct_sources(con):
        sid = ge.source_id(patch["source"]["uri"])
        if sid not in missing: continue
        value = normalized_patch(patch); revision = digest(value)
        con.execute("INSERT OR IGNORE INTO source_revisions VALUES(?,?,?)", (sid,revision,canonical(value)))
        con.execute("INSERT INTO current_revisions VALUES(?,?)", (sid,revision))
        for table, key in [("node_claims", "nodes"), ("edge_claims", "edges")]:
            for item in patch[key]:
                con.execute(f"INSERT OR IGNORE INTO {table} VALUES(?,?,?,?)", (item["id"],sid,canonical(item),canonical(rank(item["evidence"],patch["source"]["uri"]))))

def resolve_claims(con, table, identifier):
    key = "node_id" if table == "node_claims" else "edge_id"
    rows = con.execute(f"SELECT payload_json,rank_json FROM {table} WHERE {key}=?", (identifier,)).fetchall()
    ordered = sorted(rows, key=lambda r: json.loads(r["rank_json"]))
    if not ordered: return None
    # Do not populate accepted canonical properties from weaker/rejected-only
    # assertions. All weaker claims remain inspectable in the claim ledger.
    best_status = json.loads(ordered[0]["rank_json"])[0]
    claims = [json.loads(r["payload_json"]) for r in ordered if json.loads(r["rank_json"])[0] == best_status]
    chosen = dict(claims[0]); properties = {}
    for claim in reversed(claims): properties.update(claim.get("properties", {}))
    chosen["properties"] = properties
    return chosen

def logical_hash(con: sqlite3.Connection) -> str:
    tables = [("sources", "uri,kind,content_hash,metadata_json"), ("nodes", "id,kind,label,properties_json"),
              ("edges", "id,source_node_id,target_node_id,relation,directed,properties_json"),
              ("node_aliases", "alias,node_id,source_id"), ("node_evidence", "id,node_id,source_id,provenance,confidence,locator,status,details_json"),
              ("edge_evidence", "id,edge_id,source_id,provenance,confidence,locator,status,details_json")]
    return digest({t: sorted([list(r) for r in con.execute(f"SELECT {cols} FROM {t}")],key=canonical) for t,cols in tables})

def apply_patches(db: Path, patches: list[dict], expected: dict[str, str] | None = None, prune: bool = True) -> dict:
    if not isinstance(patches, list) or not patches or len(patches) > 10000:
        raise ValueError("expected 1..10000 patches")
    patches = [normalized_patch(p) for p in patches]
    if len({p.get("source",{}).get("uri") for p in patches}) != len(patches):
        raise ValueError("one patch per source is required in a batch")
    con = ge.connect(Path(db))
    try:
        check_schema(con)
        con.execute("BEGIN IMMEDIATE")
        ensure_extensions(con); bootstrap_claims(con)
        known = {r[0] for r in con.execute("SELECT id FROM nodes")}
        known.update(n.get("id") for p in patches for n in p.get("nodes",[]) if isinstance(n,dict) and isinstance(n.get("id"),str))
        for patch in patches:
            errors = ge.validate_patch_data(patch, known)
            if errors: raise ValueError("; ".join(errors))
        changed = []; touched_nodes = set(); touched_edges = set()
        for patch in sorted(patches, key=lambda p: p["source"]["uri"]):
            source = patch["source"]; sid = ge.source_id(source["uri"]); revision = digest(patch)
            prior = con.execute("SELECT revision FROM current_revisions WHERE source_id=?", (sid,)).fetchone()
            prior_hash = prior[0] if prior else None
            if expected and source["uri"] in expected and expected[source["uri"]] != prior_hash:
                raise ValueError("source revision conflict; refresh before retry")
            if prior_hash == revision: continue
            changed.append(source["uri"])
            touched_nodes.update(r[0] for r in con.execute("SELECT node_id FROM node_claims WHERE source_id=?",(sid,)))
            touched_edges.update(r[0] for r in con.execute("SELECT edge_id FROM edge_claims WHERE source_id=?",(sid,)))
            con.execute("INSERT INTO sources VALUES(?,?,?,?,?,?) ON CONFLICT(uri) DO UPDATE SET kind=excluded.kind,content_hash=excluded.content_hash,metadata_json=excluded.metadata_json,indexed_at=excluded.indexed_at",(sid,source["uri"],source["kind"],source.get("content_hash"),canonical(source.get("metadata",{})),ge.normalized_indexed_at(source)))
            for table in ["node_aliases","node_evidence","edge_evidence","node_claims","edge_claims"]:
                con.execute(f"DELETE FROM {table} WHERE source_id=?",(sid,))
            # Pre-create every batch endpoint before any edge insert.
            for batch in patches:
                for node in batch["nodes"]:
                    con.execute("INSERT OR IGNORE INTO nodes VALUES(?,?,?,?)",(node["id"],node["kind"],node["label"],canonical(node.get("properties",{}))))
            for node in patch["nodes"]:
                nid=node["id"]; touched_nodes.add(nid)
                con.execute("INSERT INTO node_claims VALUES(?,?,?,?)",(nid,sid,canonical(node),canonical(rank(node["evidence"],source["uri"]))))
                for alias in sorted(set(node.get("aliases",[]))):
                    con.execute("INSERT INTO node_aliases VALUES(?,?,?)",(alias,nid,sid))
                for ev in node["evidence"]: insert_evidence(con,"node",nid,sid,ev)
            for edge in patch["edges"]:
                s,t,rel,direction=edge["source"],edge["target"],edge["relation"],edge.get("directed",True)
                eid=edge.get("id") or ge.edge_id(s,t,rel,direction)
                existing=con.execute("SELECT source_node_id,target_node_id,relation,directed FROM edges WHERE id=?",(eid,)).fetchone()
                if existing and tuple(existing)!=(s,t,rel,int(direction)): raise ValueError("edge id collision")
                con.execute("INSERT INTO edges VALUES(?,?,?,?,?,?) ON CONFLICT(source_node_id,target_node_id,relation,directed) DO NOTHING",(eid,s,t,rel,int(direction),canonical(edge.get("properties",{}))))
                eid=con.execute("SELECT id FROM edges WHERE source_node_id=? AND target_node_id=? AND relation=? AND directed=?",(s,t,rel,int(direction))).fetchone()[0]
                touched_edges.add(eid); touched_nodes.update([s,t])
                edge=dict(edge,id=eid)
                con.execute("INSERT INTO edge_claims VALUES(?,?,?,?)",(eid,sid,canonical(edge),canonical(rank(edge["evidence"],source["uri"]))))
                for ev in edge["evidence"]: insert_evidence(con,"edge",eid,sid,ev)
            con.execute("INSERT OR IGNORE INTO source_revisions VALUES(?,?,?)",(sid,revision,canonical(patch)))
            con.execute("INSERT INTO current_revisions VALUES(?,?) ON CONFLICT(source_id) DO UPDATE SET revision=excluded.revision",(sid,revision))
            con.execute("INSERT INTO graph_changes(source_id,previous_revision,revision,action) VALUES(?,?,?,?)",(sid,prior_hash,revision,"replace"))
        for nid in sorted(touched_nodes):
            claim=resolve_claims(con,"node_claims",nid)
            if claim: con.execute("UPDATE nodes SET kind=?,label=?,properties_json=? WHERE id=?",(claim["kind"],claim["label"],canonical(claim.get("properties",{})),nid))
        for eid in sorted(touched_edges):
            claim=resolve_claims(con,"edge_claims",eid)
            if claim: con.execute("UPDATE edges SET properties_json=? WHERE id=?",(canonical(claim.get("properties",{})),eid))
        if changed:
            if prune:
                con.execute("DELETE FROM edges WHERE NOT EXISTS (SELECT 1 FROM edge_evidence WHERE edge_id=edges.id)")
                con.execute("DELETE FROM nodes WHERE NOT EXISTS (SELECT 1 FROM node_evidence WHERE node_id=nodes.id) AND NOT EXISTS (SELECT 1 FROM edges WHERE source_node_id=nodes.id OR target_node_id=nodes.id)")
            con.execute("UPDATE analysis_runs SET status='stale' WHERE status='pass'")
            ge.rebuild_fts(con)
        result={"status":"pass","mutated":bool(changed),"sources_changed":changed,"sources_unchanged":len(patches)-len(changed),"graph_hash":logical_hash(con),"counts":ge.db_stats(con)}
        con.commit(); return result
    except Exception:
        con.rollback(); raise
    finally: con.close()

def insert_evidence(con,kind,entity_id,sid,ev):
    table=f"{kind}_evidence"
    eid=ge.evidence_id(kind,entity_id,sid,ev)
    con.execute(f"INSERT OR REPLACE INTO {table} VALUES(?,?,?,?,?,?,?,?)",(eid,entity_id,sid,ev["provenance"],ev["confidence"],ev.get("locator"),ev["status"],canonical(ev.get("details",{}))))

def backup(db: Path, output: Path) -> dict:
    output=safe_output(output,[db])
    if output.exists(): raise FileExistsError("backup destination already exists")
    output.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix=".graph-backup-",dir=output.parent);os.close(fd)
    src=readonly(db)
    try:
        dst=sqlite3.connect(name)
        try:
            src.backup(dst)
            dst.execute("PRAGMA journal_mode=DELETE");dst.commit()
            if dst.execute("PRAGMA quick_check").fetchone()[0]!="ok": raise ValueError("backup integrity failure")
        finally: dst.close()
        if output.exists(): raise FileExistsError(str(output))
        os.replace(name,output)
        return {"status":"pass","output":str(output),"graph_hash":logical_hash(src)}
    finally:
        src.close()
        if os.path.exists(name):os.unlink(name)
