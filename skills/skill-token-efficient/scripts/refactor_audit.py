#!/usr/bin/env python3
import argparse,json,os,re
from pathlib import Path
TEXT={'.md','.txt','.yaml','.yml','.json','.py','.sh','.toml','.template','.skill'}; NAMES={'SKILL.md','skill.md','openai.yaml','AGENTS.md','CLAUDE.md'}
SKIP={'.git','__pycache__','.pytest_cache','node_modules','.venv','venv'}; BIN={'.zip','.pyc','.png','.jpg','.jpeg','.gif','.pdf','.docx','.pptx','.xlsx'}
WORD=re.compile(r'\w+',re.U); TOK=re.compile(r'[A-Za-z0-9_]+|[^\sA-Za-z0-9_]',re.U); LINK=re.compile(r'\[[^\]]+\]\(([^)]+)\)')
PROT=re.compile(r'```[\s\S]*?```|`[^`\n]+`|https?://[^\s)>\]]+|(?<!\w)--[A-Za-z0-9][A-Za-z0-9_-]*|\$[A-Z_][A-Z0-9_]*|\b[\w.-]+/[\w./-]+')
TRACE=[r'\bcitations?\b',r'\breferences?\b',r'\bsources?\b',r'\bline ranges?\b',r'\bfile paths?\b',r'\breport paths?\b',r'\bevidence\s*/\s*citation\b',r'\bevidence\s+(?:and|or)\s+citations?\b']
TR=[re.compile(x,re.I) for x in TRACE]
def texty(p): return p.name in NAMES or (p.suffix.lower() not in BIN and (p.suffix.lower() in TEXT or '.template' in p.name))
def files(root):
    root=Path(root)
    if root.is_file():
        if texty(root): yield root
        return
    for d,dirs,names in os.walk(root):
        dirs[:]=[x for x in dirs if x not in SKIP]
        for n in names:
            p=Path(d)/n
            if texty(p): yield p
def read(p):
    for e in ('utf-8','latin-1'):
        try: return p.read_text(encoding=e)
        except UnicodeDecodeError: pass
        except Exception: return ''
    return ''
def est(s):
    t=TOK.findall(s); w=sum(bool(re.fullmatch(r'[A-Za-z0-9_]+',x)) for x in t)
    return max(1,round(w*.95+(len(t)-w)*.75+sum(ord(c)>127 for c in s)*.3))
def rel(r,p): return str(p.relative_to(r)) if r.is_dir() else p.name
def miss(p,s):
    out=[]
    for x in LINK.findall(s):
        y=x.split('#',1)[0].strip()
        if y and '://' not in y and not x.startswith(('#','mailto:')) and not (p.parent/y).exists(): out.append(x)
    return out
def prot(s): return sorted(set(PROT.findall(s)))
def trace_hits(s):
    out={}
    for pat,rx in zip(TRACE,TR):
        n=len(rx.findall(s))
        if n: out[pat]=n
    return out
def fstat(r,p):
    s=read(p); lines=s.splitlines(); para=re.split(r'\n\s*\n',s); th=trace_hits(s)
    return {'path':rel(r,p),'chars':len(s),'words':len(WORD.findall(s)),'lines':len(lines),'estimated_tokens':est(s),'tables':sum(l.strip().startswith('|') and '|' in l.strip()[1:] for l in lines),'long_paragraphs':sum(len(WORD.findall(x))>=80 for x in para),'scaffold_markers':len(re.findall(r'\b'+'TO'+'DO'+r'\b|\['+'TO'+'DO',s,re.I)),'broken_links':miss(p,s),'protected_count':len(prot(s)),'traceability_terms':sum(th.values()),'traceability_detail':th}
def audit(x):
    r=Path(x).resolve(); fs=[fstat(r,p) for p in files(r)]; total=lambda k:sum(i[k] for i in fs)
    tot={'files':len(fs),'chars':total('chars'),'words':total('words'),'lines':total('lines'),'estimated_tokens':total('estimated_tokens'),'tables':total('tables'),'long_paragraphs':total('long_paragraphs'),'scaffold_markers':total('scaffold_markers'),'broken_links':sum(len(i['broken_links']) for i in fs),'traceability_terms':total('traceability_terms')}
    warn=[]
    for k,m in [('scaffold_markers','scaffold markers found'),('broken_links','broken markdown links found'),('long_paragraphs','long paragraphs found')]:
        if tot[k]: warn.append(f'{m}: {tot[k]}')
    if tot['tables']>20: warn.append('many markdown table rows; lists may be cheaper')
    top=[{k:i[k] for k in ('path','estimated_tokens','chars','lines')} for i in sorted(fs,key=lambda z:z['estimated_tokens'],reverse=True)[:10]]
    return {'target':str(r),'files':fs,'totals':tot,'top_files':top,'warnings':warn}
