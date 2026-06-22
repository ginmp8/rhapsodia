# C# and .NET Hotspots

Apply this checklist by default for C#/.NET targets. Use current project conventions when explicit; otherwise keep recommendations version-neutral unless the user asks for a specific .NET version.

## Correctness and async

- sync-over-async: `.Result`, `.Wait()`, blocking calls in ASP.NET paths;
- `async void` outside event handlers;
- unobserved tasks, fire-and-forget without lifecycle/error logging;
- missing cancellation propagation in request handlers, consumers, and external calls;
- `DateTime.Now` where UTC or `DateTimeOffset` is needed;
- culture-sensitive parsing/formatting in data contracts;
- nullable reference assumptions, `!`, `default`, `Guid.Empty`, empty collections, and unchecked casts;
- `First`, `Single`, `SingleOrDefault` without explicit empty/duplicate handling;
- shared mutable state in singletons, static caches, or DI services.

## ASP.NET Core and APIs

- authorization missing at endpoint, policy, resource, or service layer;
- model validation assumed but not enforced;
- overposting/mass assignment on DTOs/entities;
- endpoint leaks exception or sensitive payload;
- idempotency missing on commands triggered by retries;
- request size, timeout, rate limit, and cancellation not considered for expensive paths.

## EF Core and database

- missing unique index/constraint for business idempotency;
- transaction does not include all required state changes;
- raw SQL interpolation or unsafe dynamic SQL;
- broad `ExecuteUpdate`, `ExecuteDelete`, `RemoveRange`, or update without precise predicate;
- lazy/eager loading changes causing N+1, unexpected nulls, or missing authorization filters;
- concurrency token absent for competing updates;
- migration introduces data loss, nullable mismatch, default value hazard, or incompatible expand-contract sequence.

## Messaging and workers

- message acknowledgement/offset commit before safe processing;
- retry without idempotency key or dedup storage;
- outbox/inbox absent where state change and event publish must be atomic;
- consumer trusts tenant/user/action from payload without authoritative recheck;
- handler publishes next event before local transaction commits;
- poison messages are retried forever or hide in DLQ without alert.

## Logging and observability

- logs include full payload, authorization headers, cookies, connection strings, documents, tokens, or personal data;
- correlation id lost across async boundaries;
- audit missing for privileged security decisions;
- exception handling drops stack/context or converts failure to success;
- metrics do not distinguish retry, DLQ, duplicate suppression, and terminal rejection.
