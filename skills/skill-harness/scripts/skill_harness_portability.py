#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from _harness_common import dump_json, parse_frontmatter_scalars

NAME_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
MARKDOWN_LINK_RE = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
HOST_PATH_MARKERS = (
    '/home/oai/skills/',
    '.github/skills/',
    '.cursor/skills/',
    '.claude/skills/',
    '.codex/skills/',
    '~/.copilot/skills/',
    '~/.cursor/skills/',
    '~/.claude/skills/',
    '~/.agents/skills/',
)
PROFILES = ('portable', 'openai', 'claude', 'copilot', 'cursor')
PROFILE_DISCOVERY = {
    'portable': 'Install the skill directory in any host location that implements the Agent Skills standard.',
    'openai': 'Use the host-managed ChatGPT skill installation/upload surface; OpenAI metadata under agents/ is an optional adapter, not core semantics.',
    'claude': 'Use a Claude Agent Skills-compatible installation surface such as Claude Code/project skill discovery.',
    'copilot': 'Project discovery supports .github/skills, .claude/skills, or .agents/skills; personal discovery supports ~/.copilot/skills or ~/.agents/skills.',
    'cursor': 'Project discovery supports .agents/skills or .cursor/skills; Cursor also reads compatible Claude/Codex skill directories.',
}


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace')


def core_checks(target: Path) -> tuple[list[dict], list[str]]:
    checks: list[dict] = []
    warnings: list[str] = []

    def check(code: str, passed: bool, detail: str, severity: str = 'blocker') -> None:
        checks.append({'code': code, 'passed': bool(passed), 'severity': severity, 'detail': detail})

    skill_md = target / 'SKILL.md'
    check('core/skill-md', skill_md.is_file(), 'SKILL.md exists')
    if not skill_md.is_file():
        return checks, warnings

    fm = parse_frontmatter_scalars(skill_md)
    name = fm.get('name', '')
    description = fm.get('description', '')
    compatibility = fm.get('compatibility', '')
    check('core/name-present', bool(name), 'name is present')
    check('core/name-format', bool(NAME_RE.fullmatch(name)) and len(name) <= 64, f'name={name!r}; max=64; lowercase alnum/hyphen')
    check('core/name-directory-match', name == target.name, f'name={name!r}; directory={target.name!r}')
    check('core/description', 1 <= len(description) <= 1024, f'description_length={len(description)}; allowed=1..1024')
    if compatibility:
        check('core/compatibility-length', len(compatibility) <= 500, f'compatibility_length={len(compatibility)}; max=500')

    body = read_text(skill_md)
    hardcoded = sorted(marker for marker in HOST_PATH_MARKERS if marker in body)
    check('core/no-host-install-path-dependency', not hardcoded, f'hardcoded_markers={hardcoded}', 'major')

    escaping_links = []
    missing_links = []
    for md in sorted(target.rglob('*.md')):
        text = read_text(md)
        for raw in MARKDOWN_LINK_RE.findall(text):
            ref = raw.strip().strip('<>').split('#', 1)[0]
            if not ref or ref.startswith(('http://', 'https://', 'mailto:', 'skills://', 'sandbox:', '#')):
                continue
            resolved = (md.parent / ref).resolve(strict=False)
            try:
                resolved.relative_to(target.resolve())
            except ValueError:
                escaping_links.append({'file': md.relative_to(target).as_posix(), 'reference': ref})
                continue
            if not resolved.exists():
                missing_links.append({'file': md.relative_to(target).as_posix(), 'reference': ref})
    check('core/no-reference-escape', not escaping_links, f'escaping={escaping_links}')
    check('core/local-links-exist', not missing_links, f'missing={missing_links}')

    escaping_symlinks = []
    for path in sorted(target.rglob('*')):
        if not path.is_symlink():
            continue
        try:
            resolved = path.resolve(strict=True)
            resolved.relative_to(target.resolve())
        except (OSError, ValueError):
            escaping_symlinks.append(path.relative_to(target).as_posix())
    check('core/no-escaping-symlinks', not escaping_symlinks, f'escaping_symlinks={escaping_symlinks}')

    if 'allowed-tools:' in body[: body.find('\n---\n', 4) + 5 if body.startswith('---\n') else 0]:
        warnings.append('allowed-tools is an experimental host extension; portable behavior must not depend on it.')
    if re.search(r'^paths\s*:', body[: body.find('\n---\n', 4) + 5 if body.startswith('---\n') else 0], re.M):
        warnings.append('paths is a Cursor extension; portable behavior must remain correct when another host ignores it.')

    return checks, warnings


def validate_openai_adapter(target: Path) -> list[dict]:
    checks = []
    adapter = target / 'agents' / 'openai.yaml'
    if not adapter.exists():
        return [{'code': 'openai/adapter-optional', 'passed': True, 'severity': 'info', 'detail': 'agents/openai.yaml absent; portable core remains valid'}]
    text = read_text(adapter)
    checks.append({'code': 'openai/adapter-readable', 'passed': bool(text.strip()), 'severity': 'major', 'detail': 'agents/openai.yaml is non-empty'})
    for icon in re.findall(r'icon_(?:small|large):\s*([^\s#]+)', text):
        path = target / icon.strip('"\'')
        checks.append({'code': f'openai/icon:{icon}', 'passed': path.is_file(), 'severity': 'major', 'detail': f'{icon} exists={path.is_file()}'})
    return checks


def validate(target: Path, profile: str) -> dict:
    target = target.expanduser().resolve()
    checks, warnings = core_checks(target)
    adapters = {
        'openai': (target / 'agents' / 'openai.yaml').is_file(),
        'claude_frontmatter': any(token in read_text(target / 'SKILL.md') if (target / 'SKILL.md').exists() else '' for token in ('allowed-tools:',)),
        'cursor_paths_frontmatter': bool(re.search(r'^paths\s*:', read_text(target / 'SKILL.md') if (target / 'SKILL.md').exists() else '', re.M)),
    }
    if profile == 'openai':
        checks.extend(validate_openai_adapter(target))
    blocker = [c for c in checks if not c['passed'] and c['severity'] == 'blocker']
    major = [c for c in checks if not c['passed'] and c['severity'] == 'major']
    status = 'fail' if blocker else ('warn' if major or warnings else 'pass')
    return {
        'status': status,
        'profile': profile,
        'target': str(target),
        'portable_core_pass': not blocker,
        'checks': checks,
        'warnings': warnings,
        'host_adapters_detected': adapters,
        'profile_discovery_note': PROFILE_DISCOVERY[profile],
        'capability_contract': [
            'filesystem-read',
            'filesystem-write for apply/package',
            'Python 3.10+ for bundled deterministic helpers',
            'command execution for script-based gates',
            'network only when current research is requested/required',
            'artifact delivery for returned ZIP/report files',
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate the host-neutral Agent Skills core and report optional host adapters.')
    parser.add_argument('--target', required=True)
    parser.add_argument('--profile', choices=PROFILES, default='portable')
    parser.add_argument('--output')
    args = parser.parse_args()
    report = validate(Path(args.target), args.profile)
    dump_json(report, args.output)
    return 0 if report['status'] in {'pass', 'warn'} else 1


if __name__ == '__main__':
    raise SystemExit(main())
