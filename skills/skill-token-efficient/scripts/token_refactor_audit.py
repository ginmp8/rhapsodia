#!/usr/bin/env python3
import argparse, json, os, re
from pathlib import Path

TEXT_EXT = {'.md','.txt','.yaml','.yml','.json','.py','.sh','.toml','.template','.skill'}
TEXT_NAMES = {'SKILL.md','skill.md','openai.yaml','AGENTS.md','CLAUDE.md'}
SKIP_DIRS = {'.git','__pycache__','.pytest_cache','node_modules','.venv','venv'}
SKIP_EXT = {'.zip','.pyc','.png','.jpg','.jpeg','.gif','.pdf','.docx','.pptx','.xlsx'}
TOK = re.compile(r'[A-Za-z0-9_]+|[^\sA-Za-z0-9_]', re.U)
WORD = re.compile(r'\w+', re.U)
HEAD = re.compile(r'^#{1,6}\s+(.+?)\s*$', re.M)
LINK = re.compile(r'\[[^\]]+\]\(([^)]+)\)')
FENCE = re.compile(r'```[\s\S]*?```', re.M)
INLINE = re.compile(r'`([^`\n]+)`')
URL = re.compile(r'https?://[^\s)>\]]+')
FLAG = re.compile(r'(?<!\w)--[A-Za-z0-9][A-Za-z0-9_-]*')
ENV = re.compile(r'\$[A-Z_][A-Z0-9_]*')


def is_text(p):
    return p.name in TEXT_NAMES or (p.suffix.lower() not in SKIP_EXT and (p.suffix.lower() in TEXT_EXT or '.template' in p.name))


def walk(root):
    if root.is_file():
        if is_text(root):
            yield root
        return
    for d, dirs, names in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for n in names:
            p = Path(d) / n
            if is_text(p):
                yield p


def read(p):
    for enc in ('utf-8','latin-1'):
        try:
            return p.read_text(encoding=enc)
        except UnicodeDecodeError:
            pass
        except Exception:
            return None
    return None


def est(s):
    parts = TOK.findall(s)
    words = sum(1 for x in parts if re.fullmatch(r'[A-Za-z0-9_]+', x))
    punct = len(parts) - words
    non_ascii = sum(1 for c in s if ord(c) > 127)
    return max(1, round(words * .95 + punct * .75 + non_ascii * .30))


def rel(root, p):
    return str(p.relative_to(root)) if root.is_dir() else p.name


def headings(s):
    seen, dup = set(), set()
    for h in (x.strip().lower() for x in HEAD.findall(s)):
        dup.add(h) if h in seen else seen.add(h)
    return sorted(dup)


def broken(p, s):
    out = []
    for link in LINK.findall(s):
        if '://' in link or link.startswith('#') or link.startswith('mailto:'):
            continue
        clean = link.split('#', 1)[0].strip()
        if clean and not (p.parent / clean).exists():
            out.append(link)
    return out


def protect(s):
    plain = FENCE.sub('', s)
    return {
        'fenced_code': sorted(set(FENCE.findall(s))),
        'inline_code': sorted(set(m.group(0) for m in INLINE.finditer(plain))),
        'urls': sorted(set(URL.findall(s))),
        'markdown_link_targets': sorted(set(LINK.findall(s))),
        'paths': sorted({tok.strip('.,;)\"\'') for tok in plain.split() if '/' in tok and len(tok) < 180}),
        'cli_flags': sorted(set(FLAG.findall(plain))),
        'env_vars': sorted(set(ENV.findall(plain))),
    }


def file_stats(root, p):
    s = read(p)
    if s is None:
        return None
    prot = protect(s)
    rows = sum(1 for line in s.splitlines() if line.strip().startswith('|') and '|' in line.strip()[1:])
    longp = sum(1 for para in re.split(r'\n\s*\n', s) if len(WORD.findall(para)) >= 80)
    scaffold = len(re.findall(r'\b' + 'TO' + 'DO' + r'\b|\[' + 'TO' + 'DO', s, re.I))
    return {
        'path': rel(root, p), 'chars': len(s), 'words': len(WORD.findall(s)),
        'lines': s.count('\n') + (1 if s else 0), 'estimated_tokens': est(s),
        'tables': rows, 'long_paragraphs': longp, 'scaffold_markers': scaffold,
        'duplicate_headings': headings(s), 'broken_links': broken(p, s),
        'protected_counts': {k: len(v) for k, v in prot.items()},
    }


