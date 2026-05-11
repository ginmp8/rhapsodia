# Serialization and Contract Versioning

## Rules

- Use `System.Text.Json` by default.
- Keep public DTOs explicit and stable.
- Avoid leaking internal enums or EF entity shapes into public contracts.
- Use converters intentionally for value objects, money, dates, and domain-specific formats.
- Prefer additive changes for backward compatibility.
- Do not rename or remove fields in public integration events without a versioning plan.

## Event versioning

For message contracts, design for forward/backward compatibility:

- add optional fields;
- keep semantic meaning stable;
- include event name, version, id, timestamp, correlation id;
- validate consumers before removing fields;
- use schema registry or contract tests when available.
