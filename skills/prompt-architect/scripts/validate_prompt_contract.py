#!/usr/bin/env python3
"""Validate Prompt Architect prompt-contract v2 JSON using only the standard library."""
from __future__ import annotations
import argparse, json
from pathlib import Path

ALLOWED_MODES={"create","improve","review-only","validation-only","package-guidance"}
ALLOWED_AUTHORITY={"explicit","source-required","inferred","optional"}
ALLOWED_STATUS={"preserve","clarify","change","remove","blocked"}
ALLOWED_FREEZE={"frozen","planned","not-applicable"}
ALLOWED_CLAIM={"structural","behavioral","runtime"}
ALLOWED_CITATIONS={"required","optional","forbidden","not-applicable"}
ALLOWED_LEVERS={"prompt","model","context","tool-schema","application-control","fine-tuning","architecture","mixed","undetermined"}
ALLOWED_PORTABILITY={"portable-core","host-specific","unknown"}
ALLOWED_CONTROL={"semantic","format","authorization","security","side-effect","tooling","evidence","performance","other"}
ALLOWED_ENFORCEMENT={"prompt","native-schema","tool-schema","application","human-approval","evaluator","mixed"}
RUNTIME_CONTROL_CLASSES={"authorization","security","side-effect"}


def nonempty(v): return isinstance(v,str) and bool(v.strip())

