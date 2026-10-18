# Causal Flow Comprehension v0.1.0

A portable Agent Skills package for understanding and questioning the behavior of existing code, systems, and documented processes. No mandatory dependencies; Python 3.10+ is optional for structure and artifact validation.

## Install

Copy/extract the **single** `causal-flow-comprehension/` directory into your compatible Agent Skills discovery location; keep `SKILL.md`, `VERSION`, `CHANGELOG.md` and relative subdirectories together. Consult the current host's installation documentation for its discovery location. Avoid duplicating or modifying the semantic core for each IDE. No symlinks or external orchestrator are required.

## Prompt examples

- "Explain how the account-activation event moves through the repository, including guards, state updates, retries, and alternate writers. Cite exact source locations and mark unknowns."
- "Challenge this sequence diagram against the current source revision. Which arrows are grounded and which are inferred?"
- "Could an unapproved request reach the Active state by any alternative path? State what the available evidence can and cannot prove."
- "Trace the potential behavioral impact of changing this API field without editing any file."

## Validate the package and sample contract

From inside the skill folder (assuming an available Python 3.10+ interpreter):

```text
python -B scripts/validate_skill.py .
python -B scripts/validate_analysis.py examples/sample-analysis.json
python -B -m unittest discover -s tests -p 'test_*.py' -v
```

The validator checks structure, not actual target-repository behavior. Agent activation and behavior across ChatGPT/OpenAI, Codex, Claude, Copilot/VS Code/Visual Studio, and Cursor require separate host trials. `evals/` contains authored cases, not executed results.

For a new immutable ZIP, run `python -B scripts/package_skill.py --output <external-path/causal-flow-comprehension-0.1.0.zip>`. The output must be **outside** the skill folder and must not already exist. The packager writes a SHA-256 receipt beside the ZIP and excludes Python cache files.

## Research and ownership

`research/traceability.json` preserves a bounded research-to-requirement-to-change/evaluation map. It is a creation provenance record, not an exhaustive scientific review or evidence of cognitive-performance improvements. The skill owns verification of *understanding*, not implementation, incident debugging, graph persistence, or diagram rendering.
