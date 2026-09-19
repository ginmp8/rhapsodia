#!/usr/bin/env python3
"""Record and validate a local, authority-neutral ecosystem handoff ledger with explicit last-known-good recovery."""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import ecosystem_handoff
SCHEMA_VERSION="1.0.0"
STATES=("created","accepted","consumed","superseded","replayed")
ALLOWED={None:{"created"},"created":{"accepted","superseded"},"accepted":{"consumed","superseded"},"consumed":{"replayed","superseded"},"replayed":{"consumed","superseded"},"superseded":set()}

def sha256_bytes(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def last_good_path(path:Path)->Path: return path.resolve().with_name(path.name+".last-good")
def _atomic_bytes(path:Path,data:bytes)->None:
 path=path.resolve(); path.parent.mkdir(parents=True,exist_ok=True); fd,name=tempfile.mkstemp(prefix=f".{path.name}.",suffix=".tmp",dir=str(path.parent))
 try:
  with os.fdopen(fd,"wb") as stream: stream.write(data); stream.flush(); os.fsync(stream.fileno())
  os.replace(name,path)
 finally:
  if os.path.exists(name): os.unlink(name)
def atomic_write(path:Path,data:dict[str,Any])->None: _atomic_bytes(path,(json.dumps(data,indent=2,sort_keys=True)+"\n").encode())
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
  required={"handoff_id","direction","state","recorded_at","source_skill","target_skill","attempt"}; missing=required-set(event)
  if missing: errors.append(f"events[{i}] missing {sorted(missing)}"); continue
  hid=str(event["handoff_id"]); state=str(event["state"])
  if ecosystem_handoff.HANDOFF_ID_RE.fullmatch(hid) is None: errors.append(f"events[{i}] invalid handoff_id")
  if state not in STATES: errors.append(f"events[{i}] invalid state")
  key=(hid,state,event.get("attempt"))
  if key in seen: errors.append(f"events[{i}] duplicate event")
  seen.add(key); previous=current.get(hid)
  if state not in ALLOWED.get(previous,set()): errors.append(f"events[{i}] invalid transition {previous}->{state}")
  else: current[hid]=state
  if not isinstance(event.get("attempt"),int) or event["attempt"]<1: errors.append(f"events[{i}] invalid attempt")
 return errors
def record(ledger:dict[str,Any],envelope:dict[str,Any],state:str,recorded_at:str,*,as_of:datetime|None=None)->tuple[dict[str,Any],bool]:
 if as_of is None: as_of=ecosystem_handoff.parse_time(recorded_at)
 result=ecosystem_handoff.validate_envelope(envelope,operation="any",as_of=as_of)
 if result["status"] not in {"accepted","draft"}: raise ValueError("handoff is not structurally valid: "+"; ".join(result["reasons"]))
 if envelope["workflow_id"]!=ledger["workflow_id"]: raise ValueError("handoff workflow_id does not match ledger")
 if state not in STATES: raise ValueError("invalid ledger state")
 events=ledger["events"]; hid=envelope["handoff_id"]; previous=next((e["state"] for e in reversed(events) if e["handoff_id"]==hid),None)
 if previous==state: return ledger,True
 if state not in ALLOWED.get(previous,set()): raise ValueError(f"invalid transition {previous}->{state}")
 attempts=[e["attempt"] for e in events if e["handoff_id"]==hid]; attempt=max(attempts,default=1)+(1 if state=="replayed" else 0)
 event={"handoff_id":hid,"direction":envelope["direction"],"state":state,"recorded_at":recorded_at,"source_skill":envelope["source_skill"],"target_skill":envelope["target_skill"],"attempt":attempt}
 if envelope.get("causation_id"): event["causation_id"]=envelope["causation_id"]
 events.append(event); errors=validate(ledger)
 if errors: events.pop(); raise ValueError("invalid ledger after record: "+"; ".join(errors))
 return ledger,False
def commit_ledger(path:Path,data:dict[str,Any])->dict[str,Any]:
 errors=validate(data)
 if errors: raise ValueError("candidate ledger invalid: "+"; ".join(errors))
 path=path.resolve(); before=None; lkg=None
 if path.exists():
  current=load(path); current_errors=validate(current)
  if current_errors: raise ValueError("existing ledger invalid; recover or repair before overwrite")
  before=path.read_bytes(); lkg=last_good_path(path); _atomic_bytes(lkg,before)
 candidate=(json.dumps(data,indent=2,sort_keys=True)+"\n").encode(); _atomic_bytes(path,candidate)
 try:
  verify=load(path); after_errors=validate(verify)
  if after_errors: raise ValueError("committed ledger failed verification")
 except Exception:
  if before is not None: _atomic_bytes(path,before)
  raise
 return {"status":"pass","stage":"commit","ledger":str(path),"before_sha256":sha256_bytes(before) if before else None,"after_sha256":sha256_bytes(candidate),"last_known_good":str(lkg) if lkg else None,"last_known_good_sha256":sha256_bytes(before) if before else None}
def recover_ledger(path:Path)->dict[str,Any]:
 path=path.resolve(); lkg=last_good_path(path)
 if not lkg.is_file(): raise ValueError("last-known-good ledger is unavailable")
 data=json.loads(lkg.read_text(encoding="utf-8")); errors=validate(data)
 if errors: raise ValueError("last-known-good ledger is invalid: "+"; ".join(errors))
 previous=path.read_bytes() if path.exists() else None; restored=lkg.read_bytes(); _atomic_bytes(path,restored); verify=load(path); errs=validate(verify)
 if errs:
  if previous is not None: _atomic_bytes(path,previous)
  raise ValueError("recovery verification failed")
 return {"status":"pass","stage":"recovery","ledger":str(path),"restored_from":str(lkg),"restored_sha256":sha256_bytes(restored)}
def main(argv=None)->int:
 p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest="command",required=True)
 init=sub.add_parser("init"); init.add_argument("--ledger",required=True); init.add_argument("--workflow-id",required=True); init.add_argument("--receipt")
 add=sub.add_parser("record"); add.add_argument("--ledger",required=True); add.add_argument("--handoff",required=True); add.add_argument("--state",choices=STATES,required=True); add.add_argument("--recorded-at",default=datetime.now(timezone.utc).replace(microsecond=0).isoformat()); add.add_argument("--receipt")
 check=sub.add_parser("validate"); check.add_argument("--ledger",required=True); check.add_argument("--json-output")
 recover=sub.add_parser("recover"); recover.add_argument("--ledger",required=True); recover.add_argument("--receipt")
 args=p.parse_args(argv)
 try:
  path=Path(args.ledger)
  if args.command=="init": out=commit_ledger(path,empty_ledger(args.workflow_id))
  elif args.command=="record":
   env=json.loads(Path(args.handoff).read_text(encoding="utf-8")); data=load(path,env.get("workflow_id")); data,idempotent=record(data,env,args.state,args.recorded_at)
   if idempotent: out={"status":"pass","stage":"record","idempotent":True,"state":args.state,"handoff_id":env["handoff_id"],"ledger":str(path.resolve())}
   else: out=commit_ledger(path,data)|{"stage":"record","idempotent":False,"state":args.state,"handoff_id":env["handoff_id"]}
  elif args.command=="recover": out=recover_ledger(path)
  else:
   data=load(path); errors=validate(data); lkg=last_good_path(path); out={"status":"pass" if not errors else "fail","errors":errors,"workflow_id":data.get("workflow_id"),"event_count":len(data.get("events") or []),"ledger_sha256":sha256_bytes(path.read_bytes()),"last_known_good":str(lkg) if lkg.is_file() else None,"last_known_good_sha256":sha256_bytes(lkg.read_bytes()) if lkg.is_file() else None}
  receipt=getattr(args,"receipt",None)
  if receipt: atomic_write(Path(receipt),out)
  text=json.dumps(out,indent=2,sort_keys=True)+"\n"
  if getattr(args,"json_output",None): atomic_write(Path(args.json_output),out)
  print(text,end=""); return 0 if out["status"]=="pass" else 1
 except (OSError,ValueError,json.JSONDecodeError) as exc:
  print(json.dumps({"status":"error","stage":"operation","error":str(exc)},indent=2,sort_keys=True)); return 2
if __name__=="__main__": raise SystemExit(main())
