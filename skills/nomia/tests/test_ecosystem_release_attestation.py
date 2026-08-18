from __future__ import annotations
import importlib.util, json, shutil, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("release_attestation",ROOT/"scripts/validate_ecosystem_release.py")
assert SPEC and SPEC.loader
mod=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(mod)

class ReleaseAttestationTests(unittest.TestCase):
    def make_roots(self,base:Path):
        roots={}
        contract={"ecosystem_release":"1.7.0"}
        for role in mod.ROLE_ORDER:
            root=base/role; roots[role]=root
            (root/"scripts").mkdir(parents=True); (root/"references").mkdir(); (root/"evals").mkdir()
            (root/"SKILL.md").write_text(f"---\nname: {role}\ndescription: test package description with enough words for fixture validation only\n---\n",encoding="utf-8")
            (root/"VERSION").write_text("1.7.0\n",encoding="utf-8")
            (root/"release.json").write_text(json.dumps({"name":role,"version":"1.7.0"}),encoding="utf-8")
            (root/"scripts/package_skill.py").write_text("print('fixture')\n",encoding="utf-8")
            for rel in mod.SHARED_REQUIRED:
                p=root/rel; p.parent.mkdir(parents=True,exist_ok=True)
                content=json.dumps(contract,sort_keys=True) if rel=="references/ecosystem-compatibility.json" else "shared\n"
                p.write_text(content,encoding="utf-8")
        return roots

    def test_preflight_accepts_matching_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            roots=self.make_roots(Path(tmp))
            self.assertEqual(mod.collect_preflight_errors(roots),[])

    def test_preflight_rejects_mixed_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            roots=self.make_roots(Path(tmp)); (roots['magia']/"VERSION").write_text("1.9.0\n"); release=json.loads((roots['magia']/"release.json").read_text()); release['version']='1.9.0'; (roots['magia']/"release.json").write_text(json.dumps(release))
            self.assertTrue(any('mixed package versions' in item for item in mod.collect_preflight_errors(roots)))

    def test_preflight_rejects_contract_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            roots=self.make_roots(Path(tmp)); (roots['magia']/"references/ecosystem-handoff-contract.json").write_text("drift\n")
            self.assertTrue(any('shared resource differs' in item for item in mod.collect_preflight_errors(roots)))

    def test_preflight_rejects_missing_negative_harness(self):
        with tempfile.TemporaryDirectory() as tmp:
            roots=self.make_roots(Path(tmp)); (roots['nomia']/"scripts/run_ecosystem_negative_harness.py").unlink()
            self.assertTrue(any('missing coordinated resource scripts/run_ecosystem_negative_harness.py' in item for item in mod.collect_preflight_errors(roots)))

    def test_gate_timeout_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=mod.run_gate('timeout',[sys.executable,'-c','import time; time.sleep(1)'],Path(tmp),Path(tmp),0.05)
            self.assertEqual(result['status'],'timeout')

    def test_stable_digest_ignores_timestamps_and_durations(self):
        a={'schema_version':'1','generated_at':'one','ecosystem_release':'1.7.0','versions':{},'root_tree_hashes':{},'shared_hashes':{},'packages':{},'gates':[{'name':'x','status':'pass','exit_code':0,'required':True,'duration_ms':1}],'status':'pass'}
        b=json.loads(json.dumps(a)); b['generated_at']='two'; b['gates'][0]['duration_ms']=999
        self.assertEqual(mod.attestation_digest(a),mod.attestation_digest(b))

if __name__=='__main__': unittest.main()
