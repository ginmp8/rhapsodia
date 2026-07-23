#!/usr/bin/env python3
"""Derive and validate compact privacy lineage for durable SDD artifacts."""
import argparse,json,re
from pathlib import Path
try: import yaml
except ImportError: yaml=None
ROOT=Path(__file__).resolve().parents[1]; HID=re.compile(r'^handoff-[0-9a-f]{16}$')
LABELS={'classification':'Classification','contains_personal_data':'Contains Personal Data','contains_third_party_data':'Contains Third-Party Data','contains_confidential_data':'Contains Confidential Data','contains_secrets':'Contains Secrets','redactions_applied':'Redactions Applied','redaction_method':'Redaction Method','intended_audience':'Intended Audience','allowed_destinations':'Allowed Destinations','purpose':'Purpose','retention_days':'Retention Days','external_share_allowed':'External Share Allowed','source_handoff_id':'Source Handoff ID','source_reference':'Source Reference','transformations':'Transformations'}
def contract(root=ROOT): return json.loads((root/'references/artifact-privacy-contract.json').read_text())
def derive(env):
 p=env.get('privacy_handling') or {}; hid=env.get('handoff_id'); keys=('classification','contains_personal_data','contains_third_party_data','contains_confidential_data','contains_secrets','redactions_applied','redaction_method','intended_audience','allowed_destinations','purpose','retention_days','external_share_allowed')
 out={k:p.get(k) for k in keys}; out.update(source_handoff_id=hid,source_reference=f'handoff:{hid}' if hid else str((env.get('provenance') or {}).get('source') or 'unknown'),transformations=['inherited-from-handoff']); return out
def validate_block(v,root=ROOT):
 c=contract(root); e=[]
 if not isinstance(v,dict): return ['privacy metadata must be a mapping']
 req=set(c['required_fields']); e += [f'missing privacy.{k}' for k in sorted(req-set(v))]+[f'unknown privacy.{k}' for k in sorted(set(v)-req)]
 if v.get('classification') not in c['classification']: e.append('invalid privacy.classification')
 if v.get('redaction_method') not in c['redaction_method']: e.append('invalid privacy.redaction_method')
 for k in ('contains_personal_data','contains_third_party_data','contains_confidential_data','contains_secrets','external_share_allowed'):
  if not isinstance(v.get(k),bool): e.append(f'invalid privacy.{k}')
 for k in ('redactions_applied','intended_audience','allowed_destinations','transformations'):
  if not isinstance(v.get(k),list) or any(not isinstance(x,str) or not x.strip() for x in v.get(k,[])): e.append(f'invalid privacy.{k}')
 if isinstance(v.get('allowed_destinations'),list) and set(v['allowed_destinations'])-set(c['allowed_destinations']): e.append('invalid privacy.allowed_destinations')
 d=v.get('retention_days')
 if isinstance(d,bool) or not isinstance(d,int) or not 0<=d<=c['max_retention_days']: e.append('invalid privacy.retention_days')
 if not isinstance(v.get('purpose'),str) or not v['purpose'].strip(): e.append('invalid privacy.purpose')
 hid=v.get('source_handoff_id')
 if hid not in (None,'') and not HID.fullmatch(str(hid)): e.append('invalid privacy.source_handoff_id')
 if hid in (None,'') and not str(v.get('source_reference') or '').strip(): e.append('privacy lineage requires source_handoff_id or source_reference')
 if v.get('contains_secrets') is True: e.append('privacy secrets must be removed')
 sensitive=any(v.get(k) is True for k in ('contains_personal_data','contains_third_party_data','contains_confidential_data'))
 if sensitive and (not v.get('redactions_applied') or v.get('redaction_method')=='none'): e.append('privacy sensitive content requires redaction')
 dest=set(v.get('allowed_destinations') or [])
 if dest&{'approved-vendor','public'} and v.get('external_share_allowed') is not True: e.append('privacy external destination denied')
 if 'public' in dest and (v.get('classification')!='public' or sensitive): e.append('privacy public projection denied')
 return e
def parse_md(text):
 out={}
 for k,label in LABELS.items():
  m=re.search(rf'^- {re.escape(label)}:\s*(.+?)\s*$',text,re.M)
  if not m: continue
  x=m.group(1).strip().strip('`')
  if x.lower() in {'true','false'}: out[k]=x.lower()=='true'
  elif k=='retention_days' and x.isdigit(): out[k]=int(x)
  elif k in {'redactions_applied','intended_audience','allowed_destinations','transformations'}: out[k]=[i.strip() for i in x.strip('[]').split(',') if i.strip()]
  else: out[k]=None if k=='source_handoff_id' and x.lower() in {'null','none'} else x
 return out
def template_errors(text): return ([] if '## Privacy and Sharing' in text else ['missing Privacy and Sharing heading'])+[f'missing privacy template field {x}' for x in LABELS.values() if not re.search(rf'^- {re.escape(x)}:\s*.+$',text,re.M)]
markdown_template_errors=template_errors
def load_artifact(p):
 text=p.read_text(); suffix=p.suffix.lower()
 if suffix=='.json':
  data=json.loads(text); return data.get('privacy',data)
 if suffix in {'.yaml','.yml'}:
  if yaml is None: raise RuntimeError('PyYAML is required')
  data=yaml.safe_load(text); return data.get('privacy') if isinstance(data,dict) else None
 return parse_md(text)
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__); p.add_argument('path'); p.add_argument('--template',action='store_true'); p.add_argument('--derive-handoff',action='store_true'); p.add_argument('--output'); a=p.parse_args(argv); path=Path(a.path).resolve()
 if a.derive_handoff:
  value=derive(json.loads(path.read_text())); errors=validate_block(value)
  if not errors and a.output: Path(a.output).write_text(json.dumps({'privacy':value},indent=2,sort_keys=True)+'\n')
 elif a.template and path.suffix.lower()=='.md': errors=template_errors(path.read_text())
 elif a.template:
  if yaml is None: raise SystemExit('PyYAML is required')
  data=yaml.safe_load(path.read_text()); block=data.get('privacy') if isinstance(data,dict) else None; errors=[] if isinstance(block,dict) and set(contract()['required_fields'])<=set(block) else ['template privacy block is incomplete']
 else: errors=validate_block(load_artifact(path))
 for e in errors: print(f'ERROR: {e}')
 if errors: return 1
 print(f'OK: artifact privacy validated: {path}'); return 0
if __name__=='__main__': raise SystemExit(main())
