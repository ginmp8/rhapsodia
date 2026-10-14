# Premortem Analysis — v0.1.0

A portable Agent Skills package for **future-failure thought experiments** on consequential plans. It identifies credible ways an upcoming project or decision could fail, challenges explanations, and proposes measurable preventive changes. It never claims to predict outcomes or assume authorization to implement changes.

## Use

Ask: "Run a governed premortem on this service migration plan before release. Identify plausible failure chains, counterevidence, mitigations, validation gates, and changes we should consider."

Select `quick` for lightweight plans, `standard` normally, or `governed` for security/privacy/safety/compliance/irreversibility. Outputs are readable Markdown by default; a typed JSON contract exists when machine-to-machine handoff matters.

## Install / distribute

Copy the root `premortem-analysis/` folder (including `SKILL.md`) to the appropriate Agent Skills discovery location configured by your host. Do not duplicate or modify the canonical core for different IDEs. Review the supported discovery mechanism in your client; a ZIP is not evidence that a host installed or executed it.

## Optional offline validation

Python 3.10+ standard library only:

```sh
python3 scripts/validate_package.py .
python3 scripts/validate_traceability.py evidence/traceability.json
python3 scripts/validate_report.py examples/messaging-migration.json
python3 -m unittest discover -s tests -v
```

To package deterministically (after validation), run `python3 scripts/package.py --root . --out ../premortem-analysis-v0.1.0.zip`. This only packages; it does not install the skill. `evidence/traceability.json` documents exactly how the research corpus influenced the skill; `evals/` scenarios are planned coverage, not executed LLM trials.

See [SKILL.md](SKILL.md) for authoritative behavior and reference loading.
