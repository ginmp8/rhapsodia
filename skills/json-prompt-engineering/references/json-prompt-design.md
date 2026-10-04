# JSON Prompt Design

## Architecture decision

Use the smallest structure that improves the interface.

| Situation | Preferred form |
|---|---|
| Human maintains long behavioral rules | Markdown |
| Application supplies typed variable data | JSON |
| Human rules plus structured runtime data | Hybrid |
| Application parses model output | Native Structured Output or tool schema |
| Same domain contract targets several providers | Canonical schema + provider projections |
| Multiple skills/tools exchange state | Versioned workflow manifest |

## Hybrid default

Separate stable instructions, runtime data, and output enforcement. Do not duplicate the same rule in all layers.

```text
Markdown behavior
+ JSON runtime input
+ canonical output/tool contract
+ provider projection only when needed
```

## Field design

Prefer domain names over generic containers such as `data`, `value`, or `config`.

```json
{
  "prompt_version": "2.0.0",
  "task": "review_code",
  "context": {"language": "C#", "framework": ".NET 10"},
  "input": {"source_code": "..."},
  "constraints": {"maximum_findings": 20}
}
```

Use native JSON types. Keep identifiers as strings when cross-runtime integer precision is uncertain. Use arrays for ordered/repeated values; never rely on object-property order.

## Version identities

Separate versions when they can evolve independently:

- prompt/instruction version;
- input schema version;
- canonical output/tool schema version;
- provider projection/profile version;
- workflow manifest version.

A prompt version bump must not masquerade as a schema version bump, and a provider projection refresh must not silently change the canonical domain contract.

## Conversion rules

When converting a traditional prompt:

1. preserve objective, prohibitions, and failure behavior;
2. keep long human-maintained instructions in Markdown unless machine generation requires JSON;
3. move runtime values into typed fields;
4. move machine-consumed response structure into native schema/tool configuration when available;
5. create a canonical schema before any provider-specific projection when portability matters;
6. remove decorative nesting and duplicated rules;
7. preserve examples only when they disambiguate behavior.

## Anti-patterns

- one JSON field per prose sentence without machine use;
- full natural-language policies escaped inside one JSON string;
- deeply nested wrappers with no semantic boundary;
- copied permanent instructions from referenced skills/tools;
- output examples presented as if they were formal schemas;
- provider-specific restrictions embedded into the canonical schema without a domain reason;
- silently deleting unsupported constraints to make a provider accept a schema;
- putting model/runtime controls into prompt data and assuming they configure the API;
- assuming JSON shape forces JSON output or improves reasoning.
