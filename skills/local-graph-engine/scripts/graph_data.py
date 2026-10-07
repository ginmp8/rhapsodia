"""Domain-neutral profiling and declarative row-to-graph mapping. No inference."""
from __future__ import annotations
import csv
import io
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import quote
import xml.etree.ElementTree as ET
from graph_common import MAX_BYTES, MAX_ITEMS, canonical, digest, finite_tree, read_json

SENSITIVE = re.compile(r"(^|_)(password|passwd|secret|token|api_key|authorization|private_key)($|_)",re.I)

def scalar_label(value):
    return str(value) if not isinstance(value,(dict,list)) else canonical(value)

def scrub(value):
    if isinstance(value,dict): return {k: "[REDACTED]" if SENSITIVE.search(k) else scrub(v) for k,v in value.items()}
    if isinstance(value,list): return [scrub(v) for v in value]
    return value

def file_info(path: Path, namespace: str) -> dict:
    if not isinstance(namespace,str) or not namespace.strip(): raise ValueError("namespace is required")
    if path.stat().st_size > MAX_BYTES: raise ValueError(f"source exceeds {MAX_BYTES} bytes")
    return {"uri": "dataset://"+quote(namespace,safe="")+"/"+quote(path.name,safe=""), "kind":path.suffix.lower().lstrip('.') or "file", "content_hash":"sha256:"+__import__('hashlib').sha256(path.read_bytes()).hexdigest(), "metadata":{"namespace":namespace,"file_name":path.name}}

def read_rows(path: Path, *, table: str | None = None, records_path: str | None = None, max_rows: int = 100000, header_row: int = 1) -> list[dict]:
    path=Path(path)
    if path.stat().st_size>MAX_BYTES: raise ValueError("source exceeds byte budget")
    if not 1<=max_rows<=MAX_ITEMS or not 1<=header_row<=10000: raise ValueError("invalid row budget/header row")
    suffix=path.suffix.lower()
    if suffix in (".csv",".tsv"):
        text=path.read_text(encoding="utf-8-sig"); delimiter='\t' if suffix=='.tsv' else ','
        if suffix=='.csv':
            try: delimiter=csv.Sniffer().sniff(text[:8192],delimiters=',;\t|').delimiter
            except csv.Error: pass
        reader=csv.reader(io.StringIO(text),delimiter=delimiter,strict=True)
        for _ in range(header_row-1):next(reader,None)
        header=next(reader,None)
        if not header or any(not x for x in header) or len(set(header))!=len(header): raise ValueError("header must contain unique nonempty columns")
        rows=[]
        for index,row in enumerate(reader,header_row+1):
            if not row: continue
            if len(row)!=len(header): raise ValueError(f"row {index}: expected {len(header)} columns, got {len(row)}")
            if len(rows)>=max_rows: raise ValueError("row budget exceeded; select a smaller source or raise the explicit budget")
            rows.append(dict(zip(header,row)))
        return rows
    if suffix in (".db",".sqlite",".sqlite3"):
        con=sqlite3.connect(path.resolve().as_uri()+"?mode=ro",uri=True)
        try:
            con.row_factory=sqlite3.Row;con.execute("PRAGMA query_only=ON");con.execute("PRAGMA trusted_schema=OFF")
            tables=[r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND sql NOT LIKE 'CREATE VIRTUAL%' ORDER BY name")]
            if not table:
                if len(tables)!=1: raise ValueError("choose --table explicitly: "+", ".join(tables))
                table=tables[0]
            if table not in tables: raise ValueError("table not found or virtual tables are unsupported")
            quoted='"'+table.replace('"','""')+'"'
            rows=[dict(r) for r in con.execute(f"SELECT * FROM {quoted} LIMIT ?",(max_rows+1,))]
            if len(rows)>max_rows: raise ValueError("row budget exceeded")
            # Canonical sorting prevents unordered SQL row order affecting IDs.
            rows=sorted(rows,key=canonical)
            finite_tree(rows);return rows
        finally:con.close()
    if suffix=='.xlsx':
        try:import openpyxl
        except ImportError as exc:raise RuntimeError("XLSX needs the optional openpyxl library") from exc
        wb=openpyxl.load_workbook(path,read_only=True,data_only=False,keep_links=False)
        try:
            ws=wb[table] if table else wb.active
            iterator=ws.iter_rows(values_only=True)
            for _ in range(header_row-1):next(iterator,None)
            header=next(iterator,None)
            if not header: return []
            names=[str(x) if x is not None else '' for x in header]
            if '' in names or len(set(names))!=len(names):raise ValueError("XLSX requires unique nonempty headers")
            rows=[]
            for row in iterator:
                if all(v is None for v in row):continue
                if len(rows)>=max_rows:raise ValueError("row budget exceeded")
                rows.append({k:(v.isoformat() if hasattr(v,'isoformat') else v) for k,v in zip(names,row)})
            finite_tree(rows);return rows
        finally:wb.close()
    if suffix in ('.yaml','.yml'):
        try:import yaml
        except ImportError as exc:raise RuntimeError("YAML needs the optional PyYAML library") from exc
        obj=yaml.safe_load(path.read_text(encoding='utf-8'))
    elif suffix in ('.jsonl','.ndjson'):
        from graph_common import parse_json
        obj=[]
        for i,line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(),1):
            if line.strip():
                if len(obj)>=max_rows:raise ValueError("row budget exceeded")
                obj.append(parse_json(line))
    elif suffix=='.xml':
        raw=path.read_bytes()
        if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():raise ValueError("DTD/entity declarations are not accepted")
        root=ET.fromstring(raw)
        items=list(root.findall(records_path)) if records_path else list(root)
        obj=[]
        for element in items:
            row=dict(element.attrib)
            for child in element:
                k=child.tag.rsplit('}',1)[-1]
                if k in row:raise ValueError("repeated XML child requires a structural JSON projection")
                row[k]=child.text
            if not row:row={"tag":element.tag,"text":element.text}
            obj.append(row)
    else:obj=read_json(path)
    finite_tree(obj)
    if records_path and suffix!='.xml':
        for key in records_path.split('.'):
            if not isinstance(obj,dict) or key not in obj:raise ValueError("records path not found")
            obj=obj[key]
    if isinstance(obj,dict):obj=[obj]
    if not isinstance(obj,list) or any(not isinstance(x,dict) for x in obj):raise ValueError("record input must be an array of objects; use structural ingestion for arbitrary JSON")
    if len(obj)>max_rows:raise ValueError("row budget exceeded")
    return obj

