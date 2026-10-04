#!/usr/bin/env python3
import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path

EXPECTED = {
    "rhapsodia-supervisor.agent.md": {
        "name": "Rhapsodia Supervisor",
        "tools": {"read", "search", "agent"},
        "user_invocable": True,
        "agents": ["Rhapsodia Analyst", "Rhapsodia Verifier", "Nomia", "Mago", "Magia", "Rhapsodia Workspace"],
        "profile": "supervisor",
    },
    "rhapsodia-analyst.agent.md": {
        "name": "Rhapsodia Analyst",
        "tools": {"read", "search"},
        "user_invocable": False,
        "profile": "analyst",
    },
    "rhapsodia-verifier.agent.md": {
        "name": "Rhapsodia Verifier",
        "tools": {"read", "search", "edit", "execute"},
        "user_invocable": False,
        "profile": "verifier",
        "skill": "test-oracle-engineering",
    },
    "nomia.agent.md": {
        "name": "Nomia",
        "tools": {"read", "search", "edit", "execute"},
        "user_invocable": False,
        "profile": "worker",
        "skill": "nomia",
    },
    "mago.agent.md": {
        "name": "Mago",
        "tools": {"read", "search", "edit", "execute"},
        "user_invocable": False,
        "profile": "worker",
        "skill": "mago",
    },
    "magia.agent.md": {
        "name": "Magia",
        "tools": {"read", "search", "edit", "execute"},
        "user_invocable": False,
        "profile": "worker",
        "skill": "magia",
    },
    "rhapsodia-workspace.agent.md": {
        "name": "Rhapsodia Workspace", "tools": {"read", "search", "edit", "execute"},
        "user_invocable": False, "profile": "workspace", "skill": "rhapsodia-workspace",
    },
}

REQUIRED_SCENARIO_TYPES = {
    "core", "boundary", "regression", "ambiguous", "adversarial",
    "security", "failure", "privacy", "portability"
}


def add(findings, code, path, message, severity="error"):
    findings.append({"severity": severity, "code": code, "path": str(path), "message": message})


def parse_value(raw):
    raw = raw.strip()
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    if raw.startswith("["):
        try:
            return json.loads(raw)
        except Exception:
            return ast.literal_eval(raw)
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    return raw


