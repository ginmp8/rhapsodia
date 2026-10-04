# Time, Dates, TimeProvider, and Time Zones

## Rules

- Use `DateTimeOffset` for instants crossing boundaries.
- Store instants in UTC unless a domain rule requires local civil time.
- Prefer `TimeProvider` at application/infrastructure boundaries for logic that depends on current time.
- In tests, prefer `FakeTimeProvider` (from the supported testing package/tooling) to sleeping, polling wall-clock time, or hand-rolled mutable clocks when it fits the repository.
- Keep time-zone decisions explicit for deadlines, regulatory windows, business days, and SLAs.
- Avoid `DateTime.Now`/`DateTime.UtcNow` directly in domain/application code when deterministic time is required.

## Model carefully

- expiration time;
- cut-off windows;
- retry schedules;
- audit timestamps;
- local business calendars;
- daylight-saving transitions;
- partner-specific time zones.

## Test rule

Advance fake time deterministically and assert behavior without real delays. Still test time-zone/civil-time edge cases explicitly; a fake clock does not solve ambiguous/invalid local times or calendar rules.