def profile(rows: list[dict]) -> dict:
    columns=sorted({k for row in rows for k in row})
    info=[]
    for col in columns:
        values=[r.get(col) for r in rows]
        present=[v for v in values if v is not None and v!='']
        distinct=len({canonical(v) for v in present})
        numeric=0
        for v in present:
            if isinstance(v,bool):continue
            try:
                f=float(v)
                if __import__('math').isfinite(f):numeric+=1
            except (ValueError,TypeError):pass
        info.append({"name":col,"present":len(present),"missing":len(values)-len(present),"distinct":distinct,"candidate_key":bool(rows) and distinct==len(rows) and len(present)==len(rows),"types":dict(sorted(Counter(type(v).__name__ for v in present).items())),"numeric_count":numeric,"sensitive_name":bool(SENSITIVE.search(col))})
    duplicate_rows=len(rows)-len({canonical(r) for r in rows})
    return {"rows":len(rows),"columns":info,"duplicate_rows":duplicate_rows,"inferred_relations":0}

def propose_mapping(rows: list[dict],namespace: str,kind: str='record') -> dict:
    report=profile(rows)
    candidates=[x['name'] for x in report['columns'] if x['candidate_key'] and not x['sensitive_name']]
    preferred=sorted(candidates,key=lambda s:(s.lower() not in ('id','key','uuid'),s))
    ids=[c for c in preferred if c.lower() in ('id','key','uuid')][:1]
    return {"schema_version":"graph-mapping-v1","namespace":namespace,"entities":[{"key":"row","kind":kind,"id_columns":ids,"label_column":ids[0] if ids else None,"properties":[x['name'] for x in report['columns']]}],"relations":[],"normalization":"none","notes":["Review the proposed identity before ingesting. Uniqueness alone does not establish business identity.","No relationship is inferred. Add relations only when a source column or known rule supports them."]}

