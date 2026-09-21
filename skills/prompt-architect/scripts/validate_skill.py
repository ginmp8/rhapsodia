#!/usr/bin/env python3
"""Validate Prompt Architect package integrity with only the standard library."""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path

REQUIRED={
 "SKILL.md","assets/templates/prompt-contract.json.template","assets/templates/scenario-suite.json.template",
 "evals/activation-scenarios.json","scripts/prompt_lint.py","scripts/validate_prompt_contract.py",
 "scripts/validate_scenario_suite.py","scripts/package_skill.py"
}
LINK=re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def run(cmd:list[str])->tuple[int,str]:
    p=subprocess.run(cmd,text=True,capture_output=True)
    return p.returncode,(p.stdout+p.stderr).strip()


def validate(root:Path)->dict:
    errors=[]; checks=[]
    missing=sorted(p for p in REQUIRED if not (root/p).is_file())
    if missing: errors.append(f"missing required files: {missing}")
    if (root/'evals/activation-scenarios-v2.json').exists(): errors.append("obsolete evals/activation-scenarios-v2.json must not be present")
    skill=root/'SKILL.md'
    text=skill.read_text(encoding='utf-8') if skill.is_file() else ''
    m=re.match(r"^---\r?\n(.*?)\r?\n---",text,re.S)
    name=''
    if not m: errors.append('SKILL.md frontmatter missing')
    else:
        for line in m.group(1).splitlines():
            if line.startswith('name:'): name=line.split(':',1)[1].strip().strip('"\'')
        if name != root.name: errors.append(f"frontmatter name {name!r} must match directory {root.name!r}")
    for md in [root/'SKILL.md', *sorted((root/'references').glob('*.md'))]:
        if not md.is_file(): continue
        body=md.read_text(encoding='utf-8')
        for ref in LINK.findall(body):
            ref=ref.split('#',1)[0]
            if not ref or '://' in ref or ref.startswith('#'): continue
            target=(md.parent/ref).resolve()
            try: target.relative_to(root.resolve())
            except ValueError: errors.append(f"reference escapes package: {md.relative_to(root)} -> {ref}"); continue
            if not target.exists(): errors.append(f"missing reference: {md.relative_to(root)} -> {ref}")
    text_surfaces=[]
    for area in ('SKILL.md','references','evals','assets','examples','agents'):
        base=root/area
        paths=[base] if base.is_file() else list(base.rglob('*')) if base.is_dir() else []
        for candidate in paths:
            if candidate.is_file() and candidate.suffix.lower() in {'.md','.json','.template','.yaml','.yml'}:
                text_surfaces.append(candidate.read_text(encoding='utf-8',errors='ignore'))
    if 'Prompt Tester' in ''.join(text_surfaces):
        errors.append('host/tool-specific Prompt Tester dependency remains')
    for rel in ['scripts/prompt_lint.py','scripts/validate_prompt_contract.py','scripts/validate_scenario_suite.py','scripts/package_skill.py','scripts/validate_skill.py']:
        script=root/rel
        if script.is_file():
            try:
                compile(script.read_text(encoding='utf-8'), str(script), 'exec')
                checks.append({'check':f'compile:{rel}','passed':True,'detail':''})
            except SyntaxError as exc:
                checks.append({'check':f'compile:{rel}','passed':False,'detail':str(exc)})
                errors.append(f"python syntax failed: {rel}: {exc}")
    for rel,arg in [
      ('scripts/validate_prompt_contract.py','assets/templates/prompt-contract.json.template'),
      ('scripts/validate_scenario_suite.py','evals/activation-scenarios.json')]:
        if (root/rel).is_file() and (root/arg).is_file():
            rc,out=run([sys.executable,str(root/rel),str(root/arg)])
            checks.append({'check':f'{rel}:{arg}','passed':rc==0,'detail':out})
            if rc: errors.append(f"validator failed: {rel} {arg}")
    return {'status':'fail' if errors else 'pass','errors':errors,'checks':checks}


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--target',default=str(Path(__file__).resolve().parents[1])); ap.add_argument('--json', dest='json_output')
    a=ap.parse_args(); report=validate(Path(a.target).resolve()); payload=json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+'\n'
    if a.json_output: Path(a.json_output).write_text(payload,encoding='utf-8')
    print(payload,end=''); return 0 if report['status']=='pass' else 1
if __name__=='__main__': raise SystemExit(main())