def main()->int:
    ap=argparse.ArgumentParser(description="Validate a Prompt Architect prompt contract v2.")
    ap.add_argument("contract")
    args=ap.parse_args(); path=Path(args.contract); errors=[]; warnings=[]
    try: data=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"status":"fail","errors":[f"invalid JSON: {exc}"],"warnings":[]},indent=2)); return 1
    if data.get("contract_version") != 2: errors.append("contract_version must be 2")
    target=data.get("target")
    if not isinstance(target,dict): errors.append("target must be an object")
    else:
        for key in ("name","kind","executor","language"):
            if not nonempty(target.get(key)): errors.append(f"target.{key} must be a non-empty string")
    if data.get("mode") not in ALLOWED_MODES: errors.append("mode is invalid")
    lever=data.get("solution_lever")
    if not isinstance(lever,dict): errors.append("solution_lever must be an object")
    else:
        if lever.get("selected") not in ALLOWED_LEVERS: errors.append("solution_lever.selected is invalid")
        if not isinstance(lever.get("prompt_is_primary"),bool): errors.append("solution_lever.prompt_is_primary must be boolean")
        if not nonempty(lever.get("rationale")): errors.append("solution_lever.rationale must be non-empty")
        if lever.get("prompt_is_primary") and lever.get("selected") not in {"prompt","mixed"}: errors.append("prompt_is_primary=true requires selected prompt or mixed")
        if data.get("mode") in {"create","improve"} and lever.get("selected")=="undetermined": warnings.append("solution lever is undetermined for a mutating mode")
    profile=data.get("execution_profile")
    if not isinstance(profile,dict): errors.append("execution_profile must be an object")
    else:
        if profile.get("portability") not in ALLOWED_PORTABILITY: errors.append("execution_profile.portability is invalid")
        for key in ("provider","host","model"):
            if not nonempty(profile.get(key)): errors.append(f"execution_profile.{key} must be non-empty")
        if profile.get("portability")=="host-specific" and profile.get("host")=="unknown": errors.append("host-specific profile requires a known host")
        if not isinstance(profile.get("instruction_surfaces"),list): errors.append("execution_profile.instruction_surfaces must be a list")
        caps=profile.get("capabilities")
        if not isinstance(caps,dict): errors.append("execution_profile.capabilities must be an object")
        else:
            for key in ("structured_outputs","tool_calling","filesystem","web","human_approval"):
                if not nonempty(caps.get(key)): errors.append(f"execution_profile.capabilities.{key} must be non-empty")
    at=data.get("authority_and_trust")
    if not isinstance(at,dict): errors.append("authority_and_trust must be an object")
    else:
        if not isinstance(at.get("design_authority"),list) or not at.get("design_authority"): errors.append("authority_and_trust.design_authority must be a non-empty list")
        if not nonempty(at.get("runtime_instruction_authority")): errors.append("authority_and_trust.runtime_instruction_authority must be non-empty")
        if not nonempty(at.get("untrusted_data_policy")): errors.append("authority_and_trust.untrusted_data_policy must be non-empty")
    inputs=data.get("inputs")
    if not isinstance(inputs,dict): errors.append("inputs must be an object")
    else:
        for key in ("available","tools","sources"):
            if not isinstance(inputs.get(key),list): errors.append(f"inputs.{key} must be a list")
        ctx=inputs.get("context")
        if not isinstance(ctx,dict): errors.append("inputs.context must be an object")
        else:
            for key in ("stable","dynamic","untrusted"):
                if not isinstance(ctx.get(key),list): errors.append(f"inputs.context.{key} must be a list")
            for key in ("budget","placement_policy","overflow_strategy"):
                if not nonempty(ctx.get(key)): errors.append(f"inputs.context.{key} must be non-empty")
            if not isinstance(ctx.get("provenance_required"),bool): errors.append("inputs.context.provenance_required must be boolean")
    reqs=data.get("requirements"); seen=set()
    if not isinstance(reqs,list) or not reqs: errors.append("requirements must be a non-empty list")
    else:
        for i,r in enumerate(reqs):
            p=f"requirements[{i}]"
            if not isinstance(r,dict): errors.append(f"{p} must be an object"); continue
            rid=r.get("id")
            if not nonempty(rid): errors.append(f"{p}.id must be non-empty")
            elif rid in seen: errors.append(f"duplicate requirement id: {rid}")
            else: seen.add(rid)
            if not nonempty(r.get("text")): errors.append(f"{p}.text must be non-empty")
            if r.get("authority") not in ALLOWED_AUTHORITY: errors.append(f"{p}.authority is invalid")
            if not isinstance(r.get("protected"),bool): errors.append(f"{p}.protected must be boolean")
            if not nonempty(r.get("source")): errors.append(f"{p}.source must be non-empty")
            if r.get("status") not in ALLOWED_STATUS: errors.append(f"{p}.status is invalid")
            if r.get("control_class") not in ALLOWED_CONTROL: errors.append(f"{p}.control_class is invalid")
            if r.get("enforcement") not in ALLOWED_ENFORCEMENT: errors.append(f"{p}.enforcement is invalid")
            if r.get("control_class") in RUNTIME_CONTROL_CLASSES and r.get("enforcement")=="prompt": errors.append(f"{p} uses prompt-only enforcement for a runtime/security control")
            if r.get("protected") is True and r.get("status") in {"change","remove"} and not nonempty(str(r.get("reason",""))): errors.append(f"{p} changes/removes a protected requirement without a reason")
    output=data.get("output")
    if not isinstance(output,dict): errors.append("output must be an object")
    else:
        for key in ("format","language","citations","ordering","unknown_or_error_behavior"):
            if not nonempty(output.get(key)): errors.append(f"output.{key} must be non-empty")
        if output.get("citations") not in ALLOWED_CITATIONS: errors.append("output.citations is invalid")
        if not isinstance(output.get("sections"),list): errors.append("output.sections must be a list")
    if not isinstance(data.get("success_criteria"),list) or not data.get("success_criteria"): errors.append("success_criteria must be a non-empty list")
    if not isinstance(data.get("assumptions"),list): errors.append("assumptions must be a list")
    if not isinstance(data.get("unresolved_conflicts"),list): errors.append("unresolved_conflicts must be a list")
    val=data.get("validation")
    if not isinstance(val,dict): errors.append("validation must be an object")
    else:
        if val.get("freeze_state") not in ALLOWED_FREEZE: errors.append("validation.freeze_state is invalid")
        if val.get("claim_level") not in ALLOWED_CLAIM: errors.append("validation.claim_level is invalid")
        strong=val.get("claim_level") in {"behavioral","runtime"}
        if strong and val.get("freeze_state")!="frozen": errors.append("behavioral/runtime claim_level requires validation.freeze_state=frozen")
        if strong and not nonempty(val.get("suite_id")): errors.append("behavioral/runtime claim_level requires validation.suite_id")
        if strong:
            pid=val.get("execution_profile_identity")
            if not nonempty(pid): errors.append("behavioral/runtime claim_level requires validation.execution_profile_identity")
            elif isinstance(profile,dict) and nonempty(profile.get("profile_identity")) and pid != profile.get("profile_identity"): errors.append("validation.execution_profile_identity must match execution_profile.profile_identity")
        comp=val.get("comparison")
        if not isinstance(comp,dict): errors.append("validation.comparison must be an object")
        else:
            if not isinstance(comp.get("enabled"),bool): errors.append("validation.comparison.enabled must be boolean")
            if not isinstance(comp.get("repetitions"),int) or comp.get("repetitions",0)<1: errors.append("validation.comparison.repetitions must be >= 1")
            if not isinstance(comp.get("blinded"),bool) or not isinstance(comp.get("position_swap"),bool) or not isinstance(comp.get("ties_allowed"),bool): errors.append("validation.comparison bias-control fields must be boolean")
            if comp.get("enabled"):
                if not nonempty(comp.get("evaluator_kind")) or comp.get("evaluator_kind")=="none": errors.append("enabled comparison requires evaluator_kind")
                if not nonempty(comp.get("evaluator_identity")): errors.append("enabled comparison requires evaluator_identity")
                if comp.get("evaluator_kind")=="llm-judge" and strong:
                    if not comp.get("blinded"): errors.append("behavioral/runtime llm-judge comparison requires blinding")
                    if not comp.get("position_swap"): errors.append("behavioral/runtime llm-judge comparison requires position_swap")
                    if comp.get("repetitions",0)<2: errors.append("behavioral/runtime llm-judge comparison requires repetitions >= 2")
                    if not comp.get("ties_allowed"): errors.append("behavioral/runtime llm-judge comparison requires ties_allowed=true")
    blocked=[r for r in reqs or [] if isinstance(r,dict) and r.get("status")=="blocked"] if isinstance(reqs,list) else []
    if blocked and data.get("mode") in {"create","improve"}: warnings.append("contract contains blocked requirements; final prompt should not silently resolve them")
    status="fail" if errors else ("warn" if warnings else "pass")
    print(json.dumps({"status":status,"errors":errors,"warnings":warnings},indent=2,ensure_ascii=False,sort_keys=True))
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