def validate_mapping(mapping: dict,columns: set[str]) -> None:
    if not isinstance(mapping,dict) or mapping.get('schema_version')!='graph-mapping-v1':raise ValueError("unsupported mapping")
    if not isinstance(mapping.get('namespace'),str) or not mapping['namespace']:raise ValueError("mapping namespace required")
    if mapping.get('normalization','none') not in ('none','trim','casefold'):raise ValueError("invalid normalization")
    entities=mapping.get('entities')
    if not isinstance(entities,list) or not entities:raise ValueError("entities must be a nonempty array")
    keys=set()
    for e in entities:
        if not isinstance(e,dict) or not all(isinstance(e.get(k),str) and e[k] for k in ['key','kind']):raise ValueError("entity key and kind required")
        if e['key'] in keys:raise ValueError("duplicate mapping entity key")
        keys.add(e['key'])
        ids=e.get('id_columns',[]);props=e.get('properties',[])
        if not isinstance(ids,list) or not isinstance(props,list) or any(not isinstance(c,str) for c in ids+props):raise ValueError("column lists must be arrays of strings")
        required=set(ids+props+([e['label_column']] if e.get('label_column') else []))
        if required-columns:raise ValueError("mapping columns not found: "+', '.join(sorted(required-columns)))
        if any(SENSITIVE.search(c) for c in ids) or (e.get('label_column') and SENSITIVE.search(e['label_column'])):raise ValueError("secrets must not be identity or label columns")
        types=e.get('types',{})
        if not isinstance(types,dict) or set(types)-set(props) or any(v not in ('string','integer','number','boolean','json','datetime') for v in types.values()):raise ValueError('invalid explicit property type mapping')
    for r in mapping.get('relations',[]):
        if r.get('from') not in keys or r.get('to') not in keys or not isinstance(r.get('relation'),str) or not r['relation']:raise ValueError("invalid relation mapping")
        if not isinstance(r.get('directed',True),bool):raise ValueError("directed must be boolean")

def evidence(locator: str,provenance: str='EXTRACTED',details: dict | None=None) -> list[dict]:
    return [{"provenance":provenance,"confidence":1.0 if provenance in ('EXTRACTED','DERIVED','MANUAL') else 0.5,"status":"accepted" if provenance!='INFERRED' else 'ambiguous',"locator":locator,"details":details or {}}]

def rows_to_patch(rows: list[dict],source: dict,mapping: dict) -> dict:
    columns={k for row in rows for k in row};validate_mapping(mapping,columns)
    namespace=mapping['namespace'];nodes={};edges={};occurrences=Counter();missing=0;label_quality={}
    def normalize(v):
        mode=mapping.get('normalization','none')
        return (v.strip().casefold() if mode=='casefold' else v.strip()) if isinstance(v,str) and mode!='none' else v
    for row_no,row in enumerate(rows,1):
        locator=f"row:{row_no}";refs={}
        # Row identity keeps identical source rows separate when no key was selected.
        rowhash=digest(row);occurrences[rowhash]+=1
        for e in mapping['entities']:
            key_values=[normalize(row.get(c)) for c in e.get('id_columns',[])]
            if any(v is None or v=='' for v in key_values):missing+=1;continue
            identity=key_values if key_values else [source['uri'],rowhash,occurrences[rowhash],e['key']]
            nid='entity:'+digest([namespace,e['kind'],identity])[:32];refs[e['key']]=nid
            label_value=row.get(e.get('label_column')) if e.get('label_column') else None
            label=scalar_label(label_value) if label_value is not None and label_value!='' else ' / '.join(map(scalar_label,key_values)) or f"{e['kind']} {row_no}"
            observed=scrub({c:row.get(c) for c in e.get('properties',[])})
            props={k:cast_property(v,e.get('types',{}).get(k)) for k,v in observed.items()}
            details={'mapping_entity':e['key'],'row':row_no,'observed_properties':observed}
            node={'id':nid,'kind':e['kind'],'label':label,'properties':props,'aliases':[], 'evidence':evidence(locator,details=details)}
            quality=0 if label_value is not None and label_value!='' else 1
            if nid in nodes:
                previous=nodes[nid]
                # A role reference may introduce only an ID before a later row
                # supplies the person's attributes. Preserve complementary facts
                # without overwriting contradictory observations.
                conflicting=any(k in previous['properties'] and previous['properties'][k]!=value for k,value in props.items())
                conflicting=conflicting or (quality==label_quality[nid]==0 and previous['label']!=label)
                for key,value in props.items():previous['properties'].setdefault(key,value)
                if quality<label_quality[nid]:previous['label']=label;label_quality[nid]=quality
                if conflicting:previous['properties'].setdefault('_conflicting_rows',[]).append(row_no)
                previous['evidence'].extend(node['evidence'])
            else:nodes[nid]=node;label_quality[nid]=quality
        for r in mapping.get('relations',[]):
            if r['from'] not in refs or r['to'] not in refs:continue
            s,t=refs[r['from']],refs[r['to']];d=r.get('directed',True)
            if not d:s,t=sorted((s,t))
            key=(s,t,r['relation'],d)
            if key not in edges:edges[key]={'source':s,'target':t,'relation':r['relation'],'directed':d,'properties':{},'evidence':[]}
            edges[key]['evidence'].extend(evidence(locator,details={'mapping_relation':r['relation']}))
    metadata=dict(source.get('metadata',{}),mapping_hash=digest(mapping),rows=len(rows),missing_entity_keys=missing)
    return {'schema_version':'graph-patch-v1','source':dict(source,metadata=metadata),'nodes':sorted(nodes.values(),key=lambda x:x['id']),'edges':sorted(edges.values(),key=canonical)}

