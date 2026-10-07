#!/usr/bin/env python3
"""Deterministic GraphView v1 validator and HTML renderer.

The renderer never creates graph facts. It projects an existing graph-view-v1 into
an interactive workspace. AntV G6 5.1.1 is preferred when available; a bundled
vanilla-SVG renderer is the local/offline fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

VIEW_VERSION = "graph-view-v1"
G6_VERSION = "5.1.1"
G6_CDN = f"https://unpkg.com/@antv/g6@{G6_VERSION}/dist/g6.min.js"
LAYOUTS = {"auto", "dagre", "radial", "circular", "grid", "force"}
BACKENDS = {"auto", "g6", "builtin"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_graphview(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root: expected object"]
    if data.get("schema_version") != VIEW_VERSION:
        errors.append(f"schema_version: expected {VIEW_VERSION!r}")
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
        for field in ("id", "label", "kind"):
            if not isinstance(node.get(field), str) or not node[field].strip():
                errors.append(f"{p}.{field}: expected non-empty string")
        node_id = node.get("id")
        if isinstance(node_id, str):
            if node_id in node_ids:
                errors.append(f"{p}.id: duplicate node id {node_id!r}")
            node_ids.add(node_id)
        if node.get("properties") is not None and not isinstance(node.get("properties"), dict):
            errors.append(f"{p}.properties: expected object")
    edge_ids: set[str] = set()
    for i, edge in enumerate(edges):
        p = f"edges[{i}]"
        if not isinstance(edge, dict):
            errors.append(f"{p}: expected object")
            continue
        for field in ("id", "source", "target", "relation"):
            if not isinstance(edge.get(field), str) or not edge[field].strip():
                errors.append(f"{p}.{field}: expected non-empty string")
        edge_id = edge.get("id")
        if isinstance(edge_id, str):
            if edge_id in edge_ids:
                errors.append(f"{p}.id: duplicate edge id {edge_id!r}")
            edge_ids.add(edge_id)
        if isinstance(edge.get("source"), str) and edge["source"] not in node_ids:
            errors.append(f"{p}.source: unknown node {edge['source']!r}")
        if isinstance(edge.get("target"), str) and edge["target"] not in node_ids:
            errors.append(f"{p}.target: unknown node {edge['target']!r}")
        if "directed" in edge and not isinstance(edge.get("directed"), bool):
            errors.append(f"{p}.directed: expected boolean")
        if edge.get("properties") is not None and not isinstance(edge.get("properties"), dict):
            errors.append(f"{p}.properties: expected object")
    if data.get("communities") is not None and not isinstance(data.get("communities"), list):
        errors.append("communities: expected array")
    if data.get("metadata") is not None and not isinstance(data.get("metadata"), dict):
        errors.append("metadata: expected object")
    if data.get("query") is not None and not isinstance(data.get("query"), dict):
        errors.append("query: expected object")
    return errors


def is_dag(data: dict[str, Any]) -> bool:
    nodes = sorted(n["id"] for n in data.get("nodes", []))
    edges = data.get("edges", [])
    if any(not bool(e.get("directed", True)) for e in edges):
        return False
    indegree = {n: 0 for n in nodes}
    out: dict[str, list[str]] = {n: [] for n in nodes}
    for edge in edges:
        s, t = edge["source"], edge["target"]
        out[s].append(t)
        indegree[t] += 1
    ready = sorted([n for n in nodes if indegree[n] == 0])
    count = 0
    while ready:
        node = ready.pop(0)
        count += 1
        for nxt in sorted(out[node]):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)
                ready.sort()
    return count == len(nodes)


def choose_layout(data: dict[str, Any], requested: str) -> str:
    if requested not in LAYOUTS:
        raise ValueError(f"unsupported layout: {requested}")
    if requested != "auto":
        return requested
    hint = (data.get("metadata") or {}).get("layout_hint")
    if hint in LAYOUTS - {"auto"}:
        return str(hint)
    query = data.get("query") or {}
    if query.get("seed") and len(data.get("nodes", [])) > 1:
        return "radial"
    if data.get("nodes") and is_dag(data):
        return "dagre"
    return "circular"


def safe_script_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).replace("</", "<\\/")


def g6_loader(g6_js: Path | None, backend: str) -> str:
    if backend == "builtin":
        return ""
    if g6_js is not None:
        source = g6_js.read_text(encoding="utf-8")
        source = source.replace("</script", "<\\/script")
        return f"<script>\n{source}\n</script>"
    return f'<script src="{G6_CDN}" crossorigin="anonymous"></script>'


def render(input_path: Path, output_path: Path, template_path: Path, backend: str, layout: str, g6_js: Path | None) -> dict[str, Any]:
    if backend not in BACKENDS:
        raise ValueError(f"unsupported backend: {backend}")
    data = load_json(input_path)
    errors = validate_graphview(data)
    if errors:
        return {"status": "fail", "errors": errors, "mutated": False}
    selected_layout = choose_layout(data, layout)
    config = {
        "backend": backend,
        "layout": selected_layout,
        "g6_version": G6_VERSION,
        "source_sha256": sha256_file(input_path),
    }
    template = template_path.read_text(encoding="utf-8")
    required = ["__GRAPH_DATA__", "__VIEWER_CONFIG__", "__G6_SCRIPT__"]
    missing = [token for token in required if token not in template]
    if missing:
        raise ValueError(f"viewer template missing placeholders: {missing}")
    html = template.replace("__GRAPH_DATA__", safe_script_json(data))
    html = html.replace("__VIEWER_CONFIG__", safe_script_json(config))
    html = html.replace("__G6_SCRIPT__", g6_loader(g6_js, backend))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8", newline="\n")
    return {
        "status": "pass",
        "output": str(output_path),
        "sha256": sha256_file(output_path),
        "input_sha256": config["source_sha256"],
        "backend": backend,
        "layout": selected_layout,
        "g6_version": G6_VERSION if backend != "builtin" else None,
        "offline": bool(g6_js) or backend == "builtin",
    }


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Validate GraphView v1 and render a deterministic local graph explorer")
    sub = p.add_subparsers(dest="command", required=True)
    va = sub.add_parser("validate")
    va.add_argument("input")
    la = sub.add_parser("layout")
    la.add_argument("input")
    la.add_argument("--layout", choices=sorted(LAYOUTS), default="auto")
    re = sub.add_parser("render")
    re.add_argument("input")
    re.add_argument("--output", default="graph.html")
    re.add_argument("--backend", choices=sorted(BACKENDS), default="auto")
    re.add_argument("--layout", choices=sorted(LAYOUTS), default="auto")
    re.add_argument("--g6-js", help="Optional local g6.min.js to inline for fully offline G6 rendering")
    re.add_argument("--template", help="Override bundled viewer template")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        input_path = Path(args.input).expanduser().resolve()
        data = load_json(input_path)
        errors = validate_graphview(data)
        if args.command == "validate":
            result = {"status": "pass" if not errors else "fail", "errors": errors, "input": str(input_path)}
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if not errors else 1
        if errors:
            print(json.dumps({"status": "fail", "errors": errors}, indent=2, sort_keys=True))
            return 1
        if args.command == "layout":
            result = {"status": "pass", "layout": choose_layout(data, args.layout), "input": str(input_path)}
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0
        if args.command == "render":
            template = Path(args.template).expanduser().resolve() if args.template else root / "assets" / "graph-viewer.html"
            g6_js = Path(args.g6_js).expanduser().resolve() if args.g6_js else None
            if g6_js and not g6_js.is_file():
                raise FileNotFoundError(f"G6 bundle not found: {g6_js}")
            result = render(input_path, Path(args.output).expanduser().resolve(), template, args.backend, args.layout, g6_js)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["status"] == "pass" else 1
        raise ValueError(f"unsupported command: {args.command}")
    except (ValueError, FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
