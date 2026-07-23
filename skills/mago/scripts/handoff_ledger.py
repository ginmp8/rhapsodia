#!/usr/bin/env python3
"""Record and validate a local, authority-neutral ecosystem handoff ledger."""
from __future__ import annotations
import argparse, json, os, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import ecosystem_handoff

SCHEMA_VERSION="1.0.0"
STATES=("created","accepted","consumed","superseded","replayed")
ALLOWED={None:{"created"},"created":{"accepted","superseded"},"accepted":{"consumed","superseded"},"consumed":{"replayed","superseded"},"replayed":{"consumed","superseded"},"superseded":set()}

def atomic_write(path:Path,data:dict[str,Any])->None:
 path=path.resolve(); path.parent.mkdir(parents=True,exist_ok=True)
 fd,name=tempfile.mkstemp(prefix=f".{path.name}.",suffix=".tmp",dir=str(path.parent))
 try:
  with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as stream:
   json.dump(data,stream,indent=2,sort_keys=True); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
  os.replace(name,path)
 finally:
  if os.path.exists(name): os.unlink(name)

def empty_ledger(workflow_id:str)->dict[str,Any]:
 if ecosystem_handoff.WORKFLOW_ID_RE.fullmatch(workflow_id) is None: raise ValueError("invalid workflow_id")
 return {"schema_version":SCHEMA_VERSION,"workflow_id":workflow_id,"authority":"transport_metadata_only","events":[]}

def load(path:Path,workflow_id:str|None=None)->dict[str,Any]:
 if not path.exists():
  if workflow_id is None: raise ValueError("ledger does not exist and workflow_id was not supplied")
  return empty_ledger(workflow_id)
 value=json.loads(path.read_text(encoding="utf-8"))
 if not isinstance(value,dict): raise ValueError("ledger must be an object")
 return value

def validate(ledger:Any)->list[str]:
 errors=[]
 if not isinstance(ledger,dict): return ["ledger must be an object"]
 if ledger.get("schema_version")!=SCHEMA_VERSION: errors.append("invalid ledger schema_version")
 workflow=str(ledger.get("workflow_id") or "")
 if ecosystem_handoff.WORKFLOW_ID_RE.fullmatch(workflow) is None: errors.append("invalid ledger workflow_id")
 if ledger.get("authority")!="transport_metadata_only": errors.append("ledger must be authority-neutral")
 events=ledger.get("events")
 if not isinstance(events,list): return errors+["events must be a list"]
 current:dict[str,str]={}; seen=set()
 for i,event in enumerate(events):
  if not isinstance(event,dict): errors.append(f"events[{i}] must be an object"); continue
  required={"handoff_id","direction","state","recorded_at","source_skill","target_skill","attempt"}
  missing=required-set(event)
  if missing: errors.append(f"events[{i}] missing {sorted(missing)}"); continue
  hid=str(event["handoff_id"]); state=str(event["state"])
  if ecosystem_handoff.HANDOFF_ID_RE.fullmatch(hid) is None: errors.append(f"events[{i}] invalid handoff_id")
  if state not in STATES: errors.append(f"events[{i}] invalid state")
  key=(hid,state,event.get("attempt"))
  if key in seen: errors.append(f"events[{i}] duplicate event")
  seen.add(key)
  previous=current.get(hid)
  if state not in ALLOWED.get(previous,set()): errors.append(f"events[{i}] invalid transition {previous}->{state}")
  else: current[hid]=state
  if not isinstance(event.get("attempt"),int) or event["attempt"]<1: errors.append(f"events[{i}] invalid attempt")
 return errors

def record(ledger:dict[str,Any],envelope:dict[str,Any],state:str,recorded_at:str)->tuple[dict[str,Any],bool]:
 result=ecosystem_handoff.validate_envelope(envelope,operation="any")
 if result["status"] not in {"accepted","draft"}: raise ValueError("handoff is not structurally valid: "+"; ".join(result["reasons"]))
 if envelope["workflow_id"]!=ledger["workflow_id"]: raise ValueError("handoff workflow_id does not match ledger")
 if state not in STATES: raise ValueError("invalid ledger state")
 events=ledger["events"]; hid=envelope["handoff_id"]
 previous=next((e["state"] for e in reversed(events) if e["handoff_id"]==hid),None)
 if previous==state: return ledger,True
 if state not in ALLOWED.get(previous,set()): raise ValueError(f"invalid transition {previous}->{state}")
 attempts=[e["attempt"] for e in events if e["handoff_id"]==hid]
 attempt=max(attempts,default=1)+(1 if state=="replayed" else 0)
 event={"handoff_id":hid,"direction":envelope["direction"],"state":state,"recorded_at":recorded_at,"source_skill":envelope["source_skill"],"target_skill":envelope["target_skill"],"attempt":attempt}
 if envelope.get("causation_id"): event["causation_id"]=envelope["causation_id"]
 events.append(event)
 errors=validate(ledger)
 if errors: events.pop(); raise ValueError("invalid ledger after record: "+"; ".join(errors))
 return ledger,False

def main(argv=None)->int:
 p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest="command",required=True)
 init=sub.add_parser("init"); init.add_argument("--ledger",required=True); init.add_argument("--workflow-id",required=True)
 add=sub.add_parser("record"); add.add_argument("--ledger",required=True); add.add_argument("--handoff",required=True); add.add_argument("--state",choices=STATES,required=True); add.add_argument("--recorded-at",default=datetime.now(timezone.utc).replace(microsecond=0).isoformat())
 check=sub.add_parser("validate"); check.add_argument("--ledger",required=True); check.add_argument("--json-output")
 args=p.parse_args(argv)
 try:
  path=Path(args.ledger)
  if args.command=="init": atomic_write(path,empty_ledger(args.workflow_id)); out={"status":"pass","ledger":str(path.resolve())}
  elif args.command=="record":
   env=json.loads(Path(args.handoff).read_text(encoding="utf-8")); data=load(path,env.get("workflow_id")); data,idempotent=record(data,env,args.state,args.recorded_at); atomic_write(path,data); out={"status":"pass","idempotent":idempotent,"state":args.state,"handoff_id":env["handoff_id"]}
  else:
   data=load(path); errors=validate(data); out={"status":"pass" if not errors else "fail","errors":errors,"workflow_id":data.get("workflow_id"),"event_count":len(data.get("events") or [])}
  text=json.dumps(out,indent=2,sort_keys=True)+"\n"
  if getattr(args,"json_output",None): atomic_write(Path(args.json_output),out)
  print(text,end=""); return 0 if out["status"]=="pass" else 1
 except (OSError,ValueError,json.JSONDecodeError) as exc:
  print(json.dumps({"status":"error","error":str(exc)},indent=2,sort_keys=True)); return 2
if __name__=="__main__": raise SystemExit(main())
