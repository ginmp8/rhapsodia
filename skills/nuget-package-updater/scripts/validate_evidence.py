#!/usr/bin/env python3
"""Validate NuGet updater metadata snapshots and receipts with stdlib only."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_digest(value: Any) -> str:
    return digest_text(canonical_json(value))


def validate_receipt(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = data.get("payloadSha256")
    if not isinstance(expected, str):
        return ["missing payloadSha256"]
    payload = dict(data)
    payload.pop("payloadSha256", None)
    observed = canonical_digest(payload)
    if observed != expected:
        errors.append(f"payloadSha256 mismatch: expected {expected}, observed {observed}")
    receipt_type = data.get("receiptType")
    if receipt_type not in {"nuget-package-decision", "nuget-package-update"}:
        errors.append(f"unsupported receiptType: {receipt_type!r}")
    for key in ["receiptVersion", "toolContractVersion", "decisionIdentity", "baselineSha256", "metadataSnapshotSha256"]:
        if key not in data:
            errors.append(f"missing {key}")
    return errors


def validate_snapshot(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    records = data.get("records")
    if not isinstance(records, list):
        return ["records must be an array"]
    identity_records = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"records[{index}] must be an object")
            continue
        body = record.get("body")
        raw_hash = record.get("rawSha256")
        canonical_hash = record.get("canonicalSha256")
        url = record.get("url")
        if not isinstance(body, str) or not isinstance(raw_hash, str) or not isinstance(url, str):
            errors.append(f"records[{index}] missing url/body/rawSha256")
            continue
        if digest_text(body) != raw_hash:
            errors.append(f"records[{index}] rawSha256 mismatch")
        try:
            parsed = json.loads(body)
        except Exception as exc:
            errors.append(f"records[{index}] invalid JSON body: {exc}")
            continue
        if canonical_digest(parsed) != canonical_hash:
            errors.append(f"records[{index}] canonicalSha256 mismatch")
        identity_records.append({"url": url, "rawSha256": raw_hash, "canonicalSha256": canonical_hash})

    offline = data.get("offlineVersions")
    offline_identity = None
    if isinstance(offline, dict):
        offline_identity = {"path": offline.get("path"), "sha256": offline.get("sha256")}
    material = {
        "schemaVersion": data.get("schemaVersion"),
        "sources": data.get("sources"),
        "records": identity_records,
        "offlineVersions": offline_identity,
    }
    observed_snapshot = canonical_digest(material)
    if observed_snapshot != data.get("snapshotSha256"):
        errors.append(
            f"snapshotSha256 mismatch: expected {data.get('snapshotSha256')}, observed {observed_snapshot}"
        )
    return errors


def validate(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"path": str(path), "status": "fail", "errors": [f"invalid JSON: {exc}"]}
    if isinstance(data, dict) and "receiptType" in data:
        errors = validate_receipt(data)
        kind = data.get("receiptType")
    elif isinstance(data, dict) and "snapshotSha256" in data and "records" in data:
        errors = validate_snapshot(data)
        kind = "nuget-metadata-snapshot"
    else:
        errors = ["unrecognized evidence document"]
        kind = "unknown"
    return {"path": str(path), "kind": kind, "status": "fail" if errors else "pass", "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate NuGet updater evidence hashes.")
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()
    results = [validate(Path(value)) for value in args.paths]
    payload = {"status": "fail" if any(item["status"] == "fail" for item in results) else "pass", "results": results}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 1 if payload["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
