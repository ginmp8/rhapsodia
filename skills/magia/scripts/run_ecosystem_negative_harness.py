#!/usr/bin/env python3
"""Run coordinated fail-closed scenarios with exact status and reason-code assertions."""
from __future__ import annotations
import argparse, copy, importlib.util, json, subprocess, sys, tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
NOW=datetime(2026,7,22,12,0,tzinfo=timezone.utc)
SPEC="spec-2026-07-22-negative-contract"
WORKFLOW="workflow-0123456789abcdef"
PRIVACY = {
    "classification": "internal",
    "contains_personal_data": False,
    "contains_third_party_data": False,
    "contains_confidential_data": False,
    "contains_secrets": False,
    "redactions_applied": [],
    "redaction_method": "none",
    "intended_audience": ["sdd-maintainers"],
    "allowed_destinations": ["local", "internal"],
    "purpose": "synthetic contract validation",
    "retention_days": 30,
    "evidence_ref_visibility": "opaque",
    "external_share_allowed": False,
}

def load_module(root:Path,alias:str):
 path=root/'scripts/ecosystem_handoff.py'; spec=importlib.util.spec_from_file_location(alias,path)
 if spec is None or spec.loader is None: raise RuntimeError(f"cannot load {path}")
 module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def resign(module,envelope):
 envelope['handoff_id']=module.handoff_id_for(envelope); return envelope

def expect(module,root,role,envelope,name,status,code,steps):
 result=module.validate_envelope(envelope,as_of=NOW,role=role,operation='consume',root=root)
 if result.get('status')!=status or code not in result.get('reason_codes',[]): raise RuntimeError(f"{name}: expected {status}/{code}, got {result}")
 steps.append({'scenario':name,'status':'pass','decision':status,'reason_code':code})

def closure_result(nomia_root,closure):
 with tempfile.TemporaryDirectory() as tmp:
  inp,out=Path(tmp)/'closure.json',Path(tmp)/'result.json'; inp.write_text(json.dumps(closure),encoding='utf-8')
  done=subprocess.run([sys.executable,'-B',str(nomia_root/'scripts/validate_governance_closure.py'),'--input',str(inp),'--json-output',str(out)],text=True,capture_output=True,check=False)
  return done.returncode,json.loads(out.read_text()) if out.exists() else {'stdout':done.stdout,'stderr':done.stderr}

