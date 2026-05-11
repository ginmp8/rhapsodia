# Time, Dates, Clock, and Time Zone

## Rules

- Use `DateTimeOffset` for instants crossing boundaries.
- Store instants in UTC unless a domain rule requires local civil time.
- Use an injectable clock for business logic and tests.
- Keep time zone decisions explicit for deadlines, regulatory windows, business days, and SLAs.
- Avoid `DateTime.Now` in domain/application code.

## Model carefully

- expiration time;
- cut-off windows;
- retry schedules;
- audit timestamps;
- local business calendars;
- daylight saving transitions;
- partner-specific time zones.