def parse_frontmatter(path, findings):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        add(findings, "FRONTMATTER_MISSING", path, "agent file must start with YAML frontmatter")
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        add(findings, "FRONTMATTER_UNCLOSED", path, "frontmatter closing delimiter is missing")
        return {}, text
    header = text[4:end]
    body = text[end + 5:]
    data = {}
    for lineno, line in enumerate(header.splitlines(), 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith(" ") or ":" not in line:
            add(findings, "FRONTMATTER_UNSUPPORTED", path, f"unsupported frontmatter line {lineno}: {line}")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        try:
            data[key] = parse_value(value)
        except Exception as exc:
            add(findings, "FRONTMATTER_VALUE", path, f"cannot parse frontmatter field {key}: {exc}")
    return data, body


def validate_agent_file(path, spec, findings):
    fm, body = parse_frontmatter(path, findings)
    if fm.get("name") != spec["name"]:
        add(findings, "AGENT_NAME", path, f"name must be {spec['name']!r}")
    description = fm.get("description")
    if not isinstance(description, str) or not description.strip():
        add(findings, "DESCRIPTION", path, "description must be a non-empty string")
    if "model" in fm:
        add(findings, "MODEL_PINNING", path, "model must remain unpinned so the host/user controls model selection")
    if "mcp-servers" in fm:
        add(findings, "MCP_DEPENDENCY", path, "mcp-servers must not be a package requirement")
    if "target" in fm:
        add(findings, "TARGET_NARROWING", path, "target is intentionally omitted so the profile can be reused by VS Code and compatible Copilot surfaces")

    tools = fm.get("tools")
    if not isinstance(tools, list):
        add(findings, "TOOLS", path, "tools must be an explicit list")
        toolset = set()
    else:
        toolset = set(tools)
    if toolset != spec["tools"]:
        add(findings, "TOOLS", path, f"tools must be exactly {sorted(spec['tools'])}; got {sorted(toolset)}")

    if fm.get("user-invocable") is not spec["user_invocable"]:
        add(findings, "USER_INVOCABLE", path, f"user-invocable must be {str(spec['user_invocable']).lower()}")
    if fm.get("disable-model-invocation") is not False:
        add(findings, "SUBAGENT_INVOCATION", path, "disable-model-invocation must be false so native delegation remains available")

    if spec["profile"] == "supervisor":
        if "edit" in toolset or "execute" in toolset:
            add(findings, "SUPERVISOR_WRITE_TOOL", path, "supervisor must remain read-only and non-executing")
        if "agent" not in toolset:
            add(findings, "SUPERVISOR_AGENT_TOOL", path, "supervisor requires the native agent tool")
        if fm.get("agents") != spec["agents"]:
            add(findings, "SUPERVISOR_ALLOWLIST", path, f"agents allowlist must be exactly {spec['agents']}")
        normalized_body = body.replace("`", "")
        for phrase in (
            "maximum 24 total subagent delegations",
            "maximum 4 analyst work units",
            "maximum 4 gated checkpoints",
            "maximum 2 checkpoint repair re-entries",
            "maximum 2 re-entries",
            "zero materially identical canonical handoff, analyst work-unit, or verifier work-unit repeats",
            "Rhapsodia Analyst is the only profile eligible for adaptive read-only fan-out",
            "not promotable",
            "Never create, repair, or modify ecosystem handoff v3 yourself",
        ):
            if phrase not in normalized_body:
                add(findings, "SUPERVISOR_INVARIANT", path, f"missing required supervisor invariant: {phrase}")
    elif spec["profile"] == "analyst":
        if toolset != {"read", "search"}:
            add(findings, "ANALYST_TOOL_SCOPE", path, "analyst must expose only read and search")
        if "agent" in toolset or "edit" in toolset or "execute" in toolset:
            add(findings, "ANALYST_TOOL_SCOPE", path, "analyst must not receive agent/edit/execute tools")
        if "agents" in fm:
            add(findings, "ANALYST_ALLOWLIST", path, "analyst must not declare a subagent allowlist")
        for phrase in (
            "read-only work unit",
            "Must not:",
            "emit ecosystem handoff v3",
            "invoke another custom agent directly",
            "canonical_mutation_performed`: false",
        ):
            if phrase not in body:
                add(findings, "ANALYST_INVARIANT", path, f"missing required analyst invariant: {phrase}")
    elif spec["profile"] == "verifier":
        if toolset != {"read", "search", "edit", "execute"}:
            add(findings, "VERIFIER_TOOL_SCOPE", path, "verifier tools must be exactly read/search/edit/execute")
        if "agent" in toolset or "agents" in fm:
            add(findings, "VERIFIER_DELEGATION", path, "verifier must not delegate to other custom agents")
        for phrase in (
            "installed `test-oracle-engineering` Agent Skill",
            "Must not:",
            "edit production implementation",
            "production_mutation_performed`: false",
            "criteria_changed`: false",
            "canonical_phase_completed`: false",
            "invoke another custom agent directly",
        ):
            if phrase not in body:
                add(findings, "VERIFIER_INVARIANT", path, f"missing required verifier invariant: {phrase}")
    else:
        if "agent" in toolset:
            add(findings, "WORKER_DELEGATION_TOOL", path, "workers must not receive the native agent tool")
        if "agents" in fm:
            add(findings, "WORKER_ALLOWLIST", path, "workers must not declare a subagent allowlist")
        skill = spec["skill"]
        marker = f"installed `{skill}` Agent Skill"
        if marker not in body:
            add(findings, "SKILL_BINDING", path, f"worker must bind to {marker}")
        if "invoke another custom agent directly" not in body:
            add(findings, "WORKER_RECURSION_BOUNDARY", path, "worker must explicitly prohibit direct custom-agent invocation")

    if spec["profile"] == "workspace":
        for marker in ("canonical_mutation_performed`: false", "domain_state_changed`: false", "derived outputs only", "emit ecosystem handoff v3"):
            if marker not in body:
                add(findings, "WORKSPACE_BOUNDARY", path, f"missing derived-only boundary: {marker}")
    if spec["profile"] == "worker":
        for marker in ("artifact_actions", "artifact-native", "Workspace is optional"):
            if marker not in body:
                add(findings, "ARTIFACT_OWNERSHIP", path, f"missing native artifact orchestration contract: {marker}")

    if len(body) > 30000:
        add(findings, "PROMPT_LENGTH", path, "agent body exceeds the documented 30,000 character prompt limit")


def validate_contract(path, findings):
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        add(findings, "CONTRACT_JSON", path, f"invalid JSON: {exc}")
        return
    if doc.get("contract") != "agent-system-contract/v3":
        add(findings, "CONTRACT_ID", path, "contract must be agent-system-contract/v3")
    if doc.get("system", {}).get("autonomy") != "policy-bounded-autonomous":
        add(findings, "AUTONOMY", path, "system autonomy must remain policy-bounded-autonomous")
    routing = doc.get("routing", {})
    if routing.get("type") != "centralized-supervisor":
        add(findings, "ROUTING_TYPE", path, "routing must be centralized-supervisor")
    if routing.get("max_hops") != 24:
        add(findings, "MAX_HOPS", path, "routing.max_hops must be 24")
    if routing.get("reentry_requires_state_change") is not True:
        add(findings, "REENTRY", path, "re-entry must require a material state change")
    supporting = routing.get("supporting_capability_resolution")
    expected_supporting = {
        "selection": "semantic-capability",
        "binding": "host-native-agent-skill-discovery",
        "fixed_skill_catalog": False,
        "authority_precedence": "active-agent-contract",
        "ownership_precedence": "canonical-lifecycle-owner",
        "required_unavailable": "blocked",
        "optional_unavailable": "continue-with-not-run",
        "supporting_skill_may_expand_authority": False,
        "supporting_skill_may_change_owner": False,
    }
    if not isinstance(supporting, dict):
        add(findings, "SUPPORTING_CAPABILITY_RESOLUTION", path, "routing.supporting_capability_resolution is required")
    else:
        for key, value in expected_supporting.items():
            if supporting.get(key) != value:
                add(findings, "SUPPORTING_CAPABILITY_RESOLUTION", path, f"routing.supporting_capability_resolution.{key} must be {value!r}")
    budgets = doc.get("budgets", {})
    if budgets.get("max_reentries_per_owner") != 2:
        add(findings, "REENTRY_BUDGET", path, "max_reentries_per_owner must be 2")
    if budgets.get("max_identical_handoff_repeats") != 0:
        add(findings, "IDENTICAL_REPEAT_BUDGET", path, "identical handoff repeats must be zero")
    if budgets.get("max_work_units_per_phase") != 4:
        add(findings, "WORK_UNIT_BUDGET", path, "max_work_units_per_phase must be 4")
    if budgets.get("max_parallel_work_units") != 4:
        add(findings, "WORK_UNIT_BUDGET", path, "max_parallel_work_units must be 4")
    if budgets.get("max_checkpoints_per_magia_phase") != 4:
        add(findings, "CHECKPOINT_BUDGET", path, "max_checkpoints_per_magia_phase must be 4")
    if budgets.get("max_checkpoint_repairs") != 2:
        add(findings, "CHECKPOINT_BUDGET", path, "max_checkpoint_repairs must be 2")
    if budgets.get("max_adversarial_reviews_per_checkpoint") != 2:
        add(findings, "CHECKPOINT_BUDGET", path, "max_adversarial_reviews_per_checkpoint must be 2")
    if budgets.get("max_verifier_units_per_candidate") != 1:
        add(findings, "CHECKPOINT_BUDGET", path, "max_verifier_units_per_candidate must be 1")
    adaptive = routing.get("adaptive_execution", {})
    if adaptive.get("scope") != "inside-one-resolved-lifecycle-phase":
        add(findings, "ADAPTIVE_SCOPE", path, "adaptive execution must remain inside one resolved lifecycle phase")
    if adaptive.get("read_only_worker") != "rhapsodia-analyst":
        add(findings, "ADAPTIVE_WORKER", path, "adaptive read-only worker must be rhapsodia-analyst")
    if adaptive.get("canonical_writer_count") != 1:
        add(findings, "SINGLE_WRITER", path, "adaptive execution must keep exactly one canonical writer")
    if adaptive.get("write_capable_worker_fanout") is not False:
        add(findings, "WRITE_FANOUT", path, "write-capable canonical worker fan-out must be false")
    if adaptive.get("parallel_fallback") != "serial":
        add(findings, "ADAPTIVE_FALLBACK", path, "parallel fallback must be serial")
    if adaptive.get("executable_verifier") != "rhapsodia-verifier":
        add(findings, "VERIFIER_ROUTING", path, "adaptive executable verifier must be rhapsodia-verifier")
    if adaptive.get("verifier_domain_owner") != "magia" or adaptive.get("verifier_production_write") is not False:
        add(findings, "VERIFIER_AUTHORITY", path, "verifier must remain Magia-scoped and forbidden from production writes")
    gated = adaptive.get("gated_convergence", {})
    expected_gated = {
        "max_checkpoints_per_magia_phase": 4,
        "max_checkpoint_repairs": 2,
        "max_adversarial_reviews_per_checkpoint": 2,
        "max_verifier_units_per_candidate": 1,
        "required_gate_failure_overridable": False,
        "candidate_repair_invalidates_affected_gate_passes": True,
        "dependency_requires_promoted_checkpoint": True,
        "accepted_feedback_only": True,
        "producer_verifier_concurrency": False,
    }
    for key, value in expected_gated.items():
        if gated.get(key) != value:
            add(findings, "GATED_CONVERGENCE", path, f"routing.adaptive_execution.gated_convergence.{key} must be {value!r}")
    artifacts = doc.get("artifact_orchestration", {})
    expected_artifacts = {"default_storage_profile": "artifact-native", "selection_owner": "domain-skill", "source_of_truth": "producer-owned-artifacts", "workspace_required_for_domain_execution": False, "projection_writeback": False, "domain_state_inference": False}
    for key, expected in expected_artifacts.items():
        if artifacts.get(key) != expected:
            add(findings, "ARTIFACT_ORCHESTRATION", path, f"artifact_orchestration.{key} must be {expected!r}")
    derived = routing.get("derived_workspace", {})
    if derived.get("canonical_write") is not False or derived.get("trigger") != "explicit-visualization-request" or derived.get("max_refresh_attempts") != 2 or derived.get("concurrent_with_canonical_writer") is not False:
        add(findings, "WORKSPACE_ROUTING", path, "workspace must be optional, derived-only, serial and bounded")
    ids = [a.get("id") for a in doc.get("agents", [])]
    if ids != ["rhapsodia-supervisor", "rhapsodia-analyst", "rhapsodia-verifier", "nomia", "mago", "magia", "rhapsodia-workspace"]:
        add(findings, "AGENT_CONTRACT_SET", path, "contract agent ids/order do not match the package")
    capability_ids = {c.get("id") for c in doc.get("capabilities", []) if isinstance(c, dict)}
    capabilities = doc.get("capabilities", [])
    if len(capability_ids) != len(capabilities):
        add(findings, "CAPABILITY_CONTRACT", path, "capability IDs must be unique")
    for capability in capabilities:
        if not isinstance(capability, dict):
            add(findings, "CAPABILITY_CONTRACT", path, "each capability must be an object")
            continue
        valid = (isinstance(capability.get("id"), str)
                 and type(capability.get("required")) is bool
                 and capability.get("effect") in {"read-only", "local-write", "external-write"}
                 and isinstance(capability.get("scope"), list) and capability["scope"]
                 and all(isinstance(item, str) and item.strip() for item in capability["scope"])
                 and capability.get("approval") in {"none", "policy", "human"}
                 and capability.get("idempotency") in {"not-applicable", "required", "reconcile-before-retry"})
        if not valid:
            add(findings, "CAPABILITY_CONTRACT", path, "capability authority fields must be complete and typed")
    for agent in doc.get("agents", []):
        if isinstance(agent, dict) and any(cap not in capability_ids for cap in agent.get("capabilities", [])):
            add(findings, "CAPABILITY_CONTRACT", path, "agent references an undeclared capability")
    derived_cap = next((cap for cap in capabilities if isinstance(cap, dict) and cap.get("id") == "derived-output-write"), {})
    if (derived_cap.get("required") is not False or derived_cap.get("effect") != "local-write"
            or derived_cap.get("scope") != [".rhapsodia/catalog", ".rhapsodia/views"]
            or derived_cap.get("approval") != "policy" or derived_cap.get("idempotency") != "required"):
        add(findings, "WORKSPACE_CAPABILITY", path, "Workspace writes must be optional, policy-bounded and derived-only")
    delegation = next((cap for cap in capabilities if isinstance(cap, dict) and cap.get("id") == "specialist-delegation"), {})
    if "Rhapsodia Workspace" not in delegation.get("scope", []):
        add(findings, "WORKSPACE_CAPABILITY", path, "Workspace must be included in declared delegation scope")
    if "supporting-capability-resolution" not in capability_ids:
        add(findings, "SUPPORTING_CAPABILITY_RESOLUTION", path, "supporting-capability-resolution capability must be declared")
    for agent in doc.get("agents", []):
        if not isinstance(agent, dict) or agent.get("id") == "rhapsodia-supervisor":
            continue
        if "supporting-capability-resolution" not in agent.get("capabilities", []):
            add(findings, "SUPPORTING_CAPABILITY_RESOLUTION", path, f"agent {agent.get('id')!r} must expose supporting-capability-resolution")
    vscode = next((h for h in doc.get("hosts", []) if h.get("host") == "vscode"), None)
    if not vscode or vscode.get("status") != "supported":
        add(findings, "VSCODE_HOST", path, "VS Code must be declared supported in the primary adapter contract")
    mappings = (vscode or {}).get("capability_mapping", {})
    if mappings.get("specialist-delegation") != "agent tool with agents allowlist":
        add(findings, "VSCODE_DELEGATION", path, "VS Code delegation must map to native agent tool plus allowlist")
    analyst_mapping = mappings.get("read-only-analysis", "")
    if "read + search" not in analyst_mapping:
        add(findings, "VSCODE_ANALYST_SCOPE", path, "VS Code read-only analysis must map to an explicit read + search-only analyst profile")
    verifier_mapping = mappings.get("executable-verification", "")
    if "Rhapsodia Verifier" not in verifier_mapping or "verification-only" not in verifier_mapping:
        add(findings, "VSCODE_VERIFIER_SCOPE", path, "VS Code executable verification must map to the bounded Rhapsodia Verifier profile")
    workspace_mapping = mappings.get("derived-output-write", "")
    if not all(text in workspace_mapping for text in ("Rhapsodia Workspace", "derived-only", ".rhapsodia/catalog", ".rhapsodia/views")):
        add(findings, "WORKSPACE_CAPABILITY", path, "VS Code must map the bounded Workspace write capability")
    support_mapping = mappings.get("supporting-capability-resolution", "")
    if "host-native" not in support_mapping.lower() or "no fixed catalog" not in support_mapping.lower():
        add(findings, "SUPPORTING_CAPABILITY_RESOLUTION", path, "VS Code supporting capability resolution must use host-native Agent Skills with no fixed catalog")


def validate_manifest(root, path, findings):
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        add(findings, "MANIFEST_INTEGRITY", path, f"invalid manifest JSON: {exc}")
        return
    files = doc.get("files")
    if not isinstance(files, list):
        add(findings, "MANIFEST_INTEGRITY", path, "manifest files must be a list")
        return
    declared = {}
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            add(findings, "MANIFEST_INTEGRITY", path, "manifest contains an invalid file record")
            continue
        rel = item["path"]
        if rel in declared:
            add(findings, "MANIFEST_INTEGRITY", path, f"manifest contains duplicate path: {rel}")
            continue
        declared[rel] = item
    actual = {}
    full_repo = (root / "skills").is_dir()
    for artifact in root.rglob("*"):
        if not artifact.is_file() or artifact.name == "MANIFEST.json":
            continue
        if "__pycache__" in artifact.parts or artifact.suffix in {".pyc", ".pyo"}:
            continue
        rel = artifact.relative_to(root).as_posix()
        if full_repo:
            in_agent_surface = (
                rel in {"README.md", "LICENSE", "scripts/generate_agent_manifest.py", "scripts/install_agents.py", "scripts/validate_agents.py",
                        "tests/agent-scenarios.json", "tests/test_install_agents.py", "tests/test_validate_agents.py"}
                or rel.startswith("agents/")
                or rel.startswith("docs/agents/")
            )
            if not in_agent_surface:
                continue
        actual[rel] = artifact
    missing = sorted(set(declared) - set(actual))
    extra = sorted(set(actual) - set(declared))
    if missing or extra:
        add(findings, "MANIFEST_INTEGRITY", path, f"manifest file set mismatch: missing={missing}, extra={extra}")
    for rel in sorted(set(declared) & set(actual)):
        artifact = actual[rel]
        data = artifact.read_bytes()
        item = declared[rel]
        if item.get("size") != len(data) or item.get("sha256") != hashlib.sha256(data).hexdigest():
            add(findings, "MANIFEST_INTEGRITY", path, f"manifest hash/size mismatch: {rel}")


def validate_scenarios(path, findings):
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        add(findings, "SCENARIO_JSON", path, f"invalid JSON: {exc}")
        return
    if doc.get("suite") != "rhapsodia-agent-scenarios/v1":
        add(findings, "SCENARIO_SUITE", path, "unexpected scenario suite identity")
    scenarios = doc.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        add(findings, "SCENARIOS", path, "scenario suite must contain scenarios")
        return
    ids = []
    types = set()
    for i, item in enumerate(scenarios):
        if not isinstance(item, dict):
            add(findings, "SCENARIO_ITEM", path, f"scenario {i} must be an object")
            continue
        sid = item.get("id")
        if not isinstance(sid, str) or not sid:
            add(findings, "SCENARIO_ID", path, f"scenario {i} requires id")
        else:
            ids.append(sid)
        stype = item.get("type")
        if isinstance(stype, str):
            types.add(stype)
        for key in ("prompt", "expected_route", "expected_behavior"):
            if not isinstance(item.get(key), str) or not item.get(key).strip():
                add(findings, "SCENARIO_FIELD", path, f"scenario {sid or i} requires non-empty {key}")
    if len(ids) != len(set(ids)):
        add(findings, "SCENARIO_DUPLICATE_ID", path, "scenario ids must be unique")
    missing = sorted(REQUIRED_SCENARIO_TYPES - types)
    if missing:
        add(findings, "SCENARIO_COVERAGE", path, f"missing scenario types: {missing}")
    if len(scenarios) < 20:
        add(findings, "SCENARIO_COUNT", path, "at least 20 planned scenarios are required for this multi-agent package")


def validate(target):
    findings = []
    root = target.resolve()
    agents_dir = root / "agents"
    if not agents_dir.is_dir():
        add(findings, "AGENTS_DIR", agents_dir, "agents directory is missing")
        return findings
    actual = sorted(p.name for p in agents_dir.glob("*.agent.md"))
    if actual != sorted(EXPECTED):
        add(findings, "AGENT_FILE_SET", agents_dir, f"expected exactly {sorted(EXPECTED)}, got {actual}")
    for filename, spec in EXPECTED.items():
        path = agents_dir / filename
        if not path.is_file():
            add(findings, "AGENT_FILE", path, "required agent file is missing")
            continue
        validate_agent_file(path, spec, findings)

    contract = root / "docs" / "agents" / "contracts" / "rhapsodia-agent-system.json"
    if contract.is_file():
        validate_contract(contract, findings)
    else:
        add(findings, "CONTRACT_MISSING", contract, "portable agent-system contract is missing")

    manifest = root / "MANIFEST.json"
    if manifest.is_file():
        validate_manifest(root, manifest, findings)
    else:
        add(findings, "MANIFEST_INTEGRITY", manifest, "agent package manifest is missing")

    installer = root / "scripts" / "install_agents.py"
    if not installer.is_file():
        add(findings, "INSTALLER_MISSING", installer, "agent installer is missing")

    scenarios = root / "tests" / "agent-scenarios.json"
    if scenarios.is_file():
        validate_scenarios(scenarios, findings)
    else:
        add(findings, "SCENARIOS_MISSING", scenarios, "validation scenario suite is missing")

    for artifact in root.rglob("*"):
        if not artifact.is_file():
            continue
        rel = artifact.relative_to(root).as_posix()
        if "__pycache__" in artifact.parts or artifact.suffix in {".pyc", ".pyo"}:
            add(findings, "PACKAGE_HYGIENE", artifact, f"generated Python bytecode must not be packaged: {rel}")

    for rel in ("README.md", "docs/agents/ARCHITECTURE.md", "docs/agents/SOURCES.md"):
        if not (root / rel).is_file():
            add(findings, "DOC_MISSING", root / rel, "required documentation file is missing")
    return findings


def main():
    ap = argparse.ArgumentParser(description="Validate the Rhapsodia VS Code agent package.")
    ap.add_argument("--target", required=True)
    ap.add_argument("--json-output")
    args = ap.parse_args()
    target = Path(args.target)
    findings = validate(target)
    errors = [f for f in findings if f["severity"] == "error"]
    result = {
        "validator": "rhapsodia-agent-validator/v2",
        "status": "pass" if not errors else "fail",
        "target": str(target.resolve()),
        "errors": len(errors),
        "warnings": len(findings) - len(errors),
        "findings": findings,
    }
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.json_output:
        Path(args.json_output).write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
