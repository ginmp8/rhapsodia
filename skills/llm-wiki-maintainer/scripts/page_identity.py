#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _wiki_common import atomic_write_bytes, atomic_write_json, canonical_page_id, render_frontmatter  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Canonical page identity and deterministic frontmatter renderer for the default wiki schema.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("id")
    p.add_argument("--type", required=True, choices=["source", "entity", "concept", "synthesis"])
    p.add_argument("--key", required=True)
    p.add_argument("--json")
    p = sub.add_parser("render-frontmatter")
    p.add_argument("--metadata", required=True)
    p.add_argument("--body")
    p.add_argument("--out", required=True)
    args = ap.parse_args()

    if args.cmd == "id":
        page_id = canonical_page_id(args.type, args.key)
        result = {"page_type": args.type, "canonical_key": args.key, "page_id": page_id}
        if args.json:
            atomic_write_json(Path(args.json), result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    metadata_path = Path(args.metadata).resolve(strict=True)
    body_path = Path(args.body).resolve(strict=True) if args.body else None
    out_path = Path(args.out).resolve(strict=False)
    if out_path == metadata_path or (body_path is not None and out_path == body_path):
        raise SystemExit("output aliases an input file")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    body = body_path.read_text(encoding="utf-8") if body_path else ""
    rendered = render_frontmatter(metadata) + body.lstrip("\n")
    atomic_write_bytes(out_path, rendered.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
