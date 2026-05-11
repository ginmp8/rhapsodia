# AOT, Trimming, Reflection, and Source Generators

## Rules

- Prefer source generators over runtime reflection when available.
- Avoid reflection in hot paths and AOT-sensitive code.
- Cache reflection metadata if unavoidable.
- Validate trimming/AOT publish when the target deployment requires it.
- Be explicit about dynamic serialization, plugin loading, and assembly scanning risks.

## Use reflection for

- startup-time discovery;
- tests and architecture rules;
- tooling;
- carefully bounded plugin models.

## Avoid reflection for

- per-request mapping;
- per-message serialization decisions;
- high-volume object construction;
- security-sensitive dispatch.
