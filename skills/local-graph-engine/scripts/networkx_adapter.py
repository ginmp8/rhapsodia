#!/usr/bin/env python3
"""Optional NetworkX analytics adapter for local-graph-engine.

This is not required by the baseline skill. It imports NetworkX only when invoked.
Results are written to analysis_runs, node_metrics, communities, and community_members.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def db_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def connect(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(path))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA busy_timeout=5000")
    return con


def main() -> int:
    parser = argparse.ArgumentParser(description="Optional NetworkX analytics for local-graph-engine")
    parser.add_argument("--db", default=".local-graph/graph.db")
    parser.add_argument("--community", choices=["greedy-modularity", "none"], default="greedy-modularity")
    parser.add_argument("--pagerank", action="store_true")
    args = parser.parse_args()

    try:
        import networkx as nx
    except Exception as exc:
        print(json.dumps({"status": "fail", "error": f"NetworkX is optional and is not available: {exc}"}, indent=2))
        return 2

    db = Path(args.db).expanduser().resolve()
    if not db.exists():
        print(json.dumps({"status": "fail", "error": f"database does not exist: {db}"}, indent=2))
        return 1

    con = connect(db)
    try:
        node_ids = [r[0] for r in con.execute("SELECT id FROM active_nodes ORDER BY id")]
        edges = con.execute("SELECT * FROM active_edges ORDER BY id").fetchall()
        G = nx.DiGraph()
        G.add_nodes_from(node_ids)
        for r in edges:
            G.add_edge(r["source_node_id"], r["target_node_id"], id=r["id"], relation=r["relation"])
            if not bool(r["directed"]):
                G.add_edge(r["target_node_id"], r["source_node_id"], id=r["id"], relation=r["relation"])

        params = {"community": args.community, "pagerank": args.pagerank}
        run_id = "run:" + hashlib.sha256((db_hash(db) + canonical_json(params) + nx.__version__).encode("utf-8")).hexdigest()[:24]
        with con:
            con.execute("DELETE FROM analysis_runs WHERE id=?", (run_id,))
            con.execute(
                "INSERT INTO analysis_runs(id,algorithm,version,parameters_json,input_hash,status) VALUES(?,?,?,?,?,?)",
                (run_id, "networkx", nx.__version__, canonical_json(params), db_hash(db), "pass"),
            )

            metric_count = 0
            if args.pagerank and node_ids:
                scores = nx.pagerank(G)
                for node_id in sorted(scores):
                    con.execute(
                        "INSERT INTO node_metrics(run_id,node_id,metric,value) VALUES(?,?,?,?)",
                        (run_id, node_id, "pagerank", float(scores[node_id])),
                    )
                    metric_count += 1

            community_count = 0
            if args.community == "greedy-modularity" and node_ids:
                UG = nx.Graph()
                UG.add_nodes_from(node_ids)
                UG.add_edges_from(sorted({tuple(sorted((r["source_node_id"], r["target_node_id"]))) for r in edges}))
                groups = list(nx.community.greedy_modularity_communities(UG, weight=None)) if UG.number_of_edges() else [frozenset([n]) for n in node_ids]
                groups = sorted((sorted(g) for g in groups), key=lambda g: (g[0] if g else "", len(g)))
                for i, members in enumerate(groups, start=1):
                    cid = f"community:{i:04d}"
                    con.execute(
                        "INSERT INTO communities(run_id,id,label,properties_json) VALUES(?,?,?,?)",
                        (run_id, cid, f"Community {i}", "{}"),
                    )
                    for node_id in members:
                        con.execute(
                            "INSERT INTO community_members(run_id,community_id,node_id) VALUES(?,?,?)",
                            (run_id, cid, node_id),
                        )
                    community_count += 1

        print(
            json.dumps(
                {
                    "status": "pass",
                    "run_id": run_id,
                    "networkx_version": nx.__version__,
                    "nodes": len(node_ids),
                    "edges": len(edges),
                    "metrics_written": metric_count,
                    "communities_written": community_count,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except Exception as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2))
        return 1
    finally:
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())
