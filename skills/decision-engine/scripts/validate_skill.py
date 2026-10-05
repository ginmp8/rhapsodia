#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, importlib.util, json, re, sys
from pathlib import Path

def _load_eval_validators():
    module_path = Path(__file__).with_name("validate_evals.py")
    spec = importlib.util.spec_from_file_location("decision_engine_validate_evals", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load bundled validator: {module_path}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module.validate_activation, module.validate_decisions

validate_activation, validate_decisions = _load_eval_validators()

LINK_RE=re.compile(r"\[[^\]]+\]\(([^)]+)\)")
LANGUAGE_TEXT_SUFFIXES={'.md','.json','.yaml','.yml','.py','.txt','.template'}
PORTUGUESE_WORD_HEX=(
    '7175616c','6f70c3a7c3a36f','6f7063616f','6573636f6c6861','6465636973c3a36f','6465636973616f',
    '65766964c3aa6e636961','65766964656e636961','757375c3a172696f','7573756172696f','6170656e6173',
    '61676f7261','6d656c686f72','70696f72','64657665','646576656d','706f72717565','74616d62c3a96d',
    '74616d62656d','656e74c3a36f','656e74616f','7175616e646f'
)
PORTUGUESE_WORDS=tuple(bytes.fromhex(value).decode('utf-8') for value in PORTUGUESE_WORD_HEX)
PORTUGUESE_CHARS=bytes.fromhex('c3a3c3b5c3a7').decode('utf-8')
PORTUGUESE_MARKER_RE=re.compile(
    r'(?i)\b(?:' + '|'.join(re.escape(value) for value in PORTUGUESE_WORDS) + r')\b|[' + re.escape(PORTUGUESE_CHARS) + r']'
)
REQUIRED={
 'VERSION','SKILL.md','agents/openai.yaml','schemas/decision-envelope.schema.json',
 'references/behavior-contract.md','references/control-placement.md','references/decision-contract.md',
 'references/evaluation-protocol.md','references/evidence-and-confidence.md','references/host-portability.md',
 'references/maintenance-and-evidence.md','references/versioning-and-compatibility.md','references/migration-v1-to-v2.md',
 'assets/templates/decision-envelope.json.template','examples/examples.md',
 'evals/activation-scenarios.json','evals/decision-scenarios.json',
 'scripts/validate_decision.py','scripts/validate_evals.py','scripts/validate_skill.py','scripts/package_skill.py',
 'tests/fixtures/decision-envelope-cases.json','tests/test_decision_contract.py',
 'tests/test_english_only_contract.py','tests/test_validate_skill_no_self_contamination.py',
 'tests/test_test_suite_no_self_contamination.py','tests/test_top100_contract.py'
}

def add(errors,code,msg): errors.append({'code':code,'message':msg})

def main():
    ap=argparse.ArgumentParser(description='Validate Decision Engine package.'); ap.add_argument('target',type=Path); ap.add_argument('--json-output',type=Path); a=ap.parse_args()
    root=a.target.resolve(); errors=[]; warnings=[]
    if not root.is_dir(): add(errors,'SK000','target must be a directory')
    roots=[p for p in root.rglob('SKILL.md') if '__pycache__' not in p.parts]
    if roots != [root/'SKILL.md']: add(errors,'SK001',f'exactly one root SKILL.md required, found {len(roots)}')
    missing=sorted(rel for rel in REQUIRED if not (root/rel).is_file())
    if missing: add(errors,'SK002',f'missing required files: {missing}')
    skill=root/'SKILL.md'
    if skill.is_file():
        text=skill.read_text(encoding='utf-8')
        parts=text.split('---',2)
        if len(parts)<3: add(errors,'SK003','SKILL.md YAML frontmatter missing')
        else:
            fm=parts[1]
            if not re.search(r'(?m)^name:\s*decision-engine\s*$',fm): add(errors,'SK004','frontmatter name must be decision-engine')
            if not re.search(r'(?m)^description:\s*\S',fm): add(errors,'SK005','frontmatter description missing')
    version=root/'VERSION'
    if not version.is_file() or not re.fullmatch(r'\d+\.\d+\.\d+\n?',version.read_text(encoding='utf-8')): add(errors,'SK010','VERSION must contain semantic version x.y.z')
    if skill.is_file() and 'Keep the package English-only.' not in skill.read_text(encoding='utf-8'):
        add(errors,'SK011','SKILL.md must preserve the English-only package contract')

    # Discovery/control-plane contract: the complete SKILL.md must fit inside the
    # first 100 physical lines, and all decision-critical sections must be present.
    if skill.is_file():
        skill_text=skill.read_text(encoding='utf-8')
        skill_lines=skill_text.splitlines()
        first100='\n'.join(skill_lines[:100])
        if len(skill_lines)>100:
            add(errors,'SK080',f'SKILL.md must fit within 100 physical lines; found {len(skill_lines)}')
        required_top100=(
            '## Mission','## Activation and boundaries','## Decision forms and statuses',
            '## Required inputs','## Core invariants','## Decision workflow',
            '## Output contract','## Stop conditions','## Progressive loading and validation'
        )
        missing_top100=[marker for marker in required_top100 if marker not in first100]
        if missing_top100:
            add(errors,'SK081',f'missing Top-100 control-plane sections: {missing_top100}')
        direct_markdown=(
            'references/behavior-contract.md','references/control-placement.md',
            'references/decision-contract.md','references/evaluation-protocol.md',
            'references/evidence-and-confidence.md','references/host-portability.md',
            'references/maintenance-and-evidence.md','references/versioning-and-compatibility.md',
            'references/migration-v1-to-v2.md','examples/examples.md'
        )
        missing_direct=[rel for rel in direct_markdown if rel not in skill_text]
        if missing_direct:
            add(errors,'SK082',f'required Markdown must be directly discoverable from SKILL.md: {missing_direct}')

    # Long supporting Markdown needs preview-first navigation so partial reads are useful.
    for md in sorted(root.rglob('*.md')):
        if md == skill:
            continue
        lines=md.read_text(encoding='utf-8').splitlines()
        if len(lines)>100:
            preview='\n'.join(lines[:40])
            missing=[]
            if '## At a Glance' not in preview: missing.append('## At a Glance')
            if '## Contents' not in preview: missing.append('## Contents')
            if missing:
                add(errors,'SK083',f'long Markdown lacks preview-first structure {md.relative_to(root)}: {missing}')

    # Conservative deterministic guard against Portuguese-language regressions.
    # Semantic review still owns the broader English-only claim.
    for path in sorted(p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in LANGUAGE_TEXT_SUFFIXES):
        rel=path.relative_to(root)
        if '__pycache__' in rel.parts:
            continue
        for lineno,line in enumerate(path.read_text(encoding='utf-8',errors='ignore').splitlines(),1):
            if PORTUGUESE_MARKER_RE.search(line):
                add(errors,'SK012',f'non-English Portuguese marker in {rel}:{lineno}')
                break

    # Resolve all package-local Markdown links relative to the file that owns them.
    for md in sorted(root.rglob('*.md')):
        for raw in LINK_RE.findall(md.read_text(encoding='utf-8')):
            ref=raw.split('#',1)[0].strip()
            if not ref or '://' in ref or ref.startswith(('mailto:','/')): continue
            dest=(md.parent/ref).resolve()
            try: dest.relative_to(root)
            except ValueError: add(errors,'SK020',f'link escapes package: {md.relative_to(root)} -> {raw}'); continue
            if not dest.exists(): add(errors,'SK021',f'broken local link: {md.relative_to(root)} -> {raw}')

    # Parse all Python without creating bytecode.
    for py in sorted(root.rglob('*.py')):
        try: ast.parse(py.read_text(encoding='utf-8'),filename=str(py))
        except SyntaxError as exc: add(errors,'SK030',f'python syntax error {py.relative_to(root)}: {exc}')

    json_files=[p for p in root.rglob('*.json') if p.is_file()]
    parsed={}
    for p in sorted(json_files):
        try: parsed[p.relative_to(root).as_posix()]=json.loads(p.read_text(encoding='utf-8'))
        except Exception as exc: add(errors,'SK040',f'invalid JSON {p.relative_to(root)}: {exc}')
    try: json.loads((root/'assets/templates/decision-envelope.json.template').read_text(encoding='utf-8'))
    except Exception as exc: add(errors,'SK041',f'invalid JSON template: {exc}')

    schema=parsed.get('schemas/decision-envelope.schema.json',{})
    if schema.get('$schema')!='https://json-schema.org/draft/2020-12/schema': add(errors,'SK042','decision schema must use JSON Schema 2020-12')
    if schema.get('properties',{}).get('contract_version',{}).get('const')!='decision-engine/2': add(errors,'SK043','schema contract_version must be decision-engine/2')
    decision_schema=schema.get('properties',{}).get('decision',{})
    branches=decision_schema.get('oneOf',[]) if isinstance(decision_schema,dict) else []
    decision_types={b.get('properties',{}).get('type',{}).get('const') for b in branches if isinstance(b,dict)}
    if decision_types != {'binary','choice','score'}: add(errors,'SK044',f'decision schema types must be binary, choice, score; got {sorted(x for x in decision_types if isinstance(x,str))}')

    eval_errors=[]
    act=parsed.get('evals/activation-scenarios.json',{})
    dec=parsed.get('evals/decision-scenarios.json',{})
    validate_activation(act,eval_errors); validate_decisions(dec,eval_errors)
    for item in eval_errors: add(errors,'SK050',f"{item['code']} {item['subject']}: {item['detail']}")

    fixtures=parsed.get('tests/fixtures/decision-envelope-cases.json',{})
    cases=fixtures.get('cases') if isinstance(fixtures,dict) else None
    if not isinstance(cases,list) or len(cases)<30: add(errors,'SK051','decision contract fixture suite requires at least 30 cases')

    # No generated noise, nested archives, or symlinks in the source package.
    for p in root.rglob('*'):
        rel=p.relative_to(root)
        if p.is_symlink(): add(errors,'SK060',f'symlink not allowed: {rel}')
        if '__pycache__' in p.parts or p.suffix in {'.pyc','.pyo','.zip'} or p.name=='.DS_Store': add(errors,'SK061',f'generated/package noise inside target: {rel}')

    adapter=root/'agents/openai.yaml'
    if adapter.is_file():
        txt=adapter.read_text(encoding='utf-8')
        if 'display_name:' not in txt or 'short_description:' not in txt: add(errors,'SK070','OpenAI adapter missing interface labels')

    report={'status':'pass' if not errors else 'fail','errors':errors,'warnings':warnings}
    out=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if a.json_output: a.json_output.parent.mkdir(parents=True,exist_ok=True); a.json_output.write_text(out,encoding='utf-8')
    print(out,end=''); return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
