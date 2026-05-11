# Configuration, Options, Secrets, and Feature Flags

## Rules

- Bind settings to typed options classes.
- Validate options at startup when missing config would break runtime behavior.
- Do not commit real secrets in `appsettings.json`, examples, tests, Docker, CI, or docs.
- Prefer managed identity/workload identity over static credentials.
- Prefer managed secret stores over raw environment variables for production secrets.
- Keep `.env.example` placeholder-only.
- Treat feature flags as operational controls with owners and cleanup dates.

## Options pattern

```csharp
builder.Services.AddOptions<PaymentOptions>()
    .BindConfiguration("Payment")
    .ValidateDataAnnotations()
    .ValidateOnStart();
```

## Secret review

Classify suspected credentials as confirmed only when the value looks real or provider-specific. Mask secrets in outputs and recommend rotation for real exposures.
