#!/usr/bin/env python3
import argparse, json, sys

TIE_BREAKS = [
    ("temporal", "sequence"),
    ("branching_retry", "flowchart"),
    ("state_lifecycle", "state"),
    ("data_relationship", "er"),
    ("component_dependency", "architecture"),
    ("historical_sequence", "timeline"),
    ("file_responsibilities", "change-map"),
]
VALID_MODES = {"change-review", "system-explanation", "code-archaeology", "visual-scratchpad"}
VALID_VISUALS = {"sequence", "flowchart", "state", "er", "architecture", "timeline", "change-map", "none"}


def choose(mode, signals):
    if mode not in VALID_MODES:
        raise ValueError(f"invalid mode: {mode}")
    explicit = signals.get("explicit_visual")
    if explicit is not None:
        if explicit not in VALID_VISUALS:
            raise ValueError(f"invalid explicit_visual: {explicit}")
        return [{"role": "primary", "type": explicit}]

    selected = []
    if mode == "change-review" and signals.get("file_responsibilities"):
        selected.append({"role": "primary", "type": "change-map"})
    elif mode == "code-archaeology" and signals.get("historical_sequence"):
        selected.append({"role": "primary", "type": "timeline"})

    for key, visual in TIE_BREAKS:
        if not signals.get(key):
            continue
        if any(x["type"] == visual for x in selected):
            continue
        role = "primary" if not selected else "secondary"
        selected.append({"role": role, "type": visual})
        break

    if not selected:
        if mode == "system-explanation":
            selected = [{"role": "primary", "type": "architecture"}]
        else:
            selected = [{"role": "primary", "type": "none"}]
    return selected[:2]


def main():
    p = argparse.ArgumentParser(description="Deterministically select visual type(s) from normalized signals.")
    p.add_argument("--mode", required=True, choices=sorted(VALID_MODES))
    p.add_argument("--input", required=True, help="JSON file containing the signals object")
    p.add_argument("--output", help="Optional output JSON path; stdout otherwise")
    args = p.parse_args()
    with open(args.input, "r", encoding="utf-8") as f:
        signals = json.load(f)
    result = {"mode": args.mode, "visuals": choose(args.mode, signals)}
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as f:
            f.write(rendered)
    else:
        sys.stdout.write(rendered)

if __name__ == "__main__":
    main()
