#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path


def dependency_mentions(project_root: Path) -> list[dict[str, str]]:
    candidates = [
        project_root / "pyproject.toml",
        project_root / "requirements.txt",
        project_root / "requirements-dev.txt",
        project_root / "uv.lock",
        project_root / "poetry.lock",
        project_root / "pdm.lock",
    ]
    rows: list[dict[str, str]] = []
    patterns = [
        re.compile(r"(?i)(?:^|[\"'\s])streamlit\s*(?:[<>=!~^].*)?$"),
        re.compile(r"(?i)name\s*=\s*[\"']streamlit[\"']"),
    ]
    for path in candidates:
        if not path.is_file():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            stripped = line.strip()
            if "streamlit" not in stripped.lower():
                continue
            if any(p.search(stripped) for p in patterns) or path.name.endswith(".lock"):
                rows.append({"file": path.name, "line": str(line_no), "text": stripped[:500]})
    return rows


def installed_context() -> dict[str, object]:
    result: dict[str, object] = {
        "installed": False,
        "version": None,
        "module_file": None,
        "bundled_agent_skill": None,
        "bundled_agent_skill_exists": False,
    }
    spec = importlib.util.find_spec("streamlit")
    if spec is None:
        return result
    try:
        import streamlit  # type: ignore
    except Exception as exc:
        result["import_error"] = f"{type(exc).__name__}: {exc}"
        return result
    module_file = Path(streamlit.__file__).resolve()
    package_root = module_file.parent
    bundled = package_root / ".agents" / "skills" / "developing-with-streamlit" / "SKILL.md"
    result.update(
        installed=True,
        version=getattr(streamlit, "__version__", None),
        module_file=str(module_file),
        bundled_agent_skill=str(bundled),
        bundled_agent_skill_exists=bundled.is_file(),
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve version/source context for a Streamlit project.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--json", dest="json_path")
    parser.add_argument("--require-streamlit", action="store_true")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    data = {
        "resolver_version": 1,
        "python": {"executable": sys.executable, "version": sys.version.split()[0]},
        "project_root": str(project_root),
        "dependency_mentions": dependency_mentions(project_root),
        "streamlit": installed_context(),
        "cli": {
            "streamlit": shutil.which("streamlit"),
            "exact_api_lookup": "streamlit docs st.<command>",
        },
        "claim_boundary": "Environment evidence only. Verify production/CI uses the same dependency/runtime identity before making deployment compatibility claims.",
    }
    status = "pass"
    if args.require_streamlit and not data["streamlit"]["installed"]:
        status = "fail"
    data["status"] = status

    rendered = json.dumps(data, indent=2, sort_keys=True)
    if args.json_path:
        out = Path(args.json_path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_name(out.name + ".tmp")
        tmp.write_text(rendered + "\n", encoding="utf-8")
        tmp.replace(out)
    print(rendered)
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
