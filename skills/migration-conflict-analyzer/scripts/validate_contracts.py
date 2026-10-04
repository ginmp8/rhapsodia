#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

REQUIRED_SCENARIOS = {
"duplicate-add-column","drop-column","rename-vs-drop-add","conflicting-indexes","conflicting-fks","migration-ordering","snapshot-divergence","raw-sql","non-idempotent-data-migration","concurrent-deploy-version-unknown","harmless-migration","unknown-operation","same-diff-rerun","base-migration-rewrite","parallel-same-timestamp-signal","duplicate-full-id","ef11-snapshot-lineage-mismatch","structured-data-mutation","destructive-rollback-recreation","alter-nullability-tightening","alter-length-precision-narrowing","constraint-existing-data","provider-branch-incomplete","runtime-dependent-migration","ef8-concurrent-startup-unprotected","ef10-concurrent-startup-lock-aware","ef10-explicit-migrate-transaction","review-deployment-sql-drift","generated-reviewed-sql-drift","sqlite-idempotent-script-unsupported","sqlite-rebuild-required","semantic-pending-model-changes","semantic-transaction-suppressed-command","postgresql-index-locking-potential","same-diff-rerun-v3"}
REQUIRED_RULE_FIELDS={"severity","confidence","gate","hazard_type","title"}
ACTIVATION_DESCRIPTION_CLUSTERS={
"migration-artifacts":(r"migration",r"\.cs\b|repository paths?|pasted migration code"),
"pull-request-or-diff":(r"pull requests?|\bprs?\b",r"git diffs?|\bdiffs?\b"),
"schema-and-ordering":(r"schema conflicts?",r"ordering hazards?"),
"destructive-and-duplicate":(r"data[- ]loss|destructive",r"duplicate operations?|migration lineage"),
"runtime-deployment":(r"runtime migration|deployment hazards?",r"database\.migrate(?:async)?|concurrent|ef core version"),
"snapshot-provider-artifact":(r"model snapshot|snapshot divergence|lineage",r"raw sql|reviewed sql|deployment sql",r"provider|sql server|postgres|sqlite"),
"non-trigger-boundaries":(r"do not use",r"generic ef core",r"database design",r"application code review")}

