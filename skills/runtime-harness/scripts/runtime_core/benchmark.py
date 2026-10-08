"""Reproducible local mechanics measurement; not an LLM/IDE benchmark."""
from __future__ import annotations
from pathlib import Path
import statistics
import time
from .common import canonical, number
from .query import execute_query
from .store import Store


def measure(store: Store, iterations: int) -> dict:
    number(iterations, 1, 100)
    _, snapshot = store.current()
    roots = [Path(p) for p in snapshot["skill_roots"]]
    cold, warm, queries = [], [], []
    refs = ["tool://python"]
    if snapshot["skills"]:
        refs.append("skill://" + sorted(snapshot["skills"])[0])
    for _ in range(iterations):
        start = time.perf_counter_ns()
        store.initialize(roots, refresh=True, max_age=snapshot["max_age_seconds"])
        cold.append((time.perf_counter_ns() - start) / 1e6)
        start = time.perf_counter_ns()
        result = store.initialize(roots, max_age=snapshot["max_age_seconds"])
        if not result["cache_hit"]:
            raise RuntimeError("Warm-path measurement unexpectedly performed discovery")
        warm.append((time.perf_counter_ns() - start) / 1e6)
        start = time.perf_counter_ns()
        context = execute_query(store, {"operation": "context", "refs": refs})
        queries.append((time.perf_counter_ns() - start) / 1e6)
    def metrics(values):
        return {"median": round(statistics.median(values), 6), "min": round(min(values), 6), "max": round(max(values), 6)}
    return {"scope": "local-mechanics-not-agent-benchmark", "iterations": iterations,
            "cold_init_ms": metrics(cold), "warm_init_ms": metrics(warm), "query_ms": metrics(queries),
            "snapshot_bytes": len(canonical(snapshot)), "context_bytes": len(canonical(context)),
            "billed_tokens": None, "selected_refs": refs,
            "limitations": "Same process, in-memory OS cache, selected-record projection; excludes process/IDE/model startup and transport duplication. Byte reduction is not lossless compression or measured token savings."}
