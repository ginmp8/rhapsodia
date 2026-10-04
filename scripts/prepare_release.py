#!/usr/bin/env python3
from __future__ import annotations
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*args): subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true");a=ap.parse_args()
 run("scripts/generate_marketplace_manifests.py",*(["--check"] if a.check else []))
 run("scripts/generate_agent_manifest.py","--package-version","0.4.0",*(["--check"] if a.check else []))
 run("scripts/validate_release_versions.py")
 return 0
if __name__=="__main__":raise SystemExit(main())