def load_json(path,errors):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:errors.append(f"invalid JSON {path}: {exc}");return {}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--skill-root",required=True);ap.add_argument("--json-out");ns=ap.parse_args();root=Path(ns.skill_root).resolve();errors=[];warnings=[]
    rels=["SKILL.md","scripts/migration_conflict_analyzer.py","references/heuristic-set.json","references/provider-profiles.json","schemas/analysis-report.schema.json","schemas/semantic-evidence.schema.json","evals/analyzer-regression-scenarios.json","evals/expected-heuristics.json","evals/run_analyzer_regressions.py"]
    for rel in rels:
        if not (root/rel).is_file(): errors.append(f"missing required path: {rel}")
    h=load_json(root/"references/heuristic-set.json",errors); profiles=load_json(root/"references/provider-profiles.json",errors); scenarios=load_json(root/"evals/analyzer-regression-scenarios.json",errors); expected=load_json(root/"evals/expected-heuristics.json",errors); schema=load_json(root/"schemas/analysis-report.schema.json",errors); semantic_schema=load_json(root/"schemas/semantic-evidence.schema.json",errors)
    if h.get("set_name")!="migration-conflict-analyzer": errors.append("heuristic set_name mismatch")
    if h.get("version")!="3.0.0": errors.append("heuristic version must be 3.0.0")
    rules=h.get("rules",{}); sev=set(h.get("severity_order",[])); conf=set(h.get("confidence_levels",[])); gates=set(h.get("gates",[]))
    if not isinstance(rules,dict) or not rules: errors.append("heuristic rules must be a non-empty object"); rules={}
    for rid,rule in sorted(rules.items()):
        miss=REQUIRED_RULE_FIELDS-set(rule)
        if miss: errors.append(f"rule {rid} missing fields: {sorted(miss)}")
        if rule.get("severity") not in sev: errors.append(f"rule {rid} invalid severity")
        if rule.get("confidence") not in conf: errors.append(f"rule {rid} invalid confidence")
        if rule.get("gate") not in gates: errors.append(f"rule {rid} invalid gate")
    if profiles.get("profile_version")!="1.0.0": errors.append("provider profile version must be 1.0.0")
    for p in ("sqlserver","postgresql","sqlite"):
        if p not in profiles.get("providers",{}): errors.append(f"missing provider profile {p}")
    if semantic_schema.get("$id")!="urn:migration-conflict-analyzer:semantic-evidence:1.0": errors.append("semantic evidence schema identity mismatch")
    if expected.get("heuristic_version")!=h.get("version"): errors.append("expected-heuristics version does not match heuristic set")
    for rid,contract in sorted(expected.get("required_rules",{}).items()):
        rule=rules.get(rid)
        if not rule: errors.append(f"expected rule missing from heuristic set: {rid}"); continue
        for f in ("severity","gate"):
            if rule.get(f)!=contract.get(f): errors.append(f"expected rule {rid} {f} mismatch: {rule.get(f)!r} != {contract.get(f)!r}")
    rows=scenarios.get("scenarios",[]); ids=[x.get("id") for x in rows if isinstance(x,dict)]
    if len(ids)!=len(set(ids)): errors.append("duplicate regression scenario IDs")
    missing=REQUIRED_SCENARIOS-set(ids)
    if missing: errors.append(f"missing required regression scenarios: {sorted(missing)}")
    for item in rows:
        if not isinstance(item,dict): errors.append("regression scenario must be an object"); continue
        for rid in item.get("expected_rules",[]):
            if rid not in rules: errors.append(f"scenario {item.get('id')} references unknown rule {rid}")
    if schema.get("$id")!="urn:migration-conflict-analyzer:analysis-report:3.0": errors.append("report schema identity mismatch")
    for field in ("provider_profiles","context","semantic_evidence","analysis_receipt"):
        if field not in set(schema.get("required",[])): errors.append(f"report schema missing required field {field}")
    analyzer=(root/"scripts/migration_conflict_analyzer.py").read_text(encoding="utf-8") if (root/"scripts/migration_conflict_analyzer.py").is_file() else ""
    if not re.search(r'^ANALYSIS_VERSION\s*=\s*"3\.0\.0"',analyzer,re.M): errors.append("analyzer ANALYSIS_VERSION is not 3.0.0")
    for token in ("provider-profiles.json","--ef-core-version","--provider","--reviewed-sql","--deployment-sql","--rollback-sql","--semantic-evidence"):
        if token not in analyzer: errors.append(f"analyzer missing v3 surface: {token}")
    skill=(root/"SKILL.md").read_text(encoding="utf-8") if (root/"SKILL.md").is_file() else ""
    for phrase in ("heuristic-set.json","analysis_receipt","stable finding IDs","uncertainty","provider-profiles.json","semantic evidence","reviewed SQL"):
        if phrase.lower() not in skill.lower(): errors.append(f"SKILL.md missing contract phrase: {phrase}")
    fm=re.match(r"\A---\n(?P<frontmatter>.*?)\n---\n",skill,re.S); desc=""
    if not fm: errors.append("SKILL.md missing valid YAML frontmatter block")
    else:
        m=re.search(r"(?m)^description:\s*(?P<description>.+)$",fm.group("frontmatter")); desc=m.group("description").strip().lower() if m else ""
        if not m: errors.append("SKILL.md frontmatter missing description")
    for cluster,patterns in ACTIVATION_DESCRIPTION_CLUSTERS.items():
        miss=[p for p in patterns if not re.search(p,desc,re.I)]
        if miss: errors.append(f"frontmatter activation description missing {cluster} capability cluster: {miss}")
    report={"validator_version":"2.0.0","status":"fail" if errors else ("warn" if warnings else "pass"),"errors":errors,"warnings":warnings,"metrics":{"rules":len(rules),"regression_scenarios":len(ids),"required_scenarios_present":len(REQUIRED_SCENARIOS-missing),"provider_profiles":len(profiles.get('providers',{}))}}
    out=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if ns.json_out: Path(ns.json_out).write_text(out,encoding="utf-8")
    print(out,end=""); return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
