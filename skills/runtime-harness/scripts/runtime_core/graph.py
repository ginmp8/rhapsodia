"""Optional derived GraphPatch; no graph database, service, or peer imports."""
from __future__ import annotations
from .store import Store


def export_graph(store: Store) -> dict:
    snapshot_id, snapshot = store.current()
    source_uri = "runtime-environment:" + snapshot["scope"]
    scope = "runtime:" + snapshot["scope"][:24]
    root_id = scope + ":environment"
    def evidence(locator):
        return [{"provenance": "EXTRACTED", "confidence": 1.0, "status": "accepted",
                 "locator": "runtime-snapshot:" + snapshot_id + "#/" + locator, "details": {"meaning": "Observed registry membership, not execution authority or runtime proof."}}]
    nodes = [{"id": root_id, "kind": "Environment", "label": "Local environment snapshot",
              "properties": {"snapshot_id": snapshot_id}, "evidence": evidence("scope")}]
    edges = []
    for kind, catalog in (("Tool", snapshot["tools"]), ("Skill", snapshot["skills"]), ("Agent", snapshot["agents"]), ("Resource", snapshot["resources"])):
        for name, record in sorted(catalog.items()):
            node_id = scope + ":" + kind.lower() + ":" + name
            locator = kind.lower() + "s/" + name
            props = {"uri": kind.lower() + "://" + name}
            if kind == "Tool":
                props["observed_status"] = record["status"]
            elif kind == "Resource":
                props["observed_status"] = "available"
            nodes.append({"id": node_id, "kind": kind, "label": name, "properties": props, "evidence": evidence(locator)})
            edges.append({"source": root_id, "target": node_id, "relation": "records", "directed": True, "evidence": evidence(locator)})
    return {"schema_version": "graph-patch-v1", "source": {"uri": source_uri, "kind": "runtime-snapshot", "content_hash": snapshot_id,
            "metadata": {"projection": "observed-membership-only", "absolute_paths_included": False}}, "nodes": nodes, "edges": edges}
