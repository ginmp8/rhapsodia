#!/usr/bin/env python3
import argparse
import ast
import json
import sys
from pathlib import Path

EXPECTED = {
    "rhapsodia-supervisor.agent.md": {
        "name": "Rhapsodia Supervisor",
        "tools": {"read", "search", "agent"},
        "user_invocable": True,
        "agents": ["Nomia", "Mago", "Magia"],
        "profile": "supervisor",
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
        for phrase in (
            "maximum 12 specialist delegations",
            "maximum 2 re-entries",
            "zero materially identical handoff repeats",
            "Never create, repair, or modify ecosystem handoff v3 yourself",
        ):
            if phrase not in body:
                add(findings, "SUPERVISOR_BUDGET_TEXT", path, f"missing required supervisor invariant: {phrase}")
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

    if len(body) > 30000:
        add(findings, "PROMPT_LENGTH", path, "agent body exceeds the documented 30,000 character prompt limit")


def validate_contract(path, findings):
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        add(findings, "CONTRACT_JSON", path, f"invalid JSON: {exc}")
        return
    if doc.get("contract") != "agent-system-contract/v1":
        add(findings, "CONTRACT_ID", path, "contract must be agent-system-contract/v1")
    if doc.get("system", {}).get("autonomy") != "policy-bounded-autonomous":
        add(findings, "AUTONOMY", path, "system autonomy must remain policy-bounded-autonomous")
    routing = doc.get("routing", {})
    if routing.get("type") != "centralized-supervisor":
        add(findings, "ROUTING_TYPE", path, "routing must be centralized-supervisor")
    if routing.get("max_hops") != 12:
        add(findings, "MAX_HOPS", path, "routing.max_hops must be 12")
    if routing.get("reentry_requires_state_change") is not True:
        add(findings, "REENTRY", path, "re-entry must require a material state change")
    budgets = doc.get("budgets", {})
    if budgets.get("max_reentries_per_owner") != 2:
        add(findings, "REENTRY_BUDGET", path, "max_reentries_per_owner must be 2")
    if budgets.get("max_identical_handoff_repeats") != 0:
        add(findings, "IDENTICAL_REPEAT_BUDGET", path, "identical handoff repeats must be zero")
    ids = [a.get("id") for a in doc.get("agents", [])]
    if ids != ["rhapsodia-supervisor", "nomia", "mago", "magia"]:
        add(findings, "AGENT_CONTRACT_SET", path, "contract agent ids/order do not match the package")
    vscode = next((h for h in doc.get("hosts", []) if h.get("host") == "vscode"), None)
    if not vscode or vscode.get("status") != "supported":
        add(findings, "VSCODE_HOST", path, "VS Code must be declared supported in the primary adapter contract")
    mappings = (vscode or {}).get("capability_mapping", {})
    if mappings.get("specialist-delegation") != "agent tool with agents allowlist":
        add(findings, "VSCODE_DELEGATION", path, "VS Code delegation must map to native agent tool plus allowlist")


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
        "validator": "rhapsodia-agent-validator/v1",
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
