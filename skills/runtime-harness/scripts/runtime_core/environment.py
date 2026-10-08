"""Bounded host observations. Discovery is lazy and never executes candidate tools."""
from __future__ import annotations
import os
from pathlib import Path
import platform
import sys
import time
from . import VERSION
from .common import ID_RE, RuntimeFault, confined, file_hash, sha

KNOWN_SKILL_ROOTS = ("skills", ".github/skills", ".agents/skills", ".claude/skills", ".cursor/skills")
DEFAULT_POSITIVE_TTL = 86400
DEFAULT_NEGATIVE_TTL = 600


def interpreter() -> str:
    # Do not resolve symlinks: that would silently leave a virtual environment.
    return os.path.abspath(sys.executable)


def venv_signature() -> dict:
    """Stable across -S behavior changes in Python 3.10..3.14."""
    directory = Path(interpreter()).parent
    result = {}
    for location in (directory / "pyvenv.cfg", directory.parent / "pyvenv.cfg"):
        if location.is_file() and not location.is_symlink() and location.stat().st_size <= 8192:
            result[str(location)] = file_hash(location)
    return result


def scope_id(workspace: Path) -> str:
    """Stable host/workspace identity; mutable PATH/git state must not invalidate the whole registry."""
    return sha({"workspace": str(workspace), "platform": platform.system(), "machine": platform.machine(),
                "host": platform.node(), "python": interpreter(), "venv_config": venv_signature(),
                "version": list(sys.version_info[:3])})


def search_fingerprint() -> str:
    """Identity of the bounded executable search space, persisted only as a hash."""
    return sha({"PATH": os.environ.get("PATH", ""), "PATHEXT": os.environ.get("PATHEXT", "") if os.name == "nt" else ""})


def selected_roots(workspace: Path, supplied: list[Path] | None) -> list[Path]:
    candidates = supplied if supplied else [workspace / p for p in KNOWN_SKILL_ROOTS if (workspace / p).is_dir()]
    roots = []
    for candidate in candidates:
        if candidate.is_symlink() or not candidate.is_dir():
            raise RuntimeFault("INVALID_ROOT", "A selected skill root must be an existing nonsymlink directory.")
        path = candidate.resolve()
        if path not in roots:
            roots.append(path)
    if len(roots) > 16:
        raise RuntimeFault("INVALID_INPUT", "At most sixteen explicit skill roots are supported.")
    return sorted(roots)


def root_stamps(roots: list[Path]) -> list[dict]:
    stamps = []
    for root in roots:
        if not root.is_dir() or root.is_symlink():
            raise RuntimeFault("STALE_CATALOG", "A registered root changed; reinitialize explicitly.", 3)
        st = root.stat()
        stamps.append({"path": str(root), "mtime_ns": st.st_mtime_ns, "ctime_ns": st.st_ctime_ns})
    return stamps


def tool_record(name: str, path: str | None, *, version: str | None = None, verified: bool = False,
                source: str = "explicit", observed_at: float | None = None,
                ttl_seconds: int = DEFAULT_POSITIVE_TTL, search_space: str | None = None) -> dict:
    if not ID_RE.fullmatch(name):
        raise RuntimeFault("INVALID_INPUT", "Tool IDs use lowercase letters, digits and hyphens only.")
    when = time.time() if observed_at is None else observed_at
    common = {"uri": f"tool://{name}", "kind": "tool", "status": "missing" if path is None else "available",
              "verified": bool(verified), "source": source, "observed_at": when, "ttl_seconds": ttl_seconds}
    if search_space is not None:
        common["search_fingerprint"] = search_space
    if path is None:
        return common
    absolute = os.path.abspath(path)
    candidate = Path(absolute)
    if not candidate.is_file():
        raise RuntimeFault("INVALID_INPUT", "Observed tool path must be an existing file.")
    st = candidate.stat()
    common.update({"argv": [absolute],
                   "identity": sha({"path": absolute, "size": st.st_size, "mtime_ns": st.st_mtime_ns,
                                    "ctime_ns": st.st_ctime_ns, "version": version}),
                   "version": version})
    return common


