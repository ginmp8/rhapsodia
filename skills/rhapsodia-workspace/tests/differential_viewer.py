from __future__ import annotations
import copy,json,subprocess,sys
from pathlib import Path
r=Path(sys.argv[1]);out=Path(sys.argv[2]);sys.path[:0]=[str(r/'scripts'),str(r/'tests')]
from artifact_protocol import validate_record,ContractError,schema_for
from test_protocol import record
base=record();cases=[]
def add(name,value):
    try:validate_record(value);expected=True
    except (ValueError,TypeError,KeyError,OSError):expected=False
    cases.append({'name':name,'record':value,'expected':expected})
add('valid',base)
def inspect(obj,trail=()):
    for key,value in obj.items():
        location=trail+(key,)
        for replacement in [None,False,0,[],{},'', 'invalid', 'x'*250]:
            candidate=copy.deepcopy(base);cursor=candidate
            for part in trail:cursor=cursor[part]
            cursor[key]=replacement;add('.'.join(location)+':'+repr(replacement)[:30],candidate)
        candidate=copy.deepcopy(base);cursor=candidate
        for part in trail:cursor=cursor[part]
        del cursor[key];add('.'.join(location)+':missing',candidate)
        if isinstance(value,dict):inspect(value,location)
inspect(base)
for date in ['0000-01-01T12:00:00Z','2028-02-29T12:00:00Z','2026-02-30T12:00:00Z','2026-10-03T24:00:00Z','2026-10-03T12:00:60Z']:
    value=copy.deepcopy(base);value['created_at']=date;add('date:'+date,value)
for path in ['docs/a?.md','docs/.env.txt','docs/con.md','.rhapsodia/views/a.md','docs/my..txt','docs/a.pem','docs/x./a.md']:
    value=copy.deepcopy(base);value['source']['path']=path;add('path:'+path,value)
for case in cases:
    value=case['record'];source=value.get('source',{});source=source if isinstance(source,dict) else {}
    diagnostics=[]
    if value.get('lifecycle')!='removed' and isinstance(value.get('relations'),list):
        for rel in value['relations']:
            if isinstance(rel,dict) and rel.get('target')!=value.get('artifact_id'):diagnostics.append({'severity':'warning','code':'UNRESOLVED_RELATION','artifact_id':value.get('artifact_id'),'target':rel.get('target')})
    case['catalog']={'schema_version':'1.0.0','kind':'derived-artifact-catalog','authority':'non-authoritative','source_roots':['docs'],'destination':'local','source_fingerprint':'a'*64,'latest_source_update':value.get('updated_at'),'entries':[{'record':value,'manifest_path':str(source.get('path',''))+'.artifact.json','manifest_sha256':'b'*64}],'diagnostics':diagnostics}
html=(r/'assets/workspace.html').read_text();start=html.index('const envelopeSchema=');end=html.index('function setCatalog(',start);js=html[start:end]
js=js.replace("JSON.parse(document.getElementById('workspace-envelope-schema').textContent)",json.dumps(schema_for('artifact-envelope.schema.json')))
js+='\nconst fs=require("fs"); const cases=JSON.parse(fs.readFileSync(0,"utf8")); console.log(JSON.stringify(cases.map(item=>{try{validateCatalog(item.catalog);return true;}catch(e){return false;}})));'
proc=subprocess.run(['node','-e',js],input=json.dumps(cases),text=True,capture_output=True,check=True);actual=json.loads(proc.stdout)
mismatches=[{'name':case['name'],'expected':case['expected'],'actual':result} for case,result in zip(cases,actual) if case['expected']!=result]
report={'cases':len(cases),'matches':len(cases)-len(mismatches),'mismatches':mismatches,'scope':'metadata contract only; no filesystem authenticity in browser'}
out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));sys.exit(bool(mismatches))
