#!/usr/bin/env python3
"""Generate or verify the deterministic Agent-layer MANIFEST.json."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"MANIFEST.json"
AGENT_SURFACE=(
"LICENSE","README.md","agents/magia.agent.md","agents/mago.agent.md","agents/nomia.agent.md",
"agents/rhapsodia-analyst.agent.md","agents/rhapsodia-supervisor.agent.md","agents/rhapsodia-verifier.agent.md",
"agents/rhapsodia-workspace.agent.md","docs/agents/ARCHITECTURE.md","docs/agents/ARTIFACT-ORCHESTRATION.md",
"docs/agents/SOURCES.md","docs/agents/contracts/rhapsodia-agent-system.json",
"scripts/install_agents.py","scripts/validate_agents.py","tests/agent-scenarios.json","tests/test_install_agents.py","tests/test_validate_agents.py")
def sha256(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def render(version:str)->dict:
 entries=[]
 for rel in AGENT_SURFACE:
  p=ROOT/rel
  if not p.is_file():raise FileNotFoundError(rel)
  entries.append({"path":rel,"sha256":sha256(p),"size":p.stat().st_size})
 return {"files":entries,"manifest_version":1,"package":"rhapsodia-agents-vscode","package_version":version}
def main()->int:
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--package-version",default="0.4.0");ap.add_argument("--check",action="store_true");a=ap.parse_args()
 expected=json.dumps(render(a.package_version),indent=2,ensure_ascii=False)+"\n"
 if a.check:
  if not MANIFEST.is_file() or MANIFEST.read_text(encoding="utf-8")!=expected:
   print("MANIFEST.json is out of sync");return 1
  print("MANIFEST.json is in sync");return 0
 MANIFEST.write_text(expected,encoding="utf-8");print("generated MANIFEST.json");return 0
if __name__=="__main__":raise SystemExit(main())
