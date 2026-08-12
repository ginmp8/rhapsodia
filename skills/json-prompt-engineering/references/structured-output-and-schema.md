# Structured Output and Schema

## Distinguish the Mechanisms

| Mechanism | Main guarantee |
|---|---|
| Prompt asks for JSON | Best-effort model behavior |
| JSON mode | Usually valid JSON syntax |
| Structured Output | Provider-supported schema adherence |
| Tool calling | Structured arguments for an operation |
| Application validator | Local deterministic contract enforcement |

Do not describe JSON mode as equivalent to schema adherence.

## Schema Design Rules

- Define `type` explicitly.
- List mandatory properties in `required`.
- Use `additionalProperties: false` when a closed contract is intended.
- Use `enum` for finite domains.
- Add concise `description` values for semantic guidance.
- Define array `items` and useful size limits.
- Keep schemas shallow enough for the target provider.
- Test the exact provider and model because supported JSON Schema subsets differ.

Example:

```json
{
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "verdict": {
      "type": "string",
      "enum": ["approve", "reject"],
      "description": "Final review decision."
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "severity": {
            "type": "string",
            "enum": ["critical", "high", "medium", "low"]
          },
          "description": {
            "type": "string"
          }
        },
        "required": ["severity", "description"]
      }
    }
  },
  "required": ["verdict", "findings"]
}
```

## Semantic Validation

Schema validity does not prove that:

- dates are logically ordered;
- totals reconcile;
- identifiers exist;
- a user is authorized;
- a recommendation is correct;
- a tool action is safe.

Perform semantic validation, business validation, and authorization after structural validation.

## Provider Compatibility

For provider-specific work:

1. inspect current official documentation;
2. identify supported schema keywords and limits;
3. separate the canonical domain schema from the provider-compatible schema if necessary;
4. record provider, model, schema version, and prompt version;
5. test refusal, truncation, and malformed-input behavior.
