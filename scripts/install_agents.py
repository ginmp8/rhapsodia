#!/usr/bin/env python3
import argparse
import hashlib
import shutil
import sys
from pathlib import Path

AGENT_FILES = (
    "rhapsodia-supervisor.agent.md",
    "nomia.agent.md",
    "mago.agent.md",
    "magia.agent.md",
)
REQUIRED_SKILLS = ("nomia", "mago", "magia")
SKILL_ROOTS = (Path(".github/skills"), Path(".claude/skills"), Path(".agents/skills"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_root() -> Path:
    return Path(__file__).resolve().parents[1]


def find_skill(target: Path, name: str):
    matches = []
    for root in SKILL_ROOTS:
        skill = target / root / name / "SKILL.md"
        if skill.is_file():
            matches.append(skill)
    return matches


def preflight(target: Path):
    errors = []
    if not target.is_dir():
        errors.append(f"target repository does not exist or is not a directory: {target}")
        return errors
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
            errors.append(
                f"required skill '{skill}' is installed in multiple discovery roots: "
                + ", ".join(str(p.relative_to(target)) for p in matches)
            )
    return errors


def check_installation(target: Path):
    errors = preflight(target)
    source = package_root() / "agents"
    dest = target / ".github" / "agents"
    if not dest.is_dir():
        errors.append(f"agent installation directory is missing: {dest}")
        return errors
    actual = {p.name for p in dest.glob("*.agent.md")}
    for name in AGENT_FILES:
        src = source / name
        dst = dest / name
        if name not in actual or not dst.is_file():
            errors.append(f"installed agent is missing: .github/agents/{name}")
            continue
        if sha256(src) != sha256(dst):
            errors.append(f"installed agent differs from package source: .github/agents/{name}")
    return errors


def install(target: Path, *, dry_run: bool, force: bool):
    errors = preflight(target)
    if errors:
        return errors, []

    source = package_root() / "agents"
    dest = target / ".github" / "agents"
    plan = []
    for name in AGENT_FILES:
        src = source / name
        dst = dest / name
        if dst.exists():
            if not dst.is_file():
                errors.append(f"installation path is not a file: {dst}")
                continue
            if sha256(src) == sha256(dst):
                plan.append(("unchanged", src, dst))
                continue
            if not force:
                errors.append(f"existing agent differs; rerun with --force to replace: {dst}")
                continue
            plan.append(("replace", src, dst))
        else:
            plan.append(("copy", src, dst))

    if errors:
        return errors, plan

    if not dry_run:
        dest.mkdir(parents=True, exist_ok=True)
        for action, src, dst in plan:
            if action in {"copy", "replace"}:
                shutil.copy2(src, dst)
    return [], plan


def main():
    ap = argparse.ArgumentParser(
        description="Install or verify the Rhapsodia VS Code custom-agent profiles. Skills are prerequisites and are not copied."
    )
    ap.add_argument("--target", required=True, help="Target repository root")
    ap.add_argument("--check", action="store_true", help="Verify installed agent bytes and required skills without mutation")
    ap.add_argument("--dry-run", action="store_true", help="Show the installation plan without mutation")
    ap.add_argument("--force", action="store_true", help="Replace differing existing agent profiles")
    args = ap.parse_args()

    target = Path(args.target).resolve()
    if args.check:
        errors = check_installation(target)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print("PASS: four agent profiles match the package source and nomia/mago/magia skills are discoverable.")
        return 0

    errors, plan = install(target, dry_run=args.dry_run, force=args.force)
    for action, _src, dst in plan:
        label = "WOULD" if args.dry_run else "DONE"
        print(f"{label}: {action}: {dst}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.dry_run:
        print("PASS: dry-run only; target was not modified.")
    else:
        print("PASS: agent profiles installed to .github/agents/. Skills were verified but not copied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
