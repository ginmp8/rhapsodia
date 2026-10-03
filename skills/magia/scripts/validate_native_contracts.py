#!/usr/bin/env python3
"""Validate native package contracts and retained domain gates; never edits inputs."""
from __future__ import annotations
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from artifact_protocol import ContractError, load_json
ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    errors = []; checks = []
    for name in ('artifact-envelope.schema.json', 'artifact-actions.schema.json'):
        schema = load_json(ROOT / 'references' / name)
        if schema.get('additionalProperties') is not False or not schema.get('required'):
            errors.append(name + ': closed required object contract is missing')
        checks.append(name)
    for path in sorted((ROOT / 'scripts').glob('*.py')):
        try: ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        except (SyntaxError, UnicodeError) as exc: errors.append(str(exc))
    name = load_json(ROOT / "release.json")["name"]
    commands = []
    if name != 'rhapsodia-workspace':
        version = (ROOT / 'VERSION').read_text().strip()
        for relative, phrase in [('SKILL.md', 'ecosystem release `' + version + '`'),
                                 ('references/ecosystem-handoff-contract.md', 'Release `' + version + '`'),
                                 ('references/ecosystem-compatibility.md', 'Package versions must all equal `' + version + '`')]:
            if phrase not in (ROOT / relative).read_text():
                errors.append('active release documentation mismatch: ' + relative)
        if load_json(ROOT / 'references/ecosystem-handoff-contract.json')['compatibility']['required_ecosystem_release'] != version:
            errors.append('handoff required release differs from package version')
        policy = load_json(ROOT / 'references/artifact-native-policy.json')
        contract = load_json(ROOT / 'references/artifact-native-contract.json')
        if policy['producer'] != name or policy['default_root'] != contract['producer_roots'][name]:
            errors.append('producer/root ownership mismatch')
        if contract.get('workspace_required') is not False or contract.get('cross_owner_writes') is not False:
            errors.append('native authority boundary changed')
        for script in ('validate_ecosystem_handoff_contract.py', 'validate_ecosystem_compatibility.py',
                       'validate_ecosystem_routing_contract.py', 'validate_shared_contract_provenance.py',
                       'validate_ecosystem_release_metadata.py', 'validate_ecosystem_reproducibility.py'):
            if (ROOT/'scripts'/script).is_file():
                commands.append([script] if script == 'validate_ecosystem_reproducibility.py' else [script,'--target',str(ROOT)])
        if name == 'nomia':
            commands += [
                ['validate_activation_scenarios.py',str(ROOT/'examples/activation-scenarios.json')],
                ['validate_governance_scenarios.py',str(ROOT/'evals/governance-scenarios.json')],
                ['validate_golden_examples.py','--skill-root',str(ROOT)],
                *[[x,'--target',str(ROOT)] for x in ('validate_identity_contract.py','validate_contract_semantics.py',
                  'validate_release_contract.py','validate_contract_preservation.py','validate_documentation.py','validate_assurance_contract.py')]]
        # No executable peer imports or namespace lookups are required by native producers.
        for script in ('native_artifacts.py','migrate_artifacts.py'):
            if not (ROOT/'scripts'/script).is_file(): errors.append('missing '+script)
    else:
        for resource in ('scripts/workspace.py','assets/workspace.html','references/migration-boundary.md'):
            if not (ROOT/resource).is_file(): errors.append('missing '+resource)
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(ROOT/'scripts')}
    for command in commands:
        run=subprocess.run([sys.executable,'-B',str(ROOT/'scripts'/command[0]),*command[1:]],cwd=ROOT,env=env,capture_output=True,text=True,timeout=180)
        checks.append({'command':command,'returncode':run.returncode,'output_sha256':hashlib.sha256((run.stdout+'\n'+run.stderr).encode()).hexdigest()})
        if run.returncode: errors.append(command[0]+': '+(run.stdout+'\n'+run.stderr)[-5000:])
    print(json.dumps({'status':'pass' if not errors else 'fail','checks':checks,'errors':errors},indent=2))
    return 1 if errors else 0
if __name__ == '__main__':
    try: raise SystemExit(main())
    except (ContractError,OSError,ValueError,KeyError,subprocess.TimeoutExpired) as exc:
        print(json.dumps({'status':'fail','error':str(exc)})); raise SystemExit(1)
