#!/usr/bin/env python3
"""Append-only, provenance-labelled, hash-checked investigation evidence ledger.

SQLite records contain bounded JSON summaries, never executable file contents.
Importing an evidence bundle does not prove that its reported events occurred.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
from pathlib import Path
from typing import Any
from artifact_index import ArtifactError, digest, strict_json

MAX_RECORD = 20 * 1024 * 1024
MAX_BUNDLE = 80 * 1024 * 1024
MAX_RECORDS = 10000
KINDS = {'inventory','application_graph','feature_trace','application_comparison',
         'binary_report','artifact_report','interface_report','comparison','obligation_ledger','user_supplied'}
LEVELS = {'declared','lexical_candidate','decoded_call_site','claimed_semantic_resolution',
          'runtime_observed_unattested','inferred','unknown','user_supplied'}


def canonical(obj: Any) -> bytes:
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf8')


def validate_record(kind: str, artifact_sha256: str, data: dict, level: str) -> None:
    if kind not in KINDS or level not in LEVELS:
        raise ArtifactError('unsupported evidence kind or level')
    if not isinstance(artifact_sha256,str) or not re.fullmatch('[a-f0-9]{64}',artifact_sha256):
        raise ArtifactError('source sha256 required')
    if not isinstance(data,dict):
        raise ArtifactError('evidence must be a JSON object')
    if len(canonical(data)) > MAX_RECORD:
        raise ArtifactError('evidence record budget exceeded')


def build_record(kind: str, artifact_sha256: str, data: dict, level: str) -> dict:
    validate_record(kind,artifact_sha256,data,level)
    content={'kind':kind,'artifact_sha256':artifact_sha256,'level':level,'data':data}
    evidence_id='ev_'+digest(canonical(content))
    return {'evidence_id':evidence_id,**content}


class EvidenceStore:
    def __init__(self, path: Path | None = None):
        if path:
            if not path.parent.is_dir() or path.is_symlink():
                raise ArtifactError('SQLite parent must exist and not be a symlink')
        self.db = sqlite3.connect(str(path) if path else ':memory:',timeout=10,check_same_thread=False)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS records (
          sequence INTEGER PRIMARY KEY AUTOINCREMENT,
          evidence_id TEXT NOT NULL UNIQUE,
          kind TEXT NOT NULL,
          artifact_sha256 TEXT NOT NULL,
          level TEXT NOT NULL,
          body TEXT NOT NULL,
          first_seen_utc INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS records_source ON records(artifact_sha256,kind);
        ''')

    def close(self) -> None:
        self.db.close()

    def put(self,kind:str,artifact_sha256:str,data:dict,level:str) -> dict:
        record=build_record(kind,artifact_sha256,data,level)
        body=canonical(record).decode('utf8')
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO records(evidence_id,kind,artifact_sha256,level,body,first_seen_utc) VALUES (?,?,?,?,?,?)',
                            (record['evidence_id'],kind,artifact_sha256,level,body,int(time.time())))
        return {'evidence_id':record['evidence_id'],'kind':kind,'level':level,'source_sha256':artifact_sha256}

    def get(self,evidence_id:str,section:str='summary',offset:int=0,limit:int=80) -> dict:
        row=self.db.execute('SELECT body FROM records WHERE evidence_id=?',(evidence_id,)).fetchone()
        if row is None:
            raise ArtifactError('unknown evidence id')
        record=strict_json(row[0].encode('utf8'))
        if not isinstance(record,dict):
            raise ArtifactError('invalid evidence record')
        expected=build_record(record['kind'],record['artifact_sha256'],record['data'],record['level'])
        if expected['evidence_id']!=record['evidence_id']:
            raise ArtifactError('stored evidence corrupted')
        if section=='complete':
            if len(row[0])>MAX_RECORD:
                raise ArtifactError('record exceeds output budget')
            return record
        if section in ('nodes','edges','items','routes','references','unknowns','skips','mismatches'):
            items=record['data'].get(section,[])
            if not isinstance(items,list):
                raise ArtifactError('requested section is not list')
            offset=max(0,int(offset));limit=max(1,min(int(limit),200))
            return {'evidence_id':evidence_id,'section':section,'total':len(items),
                    'offset':offset,'items':items[offset:offset+limit],
                    'next_offset':offset+limit if offset+limit<len(items) else None}
        if section!='summary':
            raise ArtifactError('unknown view section')
        data=record['data']
        return {'evidence_id':evidence_id,'kind':record['kind'],'artifact_sha256':record['artifact_sha256'],
                'level':record['level'],
                'fields':{k:(len(v) if isinstance(v,list) else v if isinstance(v,(str,int,float,bool,type(None))) else
                            ('object:' + ','.join(sorted(v)[:15]) if isinstance(v,dict) else 'other'))
                          for k,v in data.items() if k in ('format','source_kind','complete','count','skipped_count',
                          'js_files_seen','nodes','edges','unknowns','items','routes','comparison_status','evidence_level','claim_ceiling','readiness')},
                'available_sections':[k for k,v in data.items() if isinstance(v,list)]}

    def query(self,kind:str|None=None,artifact_sha256:str|None=None,offset:int=0,limit:int=60) -> dict:
        if kind is not None and kind not in KINDS:raise ArtifactError('unknown evidence kind')
        if artifact_sha256 is not None and not re.fullmatch('[a-f0-9]{64}',artifact_sha256):
            raise ArtifactError('bad artifact digest')
        terms=[];values=[]
        if kind:terms.append('kind=?');values.append(kind)
        if artifact_sha256:terms.append('artifact_sha256=?');values.append(artifact_sha256)
        where=' WHERE '+' AND '.join(terms) if terms else ''
        total=self.db.execute('SELECT COUNT(*) FROM records'+where,values).fetchone()[0]
        offset=max(0,int(offset));limit=max(1,min(int(limit),200))
        rows=self.db.execute('SELECT evidence_id,kind,artifact_sha256,level FROM records'+where+
                             ' ORDER BY sequence DESC LIMIT ? OFFSET ?',values+[limit,offset]).fetchall()
        return {'total':total,'items':[dict(zip(('evidence_id','kind','artifact_sha256','level'),r)) for r in rows],
                'next_offset':offset+limit if offset+limit<total else None}

    def export(self,limit:int=MAX_RECORDS) -> dict:
        rows=self.db.execute('SELECT body FROM records ORDER BY evidence_id LIMIT ?', (min(MAX_RECORDS,limit)+1,)).fetchall()
        if len(rows)>limit:
            raise ArtifactError('bundle record count budget exceeded')
        records=[strict_json(row[0].encode('utf8')) for row in rows]
        document={'schema_version':'1.0','records':records,
                  'provenance':'Locally indexed summaries; imported runtime claims are not independently attested.'}
        document['bundle_sha256']=digest(canonical(document))
        if len(canonical(document))>MAX_BUNDLE:
            raise ArtifactError('bundle output budget exceeded')
        return document

    def import_bundle(self,blob:bytes) -> dict:
        if len(blob)>MAX_BUNDLE:
            raise ArtifactError('bundle byte budget exceeded')
        data=strict_json(blob)
        if not isinstance(data,dict) or data.get('schema_version')!='1.0':
            raise ArtifactError('unsupported evidence bundle')
        stamp=data.get('bundle_sha256')
        snapshot={k:v for k,v in data.items() if k!='bundle_sha256'}
        if not isinstance(stamp,str) or digest(canonical(snapshot))!=stamp:
            raise ArtifactError('bundle hash mismatch')
        records=data.get('records')
        if not isinstance(records,list) or len(records)>MAX_RECORDS:
            raise ArtifactError('bundle record count invalid')
        seen=set()
        checked=[]
        for record in records:
            if not isinstance(record,dict) or set(record)!={'evidence_id','kind','artifact_sha256','level','data'}:
                raise ArtifactError('invalid evidence record fields')
            calculated=build_record(record['kind'],record['artifact_sha256'],record['data'],record['level'])
            if calculated != record or record['evidence_id'] in seen:
                raise ArtifactError('tampered or duplicate evidence record')
            seen.add(record['evidence_id']);checked.append(record)
        with self.db:
            for record in checked:
                self.db.execute('INSERT OR IGNORE INTO records(evidence_id,kind,artifact_sha256,level,body,first_seen_utc) VALUES (?,?,?,?,?,?)',
                                (record['evidence_id'],record['kind'],record['artifact_sha256'],record['level'],
                                 canonical(record).decode('utf8'),int(time.time())))
        return {'imported':len(checked),'bundle_sha256':stamp,
                'authority':'Imported evidence retains its claimed tier. Content hashes do not attest observed execution.'}
