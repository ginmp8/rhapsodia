"""Small command surface; stdout is one bounded JSON result (except stdio MCP)."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
from .common import MAX_INPUT, RuntimeFault, canonical, read_bytes, strict_json
from .store import Store


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeFault("INVALID_INPUT", message)


def parser() -> argparse.ArgumentParser:
    p = Parser(description="Local runtime observations, exact resource lookups and content-bound handoffs.")
    p.add_argument("--workspace", type=Path, default=Path.cwd())
    commands = p.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--skills-root", type=Path, action="append")
    init.add_argument("--refresh", action="store_true")
    init.add_argument("--max-age-seconds", type=int)
    query = commands.add_parser("query")
    query.add_argument("--input", type=Path, help="Request file; default is bounded JSON on stdin")
    for command in ("resolve", "context"):
        sub = commands.add_parser(command)
        sub.add_argument("refs", nargs="+")
        sub.add_argument("--budget-bytes", type=int, default=8192)
    ensure = commands.add_parser("ensure")
    ensure.add_argument("refs", nargs="+")
    ensure.add_argument("--negative-ttl-seconds", type=int, default=600)
    ensure.add_argument("--budget-bytes", type=int, default=8192)
    observe_tool = commands.add_parser("observe-tool")
    observe_tool.add_argument("ref")
    observe_tool.add_argument("--path", type=Path, required=True)
    observe_tool.add_argument("--ttl-seconds", type=int, default=86400)
    observe_resource = commands.add_parser("observe-resource")
    observe_resource.add_argument("ref")
    observe_resource.add_argument("--path", type=Path, required=True)
    observe_resource.add_argument("--ttl-seconds", type=int, default=86400)
    for name in ("publish-capability", "observe-attempt", "discovery-history", "handoff-delta", "handoff-apply"):
        commands.add_parser(name).add_argument("--input", type=Path)
    commands.add_parser("status")
    create = commands.add_parser("handoff-create")
    create.add_argument("--input", type=Path)
    resume = commands.add_parser("handoff-resume")
    choice = resume.add_mutually_exclusive_group(required=True)
    choice.add_argument("--id")
    choice.add_argument("--input", type=Path)
    resume.add_argument("--rebind", action="store_true")
    commands.add_parser("export-graph")
    config = commands.add_parser("configure")
    config.add_argument("--host", required=True, choices=("generic", "codex", "copilot", "claude", "cursor"))
    bench = commands.add_parser("benchmark")
    bench.add_argument("--iterations", type=int, default=10)
    commands.add_parser("mcp")
    commands.add_parser("mcp-config")
    session = commands.add_parser("session-start")
    session.add_argument("--skills-root", type=Path, action="append")
    session.add_argument("--format", choices=("generic", "vscode-local"), default="generic")
    return p


def request(path: Path | None) -> dict:
    data = read_bytes(path, MAX_INPUT) if path is not None else sys.stdin.buffer.read(MAX_INPUT + 1)
    return strict_json(data)


def dispatch(store: Store, args) -> dict:
    if args.command in {"session-start", "mcp-config"}:
        from .session import session_start, mcp_config
        return session_start(store, args.skills_root, args.format) if args.command == "session-start" else mcp_config(store)
    if args.command in {"publish-capability", "observe-attempt", "discovery-history"}:
        from .capabilities import publish, attempt, history
        return {"publish-capability": publish, "observe-attempt": attempt, "discovery-history": history}[args.command](store, request(args.input))
    if args.command in {"handoff-delta", "handoff-apply"}:
        from .delta import make, apply
        return (make if args.command == "handoff-delta" else apply)(store, request(args.input))
    if args.command == "init":
        return store.initialize(args.skills_root, refresh=args.refresh, max_age=args.max_age_seconds)
    if args.command in {"query", "status", "resolve", "context"}:
        from .query import execute_query
        if args.command == "query":
            body = request(args.input)
        elif args.command == "status":
            body = {"operation": "status"}
        else:
            body = {"operation": args.command, "refs": args.refs, "budget_bytes": args.budget_bytes}
        return execute_query(store, body)
    if args.command == "ensure":
        from .observations import ensure
        return ensure(store, args.refs, negative_ttl=args.negative_ttl_seconds, budget=args.budget_bytes)
    if args.command == "observe-tool":
        from .observations import observe_tool
        return observe_tool(store, args.ref, args.path, ttl=args.ttl_seconds)
    if args.command == "observe-resource":
        from .observations import observe_resource
        return observe_resource(store, args.ref, args.path, ttl=args.ttl_seconds)
    if args.command == "handoff-create":
        from .handoff import create
        return create(store, request(args.input))
    if args.command == "handoff-resume":
        from .handoff import resume
        return resume(store, key=args.id, external=args.input, rebind=args.rebind)
    if args.command == "export-graph":
        from .graph import export_graph
        return export_graph(store)
    if args.command == "configure":
        from .integration import configure
        return configure(store, args.host)
    if args.command == "benchmark":
        from .benchmark import measure
        return measure(store, args.iterations)
    raise RuntimeFault("INVALID_INPUT", "Unknown operation.")


def main(argv=None) -> int:
    try:
        args = parser().parse_args(argv)
        store = Store(args.workspace)
        if args.command == "mcp":
            from .mcp import serve
            return serve(store, sys.stdin.buffer, sys.stdout.buffer)
        result = dispatch(store, args)
        sys.stdout.buffer.write(canonical(result))
        return 0
    except RuntimeFault as exc:
        sys.stdout.buffer.write(canonical(exc.result()))
        return exc.exit_code
    except (OSError, UnicodeError):
        fault = RuntimeFault("IO_ERROR", "The selected local resource could not be accessed. Check permissions and paths; no retry or installation was attempted.", 3)
        sys.stdout.buffer.write(canonical(fault.result()))
        return fault.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
