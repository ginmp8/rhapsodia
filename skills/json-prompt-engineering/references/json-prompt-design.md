# JSON Prompt Design

## Architecture Decision

Use the smallest structure that makes the interface clearer.

| Situation | Preferred format |
|---|---|
| Human writes and maintains long instructions | Markdown |
| Application supplies typed variable data | JSON |
| Human rules plus structured runtime data | Hybrid |
| Application parses the response | Native Structured Output or tool schema |
| Multiple skills exchange state | Versioned workflow manifest |

## Hybrid Default

Separate three concerns:

1. stable instructions in Markdown;
2. variable input as serialized JSON;
3. output contract through the provider's native schema facility.

Do not duplicate the same rule in all three layers.

## Field Design

Use names that communicate domain meaning:

```json
{
  "task": "review_code",
  "context": {
    "language": "C#",
    "framework": ".NET 10"
  },
  "input": {
    "source_code": "..."
  },
  "constraints": {
    "maximum_findings": 20
  }
}
```

Prefer arrays for ordered values and repeatable items. Do not depend on object property order.

Use native JSON types:

- boolean for flags;
- number for quantities;
- string for identifiers that may exceed interoperable integer ranges;
- array for ordered or repeated values;
- `null` only when the contract defines its meaning.

## Recommended Top-Level Fields

Use only the fields that add value:

- `prompt_version`;
- `task` or `objective`;
- `context`;
- `input`;
- `instructions`;
- `constraints`;
- `missing_information_behavior`;
- `output_requirements`.

Do not place API sampling parameters in the prompt merely because they are representable as JSON.

## Conversion Rules

When converting a traditional prompt:

1. preserve the original objective and prohibitions;
2. keep long behavioral rules as Markdown unless programmatic generation requires JSON;
3. move runtime values into typed fields;
4. move response structure into native schema configuration when available;
5. remove repeated statements and decorative nesting;
6. preserve examples only when they disambiguate behavior.

## Anti-Patterns

- one field per sentence with no machine use;
- deeply nested configuration objects;
- full natural-language policies escaped inside one JSON string;
- copied permanent instructions from referenced skills;
- output examples presented as if they were formal schemas;
- properties named `data`, `value`, or `config` when a domain name is available;
- string values such as `"true"`, `"10"`, or comma-separated lists where native types are appropriate;
- assuming that a JSON-shaped prompt forces a JSON-shaped response.