def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__)
 for name in ('mago','magia','nomia'): parser.add_argument(f'--{name}',required=True)
 parser.add_argument('--json-output'); args=parser.parse_args(argv)
 roots={name:Path(getattr(args,name)).resolve() for name in ('mago','magia','nomia')}; modules={name:load_module(root,f'neg_{name}') for name,root in roots.items()}; steps=[]
 try:
  shared=('references/priority-contract.json','references/ecosystem-handoff-contract.json','references/ecosystem-compatibility.json','references/ecosystem-routing-contract.json','evals/ecosystem-routing-scenarios.json','references/ecosystem-contract-provenance.json','scripts/ecosystem_handoff.py')
  for rel in shared:
   if len({(root/rel).read_bytes() for root in roots.values()})!=1: raise RuntimeError(f'shared file differs: {rel}')
  payload={'feature_key':'negative-contract','outcome':'exercise fail-closed behavior','scope_summary':'negative fixture','owner':'delivery-role','business_priority':{'level':'high','owner':'nomia','source':'fixture://governance','observed_at':NOW.isoformat()},'dependencies':[],'governance_readiness':'ready','candidate_spec_id':SPEC,'candidate_spec_id_provenance':'fixture://mago-registry'}
  current=modules['nomia'].build_envelope(direction='nomia_to_mago',payload=payload,source='fixture://nomia',authority='nomia',evidence_refs=['fixture://decision'],observed_at=NOW.isoformat(),freshness_days=30,workflow_id=WORKFLOW,privacy_handling=PRIVACY,root=roots['nomia'])
  mixed=resign(modules['nomia'],copy.deepcopy(current)); mixed['ecosystem_release']='1.6.0'; mixed['source_version']='1.6.0'; resign(modules['nomia'],mixed); expect(modules['mago'],roots['mago'],'mago',mixed,'mixed-version-rejected','rejected','HANDOFF_INVALID_ECOSYSTEM_RELEASE',steps)
  missing_privacy=copy.deepcopy(current); del missing_privacy['privacy_handling']; resign(modules['nomia'],missing_privacy); expect(modules['mago'],roots['mago'],'mago',missing_privacy,'privacy-metadata-required','rejected','HANDOFF_MISSING_FIELD',steps)
  secret_case=copy.deepcopy(current); secret_case['privacy_handling']['contains_secrets']=True; resign(modules['nomia'],secret_case); expect(modules['mago'],roots['mago'],'mago',secret_case,'secret-transport-rejected','rejected','HANDOFF_SECRET_EXPOSURE',steps)
  public_bad=copy.deepcopy(current); public_bad['privacy_handling']['allowed_destinations']=['public']; public_bad['privacy_handling']['external_share_allowed']=True; resign(modules['nomia'],public_bad); expect(modules['mago'],roots['mago'],'mago',public_bad,'confidential-public-destination-rejected','rejected','HANDOFF_PUBLIC_DESTINATION_DENIED',steps)
  lineage=copy.deepcopy(current); lineage['workflow_id']='workflow-invalid'; resign(modules['nomia'],lineage); expect(modules['mago'],roots['mago'],'mago',lineage,'invalid-workflow-rejected','rejected','HANDOFF_INVALID_WORKFLOW_ID',steps)
  stale=copy.deepcopy(current); stale['observed_at']=(NOW-timedelta(days=10)).isoformat(); stale['freshness']={'max_age_days':1}; resign(modules['nomia'],stale); expect(modules['mago'],roots['mago'],'mago',stale,'stale-evidence','stale','HANDOFF_STALE',steps)
  future=copy.deepcopy(current); future['observed_at']=(NOW+timedelta(minutes=10)).isoformat(); resign(modules['nomia'],future); expect(modules['mago'],roots['mago'],'mago',future,'future-evidence-rejected','rejected','HANDOFF_FUTURE_OBSERVED_AT',steps)
  wrong=copy.deepcopy(current); wrong['provenance']['authority']='magia'; resign(modules['nomia'],wrong); expect(modules['mago'],roots['mago'],'mago',wrong,'wrong-authority-rejected','rejected','HANDOFF_INVALID_PROVENANCE_AUTHORITY',steps)
  generic=copy.deepcopy(current); generic['payload']['priority']='high'; resign(modules['nomia'],generic); expect(modules['mago'],roots['mago'],'mago',generic,'generic-priority-rejected','rejected','HANDOFF_OUTSIDE_AUTHORITY',steps)
  unknown=copy.deepcopy(current); unknown['payload']['solution_outline']={}; resign(modules['nomia'],unknown); expect(modules['mago'],roots['mago'],'mago',unknown,'unknown-payload-rejected','rejected','HANDOFF_UNKNOWN_PAYLOAD_FIELD',steps)
  empty=copy.deepcopy(current); empty['provenance']['evidence_refs']=[]; resign(modules['nomia'],empty); expect(modules['mago'],roots['mago'],'mago',empty,'empty-evidence-rejected','rejected','HANDOFF_EMPTY_EVIDENCE_REFS',steps)
  bad=copy.deepcopy(current); bad['payload']['candidate_spec_id']='spec002'; resign(modules['nomia'],bad); expect(modules['mago'],roots['mago'],'mago',bad,'legacy-identity-rejected','rejected','HANDOFF_INVALID_CANDIDATE_SPEC_ID',steps)
  conflict=copy.deepcopy(current); conflict['conflicts']=['sources disagree']; resign(modules['nomia'],conflict); expect(modules['mago'],roots['mago'],'mago',conflict,'conflict-evidence','conflicting','HANDOFF_CONFLICTING',steps)
  draft_payload=copy.deepcopy(payload); draft_payload['governance_readiness']='draft'; draft=modules['nomia'].build_envelope(direction='nomia_to_mago',payload=draft_payload,source='fixture://draft',authority='nomia',evidence_refs=['fixture://draft'],observed_at=NOW.isoformat(),freshness_days=30,workflow_id=WORKFLOW,privacy_handling=PRIVACY,root=roots['nomia'])
  with tempfile.TemporaryDirectory() as tmp:
   inp=Path(tmp)/'draft.json'; inp.write_text(json.dumps(draft),encoding='utf-8'); base=[sys.executable,'-B',str(roots['mago']/'scripts/ecosystem_handoff.py'),'validate','--input',str(inp),'--operation','consume','--as-of',NOW.isoformat()]
   blocked=subprocess.run(base,text=True,capture_output=True,check=False); allowed=subprocess.run(base+['--allow-draft'],text=True,capture_output=True,check=False)
   if blocked.returncode!=3 or allowed.returncode!=0: raise RuntimeError(f'draft exit matrix failed: {blocked.returncode}/{allowed.returncode}')
  steps.append({'scenario':'draft-non-actionable-by-default','status':'pass','decision':'draft','default_exit':3,'inspection_exit':0})
  base_closure={'governance_status':'closed','governance_lifecycle':'close','decision':{'state':'accepted','authority':'nomia','evidence':['fixture://decision/close']},'technical_state':{'planning':{'state':'complete','source':'fixture://mago','observed_at':NOW.isoformat()},'execution':{'state':'complete','source':'fixture://magia','observed_at':NOW.isoformat()},'validation':{'state':'passed','source':'fixture://magia','observed_at':NOW.isoformat()}},'release':{'state':'closed','released_at':NOW.isoformat(),'evidence':['fixture://external-release']}}
  failed=copy.deepcopy(base_closure); failed['technical_state']['validation']['state']='failed'; rc,res=closure_result(roots['nomia'],failed)
  if rc==0: raise RuntimeError('closure accepted failed validation')
  steps.append({'scenario':'closure-denied-after-failed-validation','status':'pass','decision':res.get('status','rejected')})
  missing=copy.deepcopy(base_closure); missing['release']['evidence']=[]; rc,res=closure_result(roots['nomia'],missing)
  if rc==0: raise RuntimeError('closure accepted missing external release evidence')
  steps.append({'scenario':'closure-denied-without-release-evidence','status':'pass','decision':res.get('status','rejected')})
  result={'status':'pass','ecosystem_release':(roots['mago']/'VERSION').read_text().strip(),'scenario':'ecosystem-fail-closed-suite','steps':steps,'limitations':['Structural contract fixtures; live-model routing and production interruption are not measured.']}; rc=0
 except Exception as exc:
  result={'status':'fail','scenario':'ecosystem-fail-closed-suite','steps':steps,'error':str(exc)}; rc=1
 text=json.dumps(result,indent=2,sort_keys=True)+'\n'
 if args.json_output: Path(args.json_output).write_text(text,encoding='utf-8')
 print(text,end=''); return rc
if __name__=='__main__': raise SystemExit(main())
