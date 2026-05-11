# Abstractions, Design, and Anti-Overengineering

## Create abstractions when

- crossing external boundaries;
- multiple real implementations exist;
- tests need isolation from slow/unreliable dependencies;
- a policy or strategy varies by business rule;
- the boundary protects the domain/application layer.

## Avoid abstractions when

- the interface merely mirrors one implementation;
- there is no variation;
- the only reason is future-proofing;
- the abstraction hides important behavior;
- naming becomes `Manager`, `Helper`, `Utils`, or `Service` without domain meaning.

## Naming

Prefer role names: `IEligibilityPolicy`, `IAccountOpeningGateway`, `IClock`, `IIdempotencyStore`.