def audit(path):
    root = Path(path).resolve()
    files = [x for p in walk(root) if (x := file_stats(root, p))]
    total = lambda k: sum(x[k] for x in files)
    totals = {
        'files': len(files), 'chars': total('chars'), 'words': total('words'),
        'lines': total('lines'), 'estimated_tokens': total('estimated_tokens'),
        'tables': total('tables'), 'long_paragraphs': total('long_paragraphs'),
        'scaffold_markers': total('scaffold_markers'),
        'broken_links': sum(len(x['broken_links']) for x in files),
    }
    warnings = []
    if totals['scaffold_markers']:
        warnings.append(f"scaffold markers found: {totals['scaffold_markers']}")
    if totals['broken_links']:
        warnings.append(f"broken markdown links found: {totals['broken_links']}")
    if totals['tables'] > 20:
        warnings.append('many markdown table rows; lists may be cheaper')
    if totals['long_paragraphs']:
        warnings.append(f"long paragraphs found: {totals['long_paragraphs']}")
    top = [{'path': x['path'], 'estimated_tokens': x['estimated_tokens'], 'chars': x['chars'], 'lines': x['lines']} for x in sorted(files, key=lambda y: y['estimated_tokens'], reverse=True)[:10]]
    return {'target': str(root), 'files': files, 'totals': totals, 'top_files': top, 'warnings': warnings}


def text_map(path):
    root = Path(path).resolve(); out = {}
    for p in walk(root):
        s = read(p)
        if s is not None:
            out[rel(root, p)] = s
    return out


def compare(before, after, limit=20):
    b, a = audit(before), audit(after)
    bt, at = b['totals']['estimated_tokens'], a['totals']['estimated_tokens']
    bm, am = text_map(before), text_map(after)
    diffs = []
    for name in sorted(set(bm) & set(am)):
        bp, ap = protect(bm[name]), protect(am[name])
        miss, add = {}, {}
        for k in bp:
            m = sorted(set(bp[k]) - set(ap[k]))[:limit]
            n = sorted(set(ap[k]) - set(bp[k]))[:limit]
            if m: miss[k] = m
            if n: add[k] = n
        if miss or add:
            diffs.append({'path': name, 'missing_after': miss, 'added_after': add})
    return {
        'comparison': {'before_estimated_tokens': bt, 'after_estimated_tokens': at, 'token_delta': at - bt, 'reduction_pct': round(((bt - at) / bt * 100) if bt else 0, 2), 'improved': at < bt},
        'protected_region_comparison': {'common_files_checked': len(set(bm) & set(am)), 'files_missing_after': sorted(set(bm)-set(am)), 'files_added_after': sorted(set(am)-set(bm)), 'files_with_protected_diffs': len(diffs), 'diffs': diffs[:limit]},
        'targets': [b, a],
    }


def md(payload):
    lines = ['# Token Refactor Audit', '']
    c = payload.get('comparison')
    if c:
        lines += ['## Comparison', f"- Before estimated tokens: {c['before_estimated_tokens']}", f"- After estimated tokens: {c['after_estimated_tokens']}", f"- Delta: {c['token_delta']}", f"- Reduction: {c['reduction_pct']}%", f"- Improved: {c['improved']}", '']
    p = payload.get('protected_region_comparison')
    if p:
        lines += ['## Protected Regions', f"- Common files checked: {p['common_files_checked']}", f"- Files with protected diffs: {p['files_with_protected_diffs']}", f"- Files missing after: {len(p['files_missing_after'])}", f"- Files added after: {len(p['files_added_after'])}", '']
    for t in payload['targets']:
        z = t['totals']
        lines += [f"## {t['target']}", f"- Files: {z['files']}", f"- Estimated tokens: {z['estimated_tokens']}", f"- Chars: {z['chars']}", f"- Words: {z['words']}", f"- Lines: {z['lines']}", f"- Tables: {z['tables']}", f"- Long paragraphs: {z['long_paragraphs']}", f"- Scaffold markers: {z['scaffold_markers']}", f"- Broken links: {z['broken_links']}", '', '### Largest files']
        lines += [f"- `{x['path']}`: {x['estimated_tokens']} est. tokens" for x in t['top_files']]
        if t['warnings']:
            lines += ['', '### Warnings'] + [f"- {w}" for w in t['warnings']]
        lines.append('')
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--target'); ap.add_argument('--before'); ap.add_argument('--after')
    ap.add_argument('--output'); ap.add_argument('--markdown')
    ns = ap.parse_args()
    if ns.target and (ns.before or ns.after): ap.error('use --target or --before/--after, not both')
    if not ns.target and not (ns.before and ns.after): ap.error('provide --target or both --before and --after')
    payload = {'targets': [audit(ns.target)]} if ns.target else compare(ns.before, ns.after)
    data = json.dumps(payload, ensure_ascii=False, indent=2)
    if ns.output:
        Path(ns.output).parent.mkdir(parents=True, exist_ok=True); Path(ns.output).write_text(data, encoding='utf-8')
    else:
        print(data)
    if ns.markdown:
        Path(ns.markdown).parent.mkdir(parents=True, exist_ok=True); Path(ns.markdown).write_text(md(payload), encoding='utf-8')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
