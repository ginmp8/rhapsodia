"""Portable package and published-interface consistency; not host activation proof."""
import ast
import json
from pathlib import Path
import re
import sys
import unittest
SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))
from runtime_core.mcp import QUERY_SCHEMA

class ContractTests(unittest.TestCase):
    def test_query_schema_matches_published_mcp_contract(self):
        schema = json.loads((SKILL / 'contracts/runtime-query-v1.schema.json').read_text())
        self.assertEqual({k:v for k,v in schema.items() if k not in {'$schema','$id','title'}}, QUERY_SCHEMA)

    def test_entrypoint_top100_contains_start_authority_recovery_and_refs(self):
        text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
        top = '\n'.join(text.splitlines()[:100])
        for term in ('name: runtime-harness', 'Python 3.10+', 'Read-only', 'handoff-resume', 'No peer skill', 'byte', 'stop'):
            self.assertIn(term.casefold(), top.casefold())

    def test_all_local_document_links_resolve_inside_package(self):
        for doc in SKILL.rglob('*.md'):
            for reference in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
                if '://' in reference or reference.startswith('#'):
                    continue
                path = (doc.parent / reference.split('#')[0]).resolve()
                self.assertTrue(path.is_relative_to(SKILL.resolve()), (doc, reference))
                self.assertTrue(path.is_file(), (doc, reference))

    def test_python_sources_use_the_310_syntax_baseline(self):
        for path in SKILL.rglob('*.py'):
            ast.parse(path.read_text(encoding='utf-8'), filename=str(path), feature_version=(3,10))

    def test_runtime_imports_are_standard_library_or_package_local(self):
        imports = set()
        for path in (SKILL / 'scripts').rglob('*.py'):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(a.name.split('.')[0] for a in node.names)
                elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
                    imports.add(node.module.split('.')[0])
        self.assertFalse(imports - sys.stdlib_module_names - {'runtime_core'}, imports)

    def test_all_contracts_have_versioned_local_identity(self):
        for path in (SKILL / 'contracts').glob('*.json'):
            schema = json.loads(path.read_text())
            self.assertTrue(schema['$id'].startswith('urn:rhapsodia:runtime-'))
            self.assertEqual(schema['type'], 'object')
            self.assertFalse(schema['additionalProperties'])

if __name__ == '__main__':
    unittest.main()
