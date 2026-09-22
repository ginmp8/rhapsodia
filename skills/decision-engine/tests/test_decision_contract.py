#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0,str(ROOT/'scripts'))
from validate_decision import validate  # noqa: E402

def main():
    fixture=json.loads((ROOT/'tests/fixtures/decision-envelope-cases.json').read_text(encoding='utf-8'))
    failures=[]
    for case in fixture['cases']:
        errors=validate(case['data']); got=not errors; codes={e['code'] for e in errors}
        missing_codes=[c for c in case.get('expected_codes',[]) if c not in codes]
        if got!=case['valid'] or missing_codes:
            failures.append({'id':case['id'],'expected_valid':case['valid'],'got_valid':got,'missing_expected_codes':missing_codes,'errors':errors})
    payload={'status':'pass' if not failures else 'fail','cases':len(fixture['cases']),'failures':failures}
    print(json.dumps(payload,indent=2,sort_keys=True)); return 0 if not failures else 1
if __name__=='__main__': raise SystemExit(main())
