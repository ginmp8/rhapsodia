# Validation and evidence layers

Run from this skill directory with an available Python 3.10+:

```text
<PYTHON> -I -S -B -m unittest discover -s tests -p "test_*.py" -v
<PYTHON> -I -S -B scripts/validate_package.py
```

The first command exercises actual file hashing, stale/corrupt inputs, action eligibility,
cache hits/misses, live receipt/output validation, metrics, authority-preserving policy,
quarantine, lease compare-and-set, standalone CLI and payload boundaries. The second checks
portable shape, direct local references, Top-100 controls, JSON contracts, syntax and package
hygiene. Neither command invokes a model, contacts a service or proves actual host routing.

The release also executes Skill Creator Juiced structural/portability gates externally and
records their exact outcomes. Seed properties were defined before new implementation and
preserved. Added regression cases diagnose general failures, not exact task filenames.

Layers are separate: structural format/links; deterministic behavior; local Python/CLI
runtime; manual semantic/routing review; native-host/model behavior. Activation scenarios
are planned prompts until an actual model/host evaluates them. No held-out routing accuracy
or independent-review score is fabricated from their presence.

For an efficiency experiment use the same scenario inputs, model, host, configuration,
evaluator, quality bar and cache state across balanced repeated baseline/candidate runs.
Record actual provider usage or null. Test cold/warm states, changed inputs, wrong scopes,
expired evidence, denied/transient failures and required fresh/independent gates. A byte
benchmark is useful local evidence, but not a proxy for paid tokens or total agent duration.

Freeze passing source bytes; package only after required checks pass. Rerun affected checks
following any edit. Keep source archives/evaluators immutable and record residual unavailable
platform/model checks explicitly. Never weaken a fixture or acceptance rule to obtain green.
