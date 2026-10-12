# Reconstruct — independent source-to-behavior implementation

**Purpose:** implement an observable compatible replacement without copying target internals or confusing reconstructed source with functionally tested behavior.
**Load when:** writing a new port, reimplementation or bug-compatible replacement from source/binary/black-box evidence.
**Decision impact:** freezes correct acceptance obligations, prevents silent behavior fixes and makes implementation depend on finite trusted oracles rather than static guesswork.

1. Identify the rights/permission to analyze and reimplement, freeze exact source identities and previously observed corpus before candidate changes. Keep third-party notices for code actually reused.
2. Write a behavior contract: public operations, input/output schemas, error classes/messages, serialization (including missing/undefined, numeric precision, binary and date), deterministic ordering, state transitions, retries/idempotency, concurrency, cancellation, clock/locale, side effects, environment, resource limits and unknown paths.
3. Separate **legacy observed** quirks from **desired changed** behavior. For strict cloning, do not silently repair a bug. Declared and lexical evidence are not the same as runtime observation.
4. Use `evidence_ir.py` to correlate source or compiler reports; optionally use an authorized installed ILSpy/JADX/Ghidra/Kaitai analyzer or the trusted .NET 10 Roslyn source helper. Treat decompiled source as approximation; reflection, proxy/DI/virtual dispatch and runtime binding require independent tests.
5. Generate unobserved boundary, stateful and randomized stimuli with `probe_engine.py`; prioritize gaps from existing differential results or externally recorded coverage identifiers. Query the explicitly authorized reference to create real expected behavior. Use `state_inference.py` for observed transitions and missing actions, not arbitrary inferred state equivalence.
6. Implement compatible code independently and incrementally in the chosen target language. For cross-language ports explicitly test truthiness, missing/null, number handling, Unicode, date timezone, exception identity, lazy loading and collection ordering; do not assume language syntax preserves semantics.
7. Compare frozen reference/candidate NDJSON with `behavior_lab.py`. Where authorized, use `behavioral_pipeline.py` (trusted only) and reduced counterexamples; record side effect instrumentation scope, test partitions and unresolved fields. Never mutate goldens or captured reference outputs to force a PASS.
8. Deliver implementation path/code revision, behavior delta, test execution receipts, hashes, environment assumptions, compatible interfaces and explicit uncertainty. If reference runtime cannot be safely executed, label the behavior unverified rather than claiming parity.

**Acceptance evidence:** pinned input/target/corpus identities + explicit contract + actual candidate build/tests + finite reference/candidate differential receipt + unresolved obligations. Formal universal equivalence is not established by matching finite tests, source resemblance or binary header parsing.
