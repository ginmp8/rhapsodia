# JSON Interoperability and Canonicalization

## RFC 8259 interoperability

For data exchanged across languages/runtimes:

- object member names should be unique; duplicate names can be interpreted differently by parsers;
- object member order is not a semantic contract; use arrays when order matters;
- UTF-8 is the interoperable encoding for open interchange;
- large numeric identifiers should normally be strings when exact agreement outside the IEEE-754 safe integer range matters;
- avoid relying on parser-specific acceptance of malformed or ambiguous JSON.

The bundled linter rejects duplicate object names to keep deterministic interpretation.

## Canonicalization is optional

RFC 8785 JSON Canonicalization Scheme (JCS) is useful when a stable byte representation is needed for:

- hashing;
- signing;
- content-addressed identity;
- deterministic cache keys;
- reproducible artifact receipts.

Do not require canonicalization merely because JSON is used in a prompt. It adds value only when representation identity matters.

## Contract identity

Keep these identities separate when reproducibility matters:

- semantic schema/version identity;
- serialized/canonical byte identity;
- provider projection identity;
- runtime response identity.

Equivalent JSON objects can have different serialized bytes without semantic disagreement unless the workflow explicitly requires canonical representation.
