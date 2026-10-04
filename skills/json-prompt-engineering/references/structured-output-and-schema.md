# Structured Output and Schema

## Mechanism and guarantee

| Mechanism | What it can establish | What it does not establish |
|---|---|---|
| Prompt asks for JSON | best-effort formatting | valid JSON or schema adherence |
| JSON mode | provider-defined JSON syntax guarantee | semantic correctness or arbitrary schema adherence |
| Structured Output | provider-supported schema subset adherence for eligible success outputs | business correctness, authorization, or unsupported constraints |
| Tool calling | structured arguments for a declared operation | permission to execute or correctness of the operation |
| Conforming JSON Schema validator | validity against the declared dialect | provider support, business correctness, or authorization |
| Application validation | deterministic domain checks the application implements | model reasoning quality |

Never collapse these into a single `valid` flag.

## Canonical contract first

Use one provider-neutral canonical schema when the same domain contract targets more than one provider or execution surface.

For standalone provider-neutral schemas, prefer Draft 2020-12 unless the consumer requires another dialect:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "verdict": {"type": "string", "enum": ["approve", "reject"]}
  },
  "required": ["verdict"],
  "additionalProperties": false
}
```

A valid JSON Schema may also be a boolean (`true` or `false`) or rely on `$ref`, composition, conditionals, and other dialect features. Do not treat a hand-written subset checker as a normative validator.

## Provider projection

When a provider supports only part of the canonical dialect:

1. freeze the canonical schema;
2. verify the current provider/API/model capability profile;
3. identify unsupported keywords, root-shape rules, limits, and incompatible features;
4. derive a provider projection without mutating the canonical source;
5. record every weakened or removed constraint with its JSON path and rationale;
6. reapply those constraints in application-side validation or record an explicit trade-off;
7. test the actual provider when runtime evidence is required.

A provider-compatible schema is not automatically semantically equivalent to the canonical contract.

## Schema design

- Use descriptive stable property names and concise `description` values.
- Define object closure intentionally; provider strict modes may impose stronger rules than the canonical domain contract.
- Use `enum`/`const` for finite domains when supported.
- Define array item contracts and meaningful size limits in the canonical schema.
- Use `null` only when its semantic meaning is explicit.
- Treat optionality and nullability as separate concerns; providers may encode optional fields differently.
- Keep identifiers as strings when integer precision/interoperability may exceed the RFC 8259 safe exact-integer range.
- Keep the canonical schema expressive enough for domain validation; do not pre-emptively weaken it to a lowest common denominator.

## Failure-state contract

At minimum distinguish:

- `success_schema_valid`;
- `refusal` or provider safety refusal;
- `incomplete` / truncation / token-limit termination;
- `tool_error` or execution error;
- `transport_error`;
- `schema_invalid` or provider-incompatible request;
- `semantic_invalid` after structurally valid output.

Do not parse every response body as if it were a successful schema instance.

## Validation axes

A robust validation report keeps these independent:

1. JSON syntax / duplicate-key interpretation;
2. normative JSON Schema conformance;
3. provider compatibility;
4. semantic/domain correctness;
5. business-rule validation;
6. authorization and side-effect policy;
7. runtime/tool execution result.

Schema-valid output can still contain wrong values. Constrained decoding can eliminate structural failures without proving semantic accuracy.

## Normative versus specialized lint

The bundled `scripts/validate_json_artifact.py` intentionally performs:

- JSON parsing with duplicate-key rejection;
- prompt-architecture lint;
- secret/API-control lint;
- workflow topology checks;
- lightweight schema design lint;
- optional provider-profile compatibility checks.

It intentionally does **not** claim full Draft 2020-12 conformance. Use a conforming validator for normative validation and report that step as `not-run` when unavailable.
