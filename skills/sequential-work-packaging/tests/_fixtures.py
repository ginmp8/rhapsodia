from __future__ import annotations

from pathlib import Path


def write_spec(root: Path, sid: str = "spec001", feature_key: str = "alpha", feature_version: str = "v0.1.0", order: int = 10, tasks: str | None = None) -> None:
    spec = root / "specs" / sid
    spec.mkdir(parents=True, exist_ok=True)
    (spec / "manifest.yaml").write_text(
        f'''schema_version: 1
spec_id: {sid}
feature_key: {feature_key}
title: Alpha
type: feature
classification: feature
status: planned
phase: define
cycle_version: "01.00.00"
feature_version: {feature_version}
source_of_truth:
  prd: prd.md
  tasks: tasks.md
  validation: validation.md
  notes: notes.md
traceability: {{}}
''', encoding="utf-8")
    (spec / "prd.md").write_text("# context\n\n# acceptance criteria\n\n- testable\n", encoding="utf-8")
    if tasks is None:
        tasks = '''- [ ] Task 1: First
  - Task ID: task001
  - Objective: first
  - Affected boundary: core
  - Task type: implementation
  - Reasoning: low
  - Why this reasoning is sufficient: bounded
  - Specialist Support: none
  - Dependencies: none
  - Validation: test
  - Expected result: done

- [ ] Task 2: Second
  - Task ID: task002
  - Objective: second
  - Affected boundary: core
  - Task type: validation
  - Reasoning: low
  - Why this reasoning is sufficient: bounded
  - Specialist Support: none
  - Dependencies: task001
  - Validation: test
  - Expected result: done
'''
    (spec / "tasks.md").write_text(tasks, encoding="utf-8")
    (spec / "notes.md").write_text("# assumptions\n\nnone\n", encoding="utf-8")
    (spec / "validation.md").write_text("# validation strategy\n\nrun tests\n", encoding="utf-8")


def make_cycle(base: Path, specs: list[dict] | None = None, create_specs: bool = True) -> Path:
    root = base / "01.00.00"
    root.mkdir(parents=True)
    specs = specs or [{
        "order": 10, "spec_id": "spec001", "feature_key": "alpha", "title": "Alpha",
        "type": "feature", "classification": "feature", "depends_on_features": [],
        "depends_on_specs": [], "status": "planned", "feature_version": "v0.1.0"
    }]
    lines = ['schema_version: 1', 'cycle_version: "01.00.00"', 'cycle_status: active', 'specs:']
    for s in specs:
        lines.append(f"  - order: {s['order']}")
        for key in ["spec_id", "feature_key", "title", "type", "classification"]:
            lines.append(f"    {key}: {s[key]}")
        for key in ["depends_on_features", "depends_on_specs"]:
            vals = s.get(key, [])
            if not vals:
                lines.append(f"    {key}: []")
            else:
                lines.append(f"    {key}:")
                lines.extend(f"      - {v}" for v in vals)
        lines.append(f"    status: {s['status']}")
        lines.append(f"    feature_version: {s['feature_version']}")
    (root / "spec-catalog.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if create_specs:
        for s in specs:
            write_spec(root, s["spec_id"], s["feature_key"], s["feature_version"], s["order"])
    return root
