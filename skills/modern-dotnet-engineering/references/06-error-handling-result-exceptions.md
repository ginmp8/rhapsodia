# Error Handling, Result Pattern, and Exceptions

## Distinction

Use exceptions for unexpected technical failure or impossible programmer errors. Use result objects for expected business outcomes.

## Use Result for

- validation failure;
- not found;
- conflict;
- forbidden business state;
- external dependency returned a known business response.

## Use exceptions for

- database unavailable;
- serialization bug;
- invariant violation caused by code bug;
- unexpected null or impossible state;
- infrastructure failure that should bubble to middleware.

## HTTP mapping

Map business results at the API boundary, not inside the domain.

```csharp
return result.Status switch
{
    ResultStatus.Ok => TypedResults.Ok(response),
    ResultStatus.NotFound => TypedResults.NotFound(),
    ResultStatus.Invalid => TypedResults.ValidationProblem(errors),
    ResultStatus.Conflict => TypedResults.Conflict(problem),
    _ => TypedResults.Problem()
};
```

## Anti-patterns

- Throwing exceptions for ordinary validation.
- Returning HTTP types from application handlers.
- Catching `Exception` and returning success or empty results.
