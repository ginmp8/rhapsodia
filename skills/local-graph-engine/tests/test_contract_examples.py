"""Published contracts and examples remain consumable independently."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from graph_data import read_rows,rows_to_patch
from graph_common import read_json
from graph_engine import validate_patch_data
from graph_query import validate_request

class ContractExamples(unittest.TestCase):
    def test_people_example(self):
        rows=read_rows(ROOT/'examples/people.csv');mapping=read_json(ROOT/'examples/people-mapping.json')
        patch=rows_to_patch(rows,{'uri':'example://people','kind':'csv'},mapping)
        self.assertFalse(validate_patch_data(patch));self.assertEqual(len(patch['nodes']),5);self.assertEqual(len(patch['edges']),5)
        self.assertEqual(sum(float(n['properties'].get('budget',0)) for n in patch['nodes']),39000)
    def test_published_query_examples(self):
        for p in (ROOT/'examples').glob('query-*.json'):validate_request(read_json(p))
    @unittest.skipUnless(importlib.util.find_spec('jsonschema'),'optional JSON Schema evaluator unavailable')
    def test_json_schemas_and_examples(self):
        import jsonschema
        for p in (ROOT/'contracts').glob('*.schema.json'):jsonschema.Draft202012Validator.check_schema(read_json(p))
        patches=read_json(ROOT/'contracts/graph-patch-v1.schema.json');mapping=read_json(ROOT/'contracts/graph-mapping-v1.schema.json');query=read_json(ROOT/'contracts/graph-query-v1.schema.json')
        for p in (ROOT/'examples').glob('*patch.json'):jsonschema.validate(read_json(p),patches)
        jsonschema.validate(read_json(ROOT/'examples/people-mapping.json'),mapping)
        for p in (ROOT/'examples').glob('query-*.json'):jsonschema.validate(read_json(p),query)

if __name__=='__main__':unittest.main()
