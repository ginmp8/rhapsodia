#!/usr/bin/env python3
"""Create one deterministic coordinated release attestation for Mago, Magia, and Nomia."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SHARED_REQUIRED = (
    "evals/ecosystem-routing-scenarios.json",
    "references/ecosystem-compatibility.json",
    "references/ecosystem-handoff-contract.json",
    "references/ecosystem-lifecycle.md",
    "references/ecosystem-routing-contract.json",
    "references/priority-contract.json",
    "scripts/ecosystem_handoff.py",
    "scripts/run_ecosystem_flow_harness.py",
    "scripts/run_ecosystem_negative_harness.py",
    "scripts/validate_ecosystem_release.py",
    "scripts/live_routing_harness.py",
    "references/live-routing-result-schema.json",
)
ROLE_ORDER = ("mago", "magia", "nomia")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def atomic_write(path: Path, text: str) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def package_identity(root: Path) -> tuple[str, str]:
    release = load_json(root / "release.json")
    name = str(release.get("name") or "")
    version = str(release.get("version") or "")
    version_file = (root / "VERSION").read_text(encoding="utf-8").strip()
    if name not in ROLE_ORDER:
        raise ValueError(f"invalid package name at {root}: {name}")
    if version != version_file:
        raise ValueError(f"VERSION/release mismatch for {name}: {version_file} != {version}")
    return name, version


def eligible_files(root: Path) -> list[Path]:
    blocked_dirs = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
    blocked_suffixes = {".pyc", ".pyo"}
    result=[]
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel=path.relative_to(root)
        if any(part in blocked_dirs for part in rel.parts) or path.suffix in blocked_suffixes:
            continue
        if path.suffix.lower() == ".zip":
            continue
        result.append(path)
    return result


def test_suite_digest(root: Path) -> str:
    digest=hashlib.sha256()
    files=sorted((root / "tests").glob("test_*.py"))
    if not files:
        raise ValueError(f"no test files found under {root / 'tests'}")
    for path in files:
        rel=path.relative_to(root).as_posix().encode("utf-8")
        data=path.read_bytes()
        digest.update(len(rel).to_bytes(4,"big")); digest.update(rel)
        digest.update(len(data).to_bytes(8,"big")); digest.update(data)
    return digest.hexdigest()


def tree_digest(root: Path) -> str:
    digest=hashlib.sha256()
    for path in eligible_files(root):
        rel=path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(rel).to_bytes(4,"big")); digest.update(rel)
        data=path.read_bytes(); digest.update(len(data).to_bytes(8,"big")); digest.update(data)
    return digest.hexdigest()


def collect_preflight_errors(roots: dict[str, Path]) -> list[str]:
    errors=[]
    identities={}
    for expected in ROLE_ORDER:
        root=roots.get(expected)
        if root is None or not root.is_dir():
            errors.append(f"missing package root: {expected}")
            continue
        for required in ("SKILL.md","VERSION","release.json","scripts/package_skill.py"):
            if not (root/required).is_file():
                errors.append(f"{expected}: missing {required}")
        try:
            name,version=package_identity(root)
            identities[expected]=(name,version)
            if name != expected:
                errors.append(f"root role mismatch: expected {expected}, found {name}")
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
    versions={value[1] for value in identities.values()}
    if len(identities)==3 and len(versions) != 1:
        errors.append(f"mixed package versions: {sorted(versions)}")
    if len(identities)==3:
        compatibility=load_json(roots["mago"]/"references/ecosystem-compatibility.json")
        release=str(compatibility.get("ecosystem_release") or "")
        if versions and next(iter(versions)) != release:
            errors.append(f"package version does not match ecosystem release {release}")
    for rel in SHARED_REQUIRED:
        values=[]
        for role in ROLE_ORDER:
            path=roots.get(role,Path("/nonexistent"))/rel
            if not path.is_file():
                errors.append(f"{role}: missing coordinated resource {rel}")
            else:
                values.append(path.read_bytes())
        if len(values)==3 and len(set(values)) != 1:
            errors.append(f"shared resource differs across packages: {rel}")
    return list(dict.fromkeys(errors))


def run_gate(name: str, command: list[str], cwd: Path, output_dir: Path, timeout_seconds: int) -> dict[str, Any]:
    output_dir.mkdir(parents=True,exist_ok=True)
    log_path=output_dir/f"{name}.log"
    started=time.monotonic()
    try:
        done=subprocess.run(command,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout_seconds,check=False,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
        status="pass" if done.returncode==0 else "fail"
        exit_code=done.returncode
        output=done.stdout
    except subprocess.TimeoutExpired as exc:
        status="timeout"; exit_code=None
        output=(exc.stdout or "") + "\nTIMEOUT\n"
    duration_ms=round((time.monotonic()-started)*1000)
    log_path.write_text(output,encoding="utf-8")
    return {"name":name,"status":status,"required":True,"command":command,"cwd":str(cwd),"exit_code":exit_code,"duration_ms":duration_ms,"log":str(log_path)}


def recursive_find(value: Any, keys: set[str], found: dict[str, Any] | None = None) -> dict[str, Any]:
    found={} if found is None else found
    if isinstance(value,dict):
        for key,child in value.items():
            if key in keys and key not in found:
                found[key]=child
            recursive_find(child,keys,found)
    elif isinstance(value,list):
        for child in value: recursive_find(child,keys,found)
    return found


def stable_projection(ledger: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version":ledger.get("schema_version"),
        "ecosystem_release":ledger.get("ecosystem_release"),
        "versions":ledger.get("versions"),
        "root_tree_hashes":ledger.get("root_tree_hashes"),
        "suite_digests":ledger.get("suite_digests"),
        "shared_hashes":ledger.get("shared_hashes"),
        "packages":{k:{"archive_sha256":v.get("archive_sha256"),"archive_size":v.get("archive_size"),"suite_digest":v.get("suite_digest"),"status":v.get("status")} for k,v in sorted((ledger.get("packages") or {}).items())},
        "gates":[{"name":g.get("name"),"status":g.get("status"),"exit_code":g.get("exit_code"),"required":g.get("required")} for g in ledger.get("gates",[])],
        "status":ledger.get("status"),
    }


def attestation_digest(ledger: dict[str, Any]) -> str:
    data=json.dumps(stable_projection(ledger),sort_keys=True,separators=(",",":")).encode("utf-8")
    return sha256_bytes(data)


def package_commands(roots: dict[str,Path], output_dir: Path) -> list[tuple[str,list[str],Path,Path,Path]]:
    rows=[]
    for role in ROLE_ORDER:
        root=roots[role]
        role_dir=output_dir/"packages"/role
        archive=role_dir/"skill.zip"
        report=role_dir/"package-report.json"
        if role=="mago":
            cmd=[sys.executable,"-B",str(root/"scripts/package_skill.py"),"--target",str(root),"--output",str(archive),"--validate","--json-output",str(report)]
        elif role=="magia":
            cmd=[sys.executable,"-B",str(root/"scripts/package_skill.py"),"--target",str(root),"--output",str(archive),"--validate","--json-output",str(report)]
        else:
            cmd=[sys.executable,"-B",str(root/"scripts/package_skill.py"),"--target",str(root),"--output",str(archive),"--json-output",str(report)]
        rows.append((f"package-{role}",cmd,root,archive,report))
    return rows


def build_ledger(roots: dict[str,Path], output_dir: Path, timeout_seconds: int) -> tuple[dict[str,Any],int]:
    errors=collect_preflight_errors(roots)
    versions={}
    for role in ROLE_ORDER:
        try: versions[role]=package_identity(roots[role])[1]
        except Exception: versions[role]="unknown"
    ledger:dict[str,Any]={
        "schema_version":"1.0.0",
        "generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "roots":{k:str(v.resolve()) for k,v in roots.items()},
        "versions":versions,
        "ecosystem_release":versions.get("mago"),
        "preflight_errors":errors,
        "root_tree_hashes":{k:tree_digest(v) for k,v in roots.items() if v.is_dir()},
        "suite_digests":{k:test_suite_digest(v) for k,v in roots.items() if v.is_dir()},
        "shared_hashes":{},"packages":{},"gates":[],"status":"fail",
    }
    for rel in SHARED_REQUIRED:
        path=roots["mago"]/rel
        if path.is_file(): ledger["shared_hashes"][rel]=sha256_file(path)
    if errors:
        ledger["attestation_digest"]=attestation_digest(ledger)
        return ledger,1
    for name,cmd,cwd,archive,report in package_commands(roots,output_dir):
        gate=run_gate(name,cmd,cwd,output_dir/"logs",timeout_seconds)
        ledger["gates"].append(gate)
        role=name.split("-",1)[1]
        package={"status":gate["status"],"archive":str(archive),"report":str(report),"suite_digest":ledger["suite_digests"][role]}
        if archive.is_file():
            package.update({"archive_sha256":sha256_file(archive),"archive_size":archive.stat().st_size})
        if report.is_file():
            try:
                report_data=load_json(report)
                package.update(recursive_find(report_data,{"suite_digest","test_suite_digest","archive_sha256","file_count","tests"}))
            except Exception as exc: package["report_error"]=str(exc)
        ledger["packages"][role]=package
        if gate["status"] != "pass":
            ledger["attestation_digest"]=attestation_digest(ledger)
            return ledger,1
    m,mx,n=roots["mago"],roots["magia"],roots["nomia"]
    commands=[
      ("ecosystem-compatibility",[sys.executable,"-B",str(m/"scripts/validate_ecosystem_compatibility.py"),"--target",str(m),"--peer-root",str(mx),"--peer-root",str(n),"--json-output",str(output_dir/"ecosystem-compatibility.json")],m),
    ]
    for role,root in roots.items():
        commands.extend([
          (f"routing-{role}",[sys.executable,"-B",str(root/"scripts/validate_ecosystem_routing_contract.py"),"--target",str(root),"--json-output",str(output_dir/f"routing-{role}.json")],root),
          (f"provenance-{role}",[sys.executable,"-B",str(root/"scripts/validate_shared_contract_provenance.py"),"--target",str(root),"--json-output",str(output_dir/f"provenance-{role}.json")],root),
          (f"release-metadata-{role}",[sys.executable,"-B",str(root/"scripts/validate_ecosystem_release_metadata.py"),"--target",str(root),"--json-output",str(output_dir/f"release-metadata-{role}.json")],root),
        ])
    commands.extend([
      ("positive-flow",[sys.executable,"-B",str(m/"scripts/run_ecosystem_flow_harness.py"),"--mago",str(m),"--magia",str(mx),"--nomia",str(n),"--json-output",str(output_dir/"positive-flow.json")],m),
      ("negative-flow",[sys.executable,"-B",str(m/"scripts/run_ecosystem_negative_harness.py"),"--mago",str(m),"--magia",str(mx),"--nomia",str(n),"--json-output",str(output_dir/"negative-flow.json")],m),
    ])
    for name,cmd,cwd in commands:
        gate=run_gate(name,cmd,cwd,output_dir/"logs",timeout_seconds)
        ledger["gates"].append(gate)
        if gate["status"] != "pass":
            ledger["attestation_digest"]=attestation_digest(ledger)
            return ledger,1
    ledger["status"]="pass"
    ledger["attestation_digest"]=attestation_digest(ledger)
    return ledger,0


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    for role in ROLE_ORDER: parser.add_argument(f"--{role}",required=True)
    parser.add_argument("--output-dir",required=True)
    parser.add_argument("--json-output",required=True)
    parser.add_argument("--timeout-seconds",type=int,default=300)
    parser.add_argument("--preflight-only",action="store_true")
    args=parser.parse_args(argv)
    roots={role:Path(getattr(args,role)).resolve() for role in ROLE_ORDER}
    output=Path(args.output_dir).resolve(); output.mkdir(parents=True,exist_ok=True)
    if args.preflight_only:
        errors=collect_preflight_errors(roots)
        ledger={"schema_version":"1.0.0","generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"roots":{k:str(v) for k,v in roots.items()},"preflight_errors":errors,"status":"pass" if not errors else "fail"}
        ledger["attestation_digest"]=attestation_digest(ledger)
        rc=0 if not errors else 1
    else:
        ledger,rc=build_ledger(roots,output,args.timeout_seconds)
    atomic_write(Path(args.json_output),json.dumps(ledger,indent=2,sort_keys=True)+"\n")
    print(json.dumps(ledger,indent=2,sort_keys=True))
    return rc

if __name__ == "__main__":
    raise SystemExit(main())