def locate_tool(name: str, roots: list[Path], *, windows: bool) -> str | None:
    """Explicit PATH only; never use implicit current-directory search or execute candidates."""
    if len(roots) > 256:
        raise RuntimeFault("PATH_LIMIT", "At most 256 unique absolute PATH directories are supported.")
    if windows:
        raw = [suffix.strip() for suffix in os.environ.get("PATHEXT", ".COM;.EXE;.BAT;.CMD").split(";") if suffix.strip()]
        suffixes = tuple(dict.fromkeys(s.lower() if s.startswith(".") else "." + s.lower() for s in raw)) + ("",)
    else:
        suffixes = ("",)
    for root in roots:
        if not root.is_absolute() or root.is_symlink() or not root.is_dir():
            continue
        for suffix in suffixes:
            candidate = root / (name + suffix)
            if candidate.is_file() and (windows or os.access(candidate, os.X_OK)):
                return str(candidate)
    return None


def path_roots() -> list[Path]:
    roots = []
    for value in os.environ.get("PATH", "").split(os.pathsep):
        if not value:
            continue
        path = Path(value)
        if path.is_absolute() and path not in roots:
            roots.append(path)
    return roots


def discover_tool(name: str, *, negative_ttl: int = DEFAULT_NEGATIVE_TTL) -> dict:
    """Discover one exact tool ID from the explicit PATH search space; never execute it."""
    if not ID_RE.fullmatch(name):
        raise RuntimeFault("INVALID_INPUT", "Invalid logical tool ID.")
    fingerprint = search_fingerprint()
    candidate = locate_tool(name, path_roots(), windows=os.name == "nt")
    return tool_record(name, candidate, verified=False, source="path", search_space=fingerprint,
                       ttl_seconds=negative_ttl if candidate is None else DEFAULT_POSITIVE_TTL)


def discover_tools() -> dict:
    """Minimal bootstrap: only the already-running Python is known eagerly."""
    return {"python": tool_record("python", interpreter(), version=platform.python_version(), verified=True,
                                  source="runtime", ttl_seconds=DEFAULT_POSITIVE_TTL)}


def discover_skills(roots: list[Path]) -> dict:
    skills, count = {}, 0
    for root in roots:
        for child in sorted(root.iterdir(), key=lambda p: p.name):
            count += 1
            if count > 4096:
                raise RuntimeFault("CATALOG_TOO_LARGE", "The bounded skill-root entry limit was exceeded.")
            if not child.is_dir() or child.is_symlink() or not ID_RE.fullmatch(child.name):
                continue
            entry = confined(root, child.name + "/SKILL.md")
            if not entry.is_file():
                continue
            if child.name in skills:
                raise RuntimeFault("DUPLICATE_ID", "A skill ID exists in multiple selected roots; select an unambiguous root set.", 4)
            skills[child.name] = {"root": str(child), "entrypoint_sha256": file_hash(entry)}
    return skills


def agent_stamps(workspace: Path) -> list[dict]:
    result = []
    for rel in ("agents", ".github/agents"):
        root = confined(workspace, rel)
        if root.is_dir():
            st = root.stat()
            result.append({"path": rel, "mtime_ns": st.st_mtime_ns, "ctime_ns": st.st_ctime_ns})
        else:
            result.append({"path": rel, "missing": True})
    return result


def discover_agents(workspace: Path) -> dict:
    agents = {}
    for rel in ("agents", ".github/agents"):
        root = confined(workspace, rel)
        if not root.is_dir():
            continue
        entries = list(root.glob("*.agent.md"))
        if len(entries) > 256:
            raise RuntimeFault("CATALOG_TOO_LARGE", "Too many agent profiles in a selected root.")
        for p in sorted(entries):
            name = p.name[:-len(".agent.md")]
            if not ID_RE.fullmatch(name):
                continue
            path = confined(workspace, p.relative_to(workspace).as_posix())
            if name in agents:
                raise RuntimeFault("DUPLICATE_ID", "An agent ID has multiple local definitions.", 4)
            agents[name] = {"relative_path": path.relative_to(workspace).as_posix(), "sha256": file_hash(path)}
    return agents


def discover(workspace: Path, roots: list[Path], max_age: int) -> dict:
    now = time.time()
    return {"schema": "runtime-snapshot-v1", "runtime_version": VERSION, "created_at": now, "updated_at": now,
            "scope": scope_id(workspace), "workspace": str(workspace), "max_age_seconds": max_age,
            "skill_roots": [str(p) for p in roots], "root_stamps": root_stamps(roots),
            "agent_stamps": agent_stamps(workspace), "skills": discover_skills(roots), "agents": discover_agents(workspace),
            "tools": discover_tools(), "resources": {}}
