#!/usr/bin/env python3
"""Install RhapsodIA VS Code agent profiles and the portable capability-discovery Skill.

Canonical domain/Runtime Harness/Local Graph Skills remain preinstalled prerequisites.
Only the self-contained discovery Skill is copied by default; --agents-only opts out.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import tempfile
from pathlib import Path

AGENT_FILES = (
    "rhapsodia-adhoc.agent.md", "rhapsodia-supervisor.agent.md",
    "rhapsodia-analyst.agent.md", "rhapsodia-verifier.agent.md",
    "nomia.agent.md", "mago.agent.md", "magia.agent.md",
    "rhapsodia-workspace.agent.md",
)
REQUIRED_SKILLS = ("nomia", "mago", "magia", "test-oracle-engineering", "runtime-harness", "local-graph-engine")
REQUIRED_HELPERS = {"runtime-harness": "scripts/agent_session.py", "local-graph-engine": "scripts/workspace_memory.py"}
SKILL_ROOTS = (Path(".github/skills"), Path(".claude/skills"), Path(".agents/skills"), Path(".cursor/skills"), Path("skills"))
DISCOVERY_SKILL = "capability-discovery"
DISCOVERY_REQUIRED_FILES = ("SKILL.md", "VERSION", "scripts/capability_directory.py", "references/routing.md")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_root() -> Path:
    return Path(__file__).resolve().parents[1]


def find_skill(target: Path, name: str) -> list[Path]:
    return [target / root / name / "SKILL.md" for root in SKILL_ROOTS
            if (target / root / name / "SKILL.md").is_file()]


def unsafe_ancestors(path: Path, anchor: Path) -> bool:
    current = path
    while True:
        if current.is_symlink():
            return True
        if current == anchor:
            return False
        if current == current.parent:
            return True
        current = current.parent


def discovery_source_files() -> list[tuple[Path, Path]]:
    source = package_root() / "skills" / DISCOVERY_SKILL
    files = []
    if not source.is_dir() or source.is_symlink():
        raise ValueError("source capability-discovery Skill is missing or linked")
    for f in source.rglob("*"):
        if f.is_symlink():
            raise ValueError(f"source discovery Skill contains symlink: {f}")
        if f.is_file() and not ({"__pycache__", ".pytest_cache"} & set(f.parts)) and f.suffix != ".pyc":
            files.append((f, f.relative_to(source)))
    if not all((source / rel).is_file() for rel in DISCOVERY_REQUIRED_FILES):
        raise ValueError("source discovery Skill lacks required entrypoint/command")
    return sorted(files, key=lambda item: item[1].as_posix())


def preflight(target: Path, *, agents_only: bool = False) -> list[str]:
    errors = []
    if not target.is_dir():
        return [f"target repository does not exist or is not a directory: {target}"]
    source = package_root() / "agents"
    for name in AGENT_FILES:
        if not (source / name).is_file():
            errors.append(f"source agent is missing: agents/{name}")
    for skill in REQUIRED_SKILLS:
        matches = find_skill(target, skill)
        if not matches:
            roots = ", ".join(str(r / skill / "SKILL.md") for r in SKILL_ROOTS)
            errors.append(f"required skill '{skill}' not found; expected one of: {roots}")
        elif len(matches) > 1:
            errors.append("required skill '%s' is installed in multiple discovery roots: %s" %
                          (skill, ", ".join(str(p.relative_to(target)) for p in matches)))
        elif skill in REQUIRED_HELPERS:
            helper = matches[0].parent / REQUIRED_HELPERS[skill]
            if not helper.is_file() or helper.is_symlink():
                errors.append(f"required session helper is missing or linked: {helper.relative_to(target)}; install the matching skill release")
    if not agents_only:
        try:
            discovery_source_files()
        except ValueError as exc:
            errors.append(str(exc))
        matches = find_skill(target, DISCOVERY_SKILL)
        if len(matches) > 1:
            errors.append("capability-discovery is installed in multiple roots; resolve ambiguity before installation")
        elif len(matches) == 1 and unsafe_ancestors(matches[0].parent, target):
            errors.append("capability-discovery installation root includes a symlink")
        elif len(matches) == 1 and matches[0].parent != target / ".github/skills" / DISCOVERY_SKILL:
            for rel in DISCOVERY_REQUIRED_FILES:
                path = matches[0].parent / rel
                if not path.is_file() or path.is_symlink():
                    errors.append(f"external installed discovery Skill is incomplete or linked: {path.relative_to(target)}")
    return errors


def check_installation(target: Path, *, agents_only: bool = False) -> list[str]:
    errors = preflight(target, agents_only=agents_only)
    source = package_root() / "agents"
    dest = target / ".github" / "agents"
    if not dest.is_dir() or unsafe_ancestors(dest, target):
        errors.append(f"agent installation directory is missing or linked: {dest}")
        return errors
    for name in AGENT_FILES:
        src, dst = source / name, dest / name
        if not dst.is_file() or dst.is_symlink():
            errors.append(f"installed agent is missing or linked: .github/agents/{name}")
        elif sha256(src) != sha256(dst):
            errors.append(f"installed agent differs from package source: .github/agents/{name}")
    if not agents_only:
        matches = find_skill(target, DISCOVERY_SKILL)
        if not matches:
            errors.append("capability-discovery Skill missing; run installer or pass --agents-only to use native discovery only")
        elif len(matches) == 1:
            if matches[0].parent == target / ".github/skills" / DISCOVERY_SKILL:
                for src, rel in discovery_source_files():
                    dst = matches[0].parent / rel
                    if not dst.is_file() or dst.is_symlink() or sha256(src) != sha256(dst):
                        errors.append(f"installed discovery Skill missing or differs: {dst.relative_to(target)}")
            else:
                for rel in DISCOVERY_REQUIRED_FILES:
                    dst = matches[0].parent / rel
                    if not dst.is_file() or dst.is_symlink():
                        errors.append(f"external installed discovery Skill incomplete: {dst.relative_to(target)}")
    return errors


def plan_file(src: Path, dst: Path, target: Path, force: bool, errors: list[str], plan: list):
    if unsafe_ancestors(dst.parent, target) or dst.is_symlink():
        errors.append(f"installation destination includes symlink: {dst}")
        return
    if dst.exists():
        if not dst.is_file():
            errors.append(f"installation path is not a file: {dst}")
        elif sha256(src) == sha256(dst):
            plan.append(("unchanged", src, dst))
        elif not force:
            errors.append(f"existing file differs; rerun with --force to replace: {dst}")
        else:
            plan.append(("replace", src, dst))
    else:
        plan.append(("copy", src, dst))


def install(target: Path, *, dry_run: bool, force: bool, agents_only: bool = False):
    errors = preflight(target, agents_only=agents_only)
    if errors:
        return errors, []
    source = package_root() / "agents"
    dest = target / ".github" / "agents"
    plan: list[tuple[str, Path, Path]] = []
    for name in AGENT_FILES:
        plan_file(source / name, dest / name, target, force, errors, plan)
    if not agents_only:
        matches = find_skill(target, DISCOVERY_SKILL)
        expected = target / ".github" / "skills" / DISCOVERY_SKILL
        # If already installed in another supported root, preserve it and avoid a duplicate.
        if not matches or matches[0].parent == expected:
            for src, relative in discovery_source_files():
                plan_file(src, expected / relative, target, force, errors, plan)
    if errors:
        return errors, plan
    if not dry_run:
        for action, src, dst in plan:
            if action not in {"copy", "replace"}:
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary = tempfile.mkstemp(prefix=".rhapsodia-install-", dir=dst.parent)
            temporary = Path(temporary)
            try:
                with os.fdopen(descriptor, "wb") as writer:
                    writer.write(src.read_bytes())
                os.replace(temporary, dst)
            finally:
                temporary.unlink(missing_ok=True)
    return [], plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="Target repository root")
    parser.add_argument("--check", action="store_true", help="Verify installed profiles and discovery Skill without mutation")
    parser.add_argument("--dry-run", action="store_true", help="Show install plan without mutation")
    parser.add_argument("--force", action="store_true", help="Replace differing installed profiles and discovery files")
    parser.add_argument("--agents-only", action="store_true", help="Skip optional discovery Skill copy/check (native fallback remains)")
    args = parser.parse_args()
    target = Path(args.target).resolve()
    if args.check:
        errors = check_installation(target, agents_only=args.agents_only)
        if errors:
            for issue in errors:
                print("ERROR:", issue, file=sys.stderr)
            return 1
        print(f"PASS: {len(AGENT_FILES)} agent profiles match package; required domain/session Skills present; "
              + ("native capability discovery only." if args.agents_only else "portable capability-discovery Skill present."))
        return 0
    errors, plan = install(target, dry_run=args.dry_run, force=args.force, agents_only=args.agents_only)
    for action, _src, dst in plan:
        print(f"{'WOULD' if args.dry_run else 'DONE'}: {action}: {dst}")
    if errors:
        for issue in errors:
            print("ERROR:", issue, file=sys.stderr)
        return 1
    print("PASS: dry-run only; target was not modified." if args.dry_run
          else f"PASS: {len(AGENT_FILES)} agent profiles installed; "
               + ("discovery Skill intentionally omitted." if args.agents_only else "capability-discovery Skill installed or reused."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
