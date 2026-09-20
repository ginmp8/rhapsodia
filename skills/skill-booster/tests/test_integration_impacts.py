import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('m',ROOT/'scripts/analyze_integration_impacts.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def mk(root,name,exports,imports):
 root.mkdir(parents=True);(root/'contracts').mkdir();(root/'surface.txt').write_text('x')
 (root/'contracts/integration-manifest.json').write_text(json.dumps({'manifest_version':1,'skill':name,'exports':exports,'imports':imports}))
def exp(cid,v):return {'contract_id':cid,'version':v,'role':'owner-producer','surface_paths':['surface.txt']}
def imp(cid,versions):return {'contract_id':cid,'accepted_versions':versions,'required_for':['x']}
def test_compatible(tmp_path):
 a=tmp_path/'a';b=tmp_path/'b';mk(a,'a',[exp('c',2)],[]);mk(b,'b',[],[imp('c',[2])]);r=m.analyze(a,None,[b]);assert r['status']!='fail'
def test_incompatible_consumer(tmp_path):
 a=tmp_path/'a';b=tmp_path/'b';mk(a,'a',[exp('c',2)],[]);mk(b,'b',[],[imp('c',[1])]);r=m.analyze(a,None,[b]);assert any('consumer_incompatible' in x for x in r['errors'])
def test_surface_change_requires_bump(tmp_path):
 old=tmp_path/'b1'/'s';new=tmp_path/'b2'/'s';mk(old,'s',[exp('c',1)],[]);mk(new,'s',[exp('c',1)],[]);(new/'surface.txt').write_text('changed');r=m.analyze(new,old,[]);assert any('surface_changed_without_version_bump' in x for x in r['errors'])
def test_multiple_owners_fail(tmp_path):
 a=tmp_path/'a';b=tmp_path/'b';c=tmp_path/'c';mk(a,'a',[exp('x',1)],[]);mk(b,'b',[exp('x',1)],[]);mk(c,'c',[],[imp('x',[1])]);r=m.analyze(a,None,[b,c]);assert any('multiple_owners' in x for x in r['errors'])
def test_unresolved_import_fails_with_catalog(tmp_path):
 a=tmp_path/'a';b=tmp_path/'b';mk(a,'a',[],[imp('missing',[1])]);mk(b,'b',[exp('other',1)],[]);r=m.analyze(a,None,[b]);assert any('unresolved_import' in x for x in r['errors'])
