import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("select_visual", ROOT/"scripts"/"select_visual.py")
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def sig(**kw):
    base=dict(explicit_visual=None, temporal=False, branching_retry=False, state_lifecycle=False, data_relationship=False, component_dependency=False, historical_sequence=False, file_responsibilities=False)
    base.update(kw); return base

def test_explicit_wins(): assert mod.choose("system-explanation", sig(explicit_visual="er", temporal=True))[0]["type"] == "er"
def test_change_map_primary(): assert mod.choose("change-review", sig(file_responsibilities=True, temporal=True)) == [{"role":"primary","type":"change-map"},{"role":"secondary","type":"sequence"}]
def test_tie_break_temporal(): assert mod.choose("system-explanation", sig(temporal=True, data_relationship=True))[0]["type"] == "sequence"
def test_arch_default_for_system(): assert mod.choose("system-explanation", sig())[0]["type"] == "architecture"
def test_none_default_for_scratchpad(): assert mod.choose("visual-scratchpad", sig())[0]["type"] == "none"
def test_archaeology_timeline(): assert mod.choose("code-archaeology", sig(historical_sequence=True, component_dependency=True))[0]["type"] == "timeline"