def tmap(x):
    r=Path(x).resolve(); return {rel(r,p):read(p) for p in files(r)}
def trace_diff(bm,am):
    out=[]
    for n in sorted(set(bm)&set(am)):
        bx,ax=trace_hits(bm[n]),trace_hits(am[n]); lost={k:v-ax.get(k,0) for k,v in bx.items() if ax.get(k,0)<v}
        if lost: out.append({'path':n,'lost_traceability_terms':lost})
    return out
def compare(b,a):
    B,A=audit(b),audit(a); bm,am=tmap(b),tmap(a); dif=[]
    for n in sorted(set(bm)&set(am)):
        x,y=set(prot(bm[n])),set(prot(am[n])); m=sorted(x-y)[:20]; add=sorted(y-x)[:20]
        if m or add: dif.append({'path':n,'missing_after':m,'added_after':add})
    td=trace_diff(bm,am); bt,at=B['totals']['estimated_tokens'],A['totals']['estimated_tokens']
    return {'comparison':{'before_estimated_tokens':bt,'after_estimated_tokens':at,'token_delta':at-bt,'reduction_pct':round(((bt-at)/bt*100) if bt else 0,2),'improved':at<bt},'protected_region_comparison':{'common_files_checked':len(set(bm)&set(am)),'files_missing_after':sorted(set(bm)-set(am)),'files_added_after':sorted(set(am)-set(bm)),'files_with_protected_diffs':len(dif),'diffs':dif[:20]},'traceability_comparison':{'before_terms':B['totals']['traceability_terms'],'after_terms':A['totals']['traceability_terms'],'term_delta':A['totals']['traceability_terms']-B['totals']['traceability_terms'],'files_with_traceability_loss':len(td),'losses':td[:20]},'targets':[B,A]}
def md(p):
    L=['# Token Refactor Audit','']; c=p.get('comparison')
    if c: L+=['## Comparison',f"- Before estimated tokens: {c['before_estimated_tokens']}",f"- After estimated tokens: {c['after_estimated_tokens']}",f"- Delta: {c['token_delta']}",f"- Reduction: {c['reduction_pct']}%",f"- Improved: {c['improved']}",'']
    q=p.get('protected_region_comparison')
    if q: L+=['## Protected Regions',f"- Common files checked: {q['common_files_checked']}",f"- Files with protected diffs: {q['files_with_protected_diffs']}",f"- Files missing after: {len(q['files_missing_after'])}",f"- Files added after: {len(q['files_added_after'])}",'']
    tr=p.get('traceability_comparison')
    if tr: L+=['## Traceability Terms',f"- Before terms: {tr['before_terms']}",f"- After terms: {tr['after_terms']}",f"- Delta: {tr['term_delta']}",f"- Files with traceability loss: {tr['files_with_traceability_loss']}",'']
    for t in p['targets']:
        z=t['totals']; keys=['files','estimated_tokens','chars','words','lines','tables','long_paragraphs','scaffold_markers','broken_links','traceability_terms']
        L+=[f"## {t['target']}"]+[f"- {k.replace('_',' ').title()}: {z[k]}" for k in keys]+['','### Largest files']+[f"- `{x['path']}`: {x['estimated_tokens']} est. tokens" for x in t['top_files']]
        if t['warnings']: L+=['','### Warnings']+[f'- {w}' for w in t['warnings']]
        L.append('')
    return '\n'.join(L)
def main():
    a=argparse.ArgumentParser(); a.add_argument('--target'); a.add_argument('--before'); a.add_argument('--after'); a.add_argument('--output'); a.add_argument('--markdown'); n=a.parse_args()
    if n.target and (n.before or n.after): a.error('use --target or --before/--after, not both')
    if not n.target and not (n.before and n.after): a.error('provide --target or both --before and --after')
    p={'targets':[audit(n.target)]} if n.target else compare(n.before,n.after); s=json.dumps(p,ensure_ascii=False,indent=2)
    if n.output: Path(n.output).parent.mkdir(parents=True,exist_ok=True); Path(n.output).write_text(s,encoding='utf-8')
    else: print(s)
    if n.markdown: Path(n.markdown).parent.mkdir(parents=True,exist_ok=True); Path(n.markdown).write_text(md(p),encoding='utf-8')
if __name__=='__main__': raise SystemExit(main())
