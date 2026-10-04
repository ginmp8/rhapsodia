#!/usr/bin/env python3
"""Data-only packaging of Rhapsodia Workspace with external validation evidence."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import zipfile
import sys
LOCAL_SCRIPTS = Path(__file__).resolve().parent
if str(LOCAL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(LOCAL_SCRIPTS))
from package_evidence import deterministic_zip, outside, atomic_bytes, json_bytes

def validate_archive(path):
    errors=[]
    with zipfile.ZipFile(path) as archive:
        names=archive.namelist()
        if len(names)!=len(set(names)):errors.append('duplicate archive entries')
        if any(not n.startswith('rhapsodia-workspace/') or '..' in n.split('/') or n.startswith('/') for n in names):errors.append('unsafe archive path')
        for required in ['SKILL.md','VERSION','scripts/workspace.py','assets/workspace.html','references/artifact-envelope.schema.json']:
            if 'rhapsodia-workspace/'+required not in names:errors.append('missing '+required)
    return {'status':'fail' if errors else 'pass','errors':errors}

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Data-only package construction; external executed evidence is mandatory.")
    parser.add_argument("--target")
    parser.add_argument("--output")
    parser.add_argument("--validation-evidence", type=Path)
    parser.add_argument("--validate", action="store_true", help="Retained compatibility flag; evidence is always required.")
    parser.add_argument("--validate-only", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.validate_only:
            result = validate_archive(args.validate_only)
            if isinstance(result, list):
                result = {"status": "fail" if result else "pass", "errors": result}
        else:
            if not args.target or not args.output:
                parser.error("--target and --output are required")
            target, output = Path(args.target), Path(args.output)
            if args.json_output:
                report = outside(target, args.json_output)
                if report == output.resolve() or (args.validation_evidence and report == args.validation_evidence.resolve()):
                    raise ValueError("report must not alias archive or validation evidence")
            info = deterministic_zip(target, output, evidence=args.validation_evidence, archive_validator=validate_archive)
            result = {"status": "pass", "package": info}
        if args.json_output:
            if args.validate_only and args.json_output.resolve() == args.validate_only.resolve():
                raise ValueError("report must not overwrite inspected archive")
            atomic_bytes(args.json_output, json_bytes(result))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result.get("status") == "pass" else 1
    except (OSError, ValueError, TypeError, KeyError, zipfile.BadZipFile) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
