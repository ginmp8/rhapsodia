from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path

_SHA256_REF_RE=re.compile(r'^sha256:[0-9a-fA-F]{64}$')
def _nonempty(v):return isinstance(v,str) and bool(v.strip())
def validate(d):
 e=[];version=d.get('contract_version',1);runs=d.get('runs')
 if version not in {1,2,3,4}:e.append('contract_version:unsupported')
 if not isinstance(runs,list) or not runs:return sorted(set(e+['runs:invalid']))
 cand=set();candidate_identity=set();runids=set();work=set();trace=set();trace_manifest=set();trace_manifest_sha=set();refs={}
 comparable=('evaluator_id','scenario_set_id') + (('evaluation_policy_id',) if version>=2 else tuple())
 for i,r in enumerate(runs):
  required=['candidate_id','candidate_identity','run_id','work_dir','evaluator_id','scenario_set_id']
  if version>=2:required += ['evaluation_policy_id','trace_id']
  if version>=3:required += ['trace_manifest_id','trace_manifest_sha256']
  for k in required:
   if not _nonempty(r.get(k)):e.append(f'run[{i}].{k}:missing')
  if r.get('candidate_id') in cand:e.append('candidate_id:duplicate')
  cand.add(r.get('candidate_id'))
  if version>=3:
   if r.get('candidate_identity') in candidate_identity:e.append('candidate_identity:duplicate')
   candidate_identity.add(r.get('candidate_identity'))
  if r.get('run_id') in runids:e.append('run_id:duplicate')
  runids.add(r.get('run_id'))
  if r.get('work_dir') in work:e.append('work_dir:shared')
  work.add(r.get('work_dir'))
  if version>=2:
   if r.get('trace_id') in trace:e.append('trace_id:duplicate')
   trace.add(r.get('trace_id'))
  if version>=3:
   if r.get('trace_manifest_id') in trace_manifest:e.append('trace_manifest_id:duplicate')
   trace_manifest.add(r.get('trace_manifest_id'))
   trace_hash=r.get('trace_manifest_sha256')
   if version>=4 and _nonempty(trace_hash) and not _SHA256_REF_RE.fullmatch(trace_hash):e.append(f'run[{i}].trace_manifest_sha256:invalid')
   normalized_hash=trace_hash.lower() if isinstance(trace_hash,str) else trace_hash
   if normalized_hash in trace_manifest_sha:e.append('trace_manifest_sha256:duplicate')
   trace_manifest_sha.add(normalized_hash)
  for k in comparable:
   if r.get(k) and k not in refs:refs[k]=r[k]
   elif r.get(k) and refs[k]!=r[k]:e.append(f'comparability:{k}:mismatch')
  if r.get('holdout_blind') is True and r.get('candidate_saw_evaluator_only_assets') is not False:e.append(f'run[{i}]:holdout_leakage')
 return sorted(set(e))
def main():
 p=argparse.ArgumentParser();p.add_argument('manifest');a=p.parse_args();d=json.loads(Path(a.manifest).read_text());e=validate(d);print(json.dumps({'status':'pass' if not e else 'fail','contract_version':d.get('contract_version',1),'errors':e},indent=2,sort_keys=True));return 0 if not e else 2
if __name__=='__main__':sys.exit(main())
