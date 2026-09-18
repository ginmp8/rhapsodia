#!/usr/bin/env python3
"""Validate coordinated package versions and byte-equivalent ecosystem contracts."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from ecosystem_handoff import load_compatibility, package_role, package_version

SHARED_FILES = (
    "references/priority-contract.json",
    "references/ecosystem-handoff-contract.json",
    "references/ecosystem-compatibility.json",
)
SEMVER_HEADING = re.compile(r"^##\s+\[?(\d+\.\d+\.\d+)\]?\s+-", re.M)


def collect_errors(root: Path, peers: list[Path] | None = None) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    manifest = load_compatibility(root)
    role = package_role(root)
    version = package_version(root)
    if manifest.get("schema_version") != "1.0.0" or manifest.get("contract_id") != "nomia-mago-magia-compatibility-v1":
        errors.append("invalid ecosystem compatibility manifest identity")
    expected = str((manifest.get("packages") or {}).get(role) or "")
    if version != expected or version != manifest.get("ecosystem_release"):
        errors.append(f"{role} version {version} does not equal ecosystem release {manifest.get('ecosystem_release')}")
    policy = manifest.get("policy") or {}
    if policy.get("classification") != "coordinated-exact" or policy.get("mixed_versions_allowed") is not False:
        errors.append("compatibility policy must be coordinated-exact and reject mixed versions")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    versions = SEMVER_HEADING.findall(changelog)
    if not versions or versions[0] != version:
        errors.append("CHANGELOG latest version must equal package version")
    if role == "mago":
        release = json.loads((root / "release.json").read_text(encoding="utf-8"))
        if release.get("version") != version or release.get("ecosystem_release") != version:
            errors.append("Mago release.json version/ecosystem_release mismatch")
    for rel in SHARED_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing shared contract: {rel}")
    local = {rel:(root/rel).read_bytes() for rel in SHARED_FILES if (root/rel).is_file()}
    seen_roles = {role}
    for peer in peers or []:
        peer = peer.resolve()
        try:
            peer_role = package_role(peer)
            peer_version = package_version(peer)
        except Exception as exc:
            errors.append(f"invalid peer {peer}: {exc}")
            continue
        seen_roles.add(peer_role)
        if peer_version != version:
            errors.append(f"peer {peer_role} version {peer_version} differs from {version}")
        for rel, data in local.items():
            path = peer / rel
            if not path.is_file():
                errors.append(f"peer {peer_role} missing {rel}")
            elif path.read_bytes() != data:
                errors.append(f"peer {peer_role} differs for {rel}")
    if peers and seen_roles != {"mago","magia","nomia"}:
        errors.append(f"peer set must cover mago, magia, and nomia; got {sorted(seen_roles)}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--peer-root", action="append", default=[])
    parser.add_argument("--json-output")
    args = parser.parse_args(argv)
    root = Path(args.target).resolve()
    errors = collect_errors(root, [Path(item).resolve() for item in args.peer_root])
    result: dict[str, Any] = {"status":"pass" if not errors else "fail","target":str(root),"role":package_role(root),"version":package_version(root),"errors":errors}
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_output: Path(args.json_output).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