def structural_json(obj: Any,source: dict,max_nodes: int=10000) -> dict:
    finite_tree(obj);nodes=[];edges=[]
    def walk(value,pointer,parent=None,label='root'):
        if len(nodes)>=max_nodes:raise ValueError("structural JSON node budget exceeded")
        nid='json:'+digest([source['uri'],pointer])[:32]
        kind='object' if isinstance(value,dict) else 'array' if isinstance(value,list) else 'value'
        props={} if kind in ('object','array') else {'value':value}
        nodes.append({'id':nid,'kind':kind,'label':str(label),'properties':props,'evidence':evidence(pointer or '/')})
        if parent:edges.append({'source':parent,'target':nid,'relation':'contains','directed':True,'properties':{},'evidence':evidence(pointer)})
        items=sorted(value.items()) if isinstance(value,dict) else enumerate(value) if isinstance(value,list) else []
        for key,child in items:
            token=str(key).replace('~','~0').replace('/','~1')
            walk('[REDACTED]' if isinstance(key,str) and SENSITIVE.search(key) else child,pointer+'/'+token,nid,key)
    walk(scrub(obj),'')
    return {'schema_version':'graph-patch-v1','source':source,'nodes':nodes,'edges':edges}


def cast_property(value,kind):
    """Explicit conversions only; preserve the original value in evidence."""
    if not kind or value is None:return value
    if kind=='string':return scalar_label(value)
    if kind=='integer':
        if isinstance(value,bool) or not re.fullmatch(r'[+-]?\d+',str(value)):raise ValueError('invalid integer conversion')
        return int(value)
    if kind=='number':
        if isinstance(value,bool):raise ValueError('boolean is not a numeric measurement')
        number=float(value)
        if not __import__('math').isfinite(number):raise ValueError('numeric conversion must be finite')
        return number
    if kind=='boolean':
        if isinstance(value,bool):return value
        if str(value).lower() not in ('true','false'):raise ValueError('boolean conversion requires true or false')
        return str(value).lower()=='true'
    if kind=='json':
        from graph_common import parse_json
        out=parse_json(value) if isinstance(value,str) else value;finite_tree(out);return out
    if kind=='datetime':
        from datetime import datetime
        if not isinstance(value,str):raise ValueError('datetime requires an ISO string with timezone')
        stamp=datetime.fromisoformat(value.replace('Z','+00:00'))
        if stamp.tzinfo is None:raise ValueError('datetime conversion does not guess a timezone')
        return stamp.isoformat()
    raise ValueError('unsupported property conversion')
