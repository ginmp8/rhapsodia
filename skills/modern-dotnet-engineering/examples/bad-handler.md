# Bad Handler Example

```csharp
public Task Handle(Command command)
{
    var onboarding = _db.Onboardings.Find(command.Id);
    onboarding.Status = "Approved";
    _httpClient.PostAsync("https://partner", null).Wait();
    _db.SaveChanges();
    return Task.CompletedTask;
}
```

Problems: sync-over-async, no cancellation, stringly status, external call in flow without timeout/idempotency, no result semantics.
