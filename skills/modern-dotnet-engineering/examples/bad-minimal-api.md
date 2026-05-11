# Bad Minimal API Example

```csharp
app.MapPost("/onboardings", async (AppDbContext db, Request request) =>
{
    var exists = await db.Onboardings.AnyAsync(x => x.Document == request.Document);
    if (exists) return Results.Conflict();

    db.Onboardings.Add(new Onboarding { Document = request.Document, Status = "Pending" });
    await db.SaveChangesAsync();
    return Results.Ok();
});
```

Problems: business flow is inside endpoint, no cancellation token, exposes EF as application boundary, weak status semantics.
