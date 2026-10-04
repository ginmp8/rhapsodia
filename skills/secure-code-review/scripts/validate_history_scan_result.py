#!/usr/bin/env python3
"""Validate Secure Code Review Git-history scanner JSON."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

SEV=('critical','high','medium','low'); ORDER={v:i for i,v in enumerate(SEV)}; CONF={'confirmed','likely','possible'}
RAW=[
 re.compile(r'\bgh[pousr]_[A-Za-z0-9_]{20,}\b'), re.compile(r'\bxox[baprs]-[A-Za-z0-9-]{10,}\b'),
 re.compile(r'\bAIza[0-9A-Za-z\-_]{20,}\b'), re.compile(r'\bsk_live_[0-9A-Za-z]{16,}\b'),
 re.compile(r'(?i)bearer\s+[A-Za-z0-9._\-+/=]{8,}'),
 re.compile(r'\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|mssql|amqp)://[^\s:@/]+:[^\s@/]+@')]
REQ={'schema_version','status','scope','target','revision','summary','scan_stats','findings'}
FREQ={'id','commit','path','line','severity','confidence','rule','evidence'}

def check(code,ok,subject,evidence): return {'code':code,'status':'pass' if ok else 'fail','subject':subject,'evidence':evidence,'supported_fixes':[]}

def main():
 ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('result'); ap.add_argument('--json',dest='json_out'); a=ap.parse_args(); checks=[]
 try: d=json.loads(Path(a.result).read_text(encoding='utf-8')); checks.append(check('json/parse',True,a.result,{}))
 except Exception as e: d=None; checks.append(check('json/parse',False,a.result,{'error':str(e)}))
 if isinstance(d,dict):
  checks.append(check('schema/top-fields',REQ<=set(d),a.result,{'missing':sorted(REQ-set(d))}))
  checks.append(check('schema/version',d.get('schema_version')==1,'schema_version',{'actual':d.get('schema_version')}))
  checks.append(check('schema/scope',d.get('scope')=='git-history','scope',{'actual':d.get('scope')}))
  checks.append(check('schema/status',d.get('status')=='complete','status',{'actual':d.get('status')}))
  fs=d.get('findings') if isinstance(d.get('findings'),list) else []
  bad=[i for i,f in enumerate(fs) if not isinstance(f,dict) or not FREQ<=set(f) or f.get('severity') not in ORDER or f.get('confidence') not in CONF or not isinstance(f.get('line'),int) or f.get('line',0)<1]
  checks.append(check('finding/shape',not bad,'findings',bad[:20]))
  ids=[f.get('id') for f in fs if isinstance(f,dict)]; ok=len(ids)==len(set(ids)) and all(isinstance(x,str) and re.fullmatch(r'scrh-[0-9a-f]{16}',x) for x in ids)
  checks.append(check('finding/ids',ok,'findings',{'count':len(ids),'unique':len(set(ids))}))
  canon=[(ORDER.get(f.get('severity'),99),str(f.get('commit','')),str(f.get('path','')),int(f.get('line',0) or 0),str(f.get('rule','')),str(f.get('id',''))) for f in fs if isinstance(f,dict)]
  checks.append(check('finding/order',canon==sorted(canon),'findings',{}))
  raw=[]
  for i,f in enumerate(fs):
   ev=str(f.get('evidence','')) if isinstance(f,dict) else ''
   if any(p.search(ev) for p in RAW): raw.append(i)
  checks.append(check('evidence/no-raw-secret',not raw,'findings[].evidence',raw[:20]))
  summary=d.get('summary'); expected={s:sum(1 for f in fs if isinstance(f,dict) and f.get('severity')==s) for s in SEV}
  checks.append(check('summary/counts',summary==expected,'summary',{'actual':summary,'expected':expected}))
  stats=d.get('scan_stats') if isinstance(d.get('scan_stats'),dict) else {}; checks.append(check('stats/findings',stats.get('findings')==len(fs),'scan_stats',stats))
 errors=sum(c['status']=='fail' for c in checks); r={'receipt_version':1,'status':'pass' if not errors else 'fail','stage':'validation','checks':checks,'errors':errors,'warnings':0,'metrics':{'checks':len(checks)}}
 out=json.dumps(r,indent=2,sort_keys=True)+'\n'
 if a.json_out: Path(a.json_out).write_text(out,encoding='utf-8')
 else: print(out,end='')
 return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
