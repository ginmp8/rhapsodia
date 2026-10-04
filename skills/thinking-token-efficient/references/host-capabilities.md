# Host Capability Model

## Purpose

Keep the portable reasoning policy independent of provider-specific APIs. Detect capabilities when available; otherwise use safe semantic fallbacks. Host-specific adapters or documentation may map these capabilities, but the core must remain valid when those adapters are absent.

## Capability profile

Record only capabilities relevant to the current task:

- `can_control_reasoning_effort` - host can request lower/higher reasoning effort.
- `can_measure_reasoning_tokens` - host exposes reasoning-token telemetry for the run.
- `can_preserve_reasoning_state` - host can carry opaque reasoning state across calls/tool loops without exposing raw chain of thought.
- `can_detect_truncation` - host reports incomplete/truncated generation distinctly from success.
- `can_report_cached_tokens` - host exposes cache/token-reuse telemetry.
- `can_lazy_load_tools` - host can defer tool/schema loading until relevant.
- `can_report_latency_cost` - host exposes comparable latency and/or monetary cost telemetry.

Unknown capability state is `unknown`, not `false`, unless absence is established.

## Portable fallbacks

| capability unavailable | fallback |
|---|---|
| reasoning-effort control | use the host-neutral effort policy through context, scope, tool choice, stopping, and validation behavior |
| reasoning-token telemetry | make no hidden-token saving claim; report only observable/static metrics |
| reasoning-state preservation | carry a compact semantic checkpoint: load-bearing facts, unresolved unknowns, current decision, and pending checks |
| truncation detection | treat suspiciously incomplete output as unverified; do not silently label it success |
| cached-token telemetry | omit cache savings claims |
| lazy tool loading | manually restrict tool/reference loading to named information needs |
| latency/cost telemetry | omit measured latency/cost claims or label estimates explicitly |

## Reasoning-state continuity

Opaque host reasoning state may be reused only when the host supports it safely. Do not decode, reconstruct, summarize as raw chain of thought, or require it for portability. The fallback semantic checkpoint must contain only decision-relevant state that is safe to expose if necessary: facts, assumptions/unknowns, chosen direction, and pending checks.

## Adapter boundary

Vendor/model parameter names, supported level names, defaults, and deprecations change over time. Keep them out of the portable core unless the user explicitly asks for a host adapter. A host adapter may map `direct|light|standard|deep` to current controls, but correctness must not depend on one vendor's private runtime.
