# Synthetic flow (illustration, not executable evidence)

## EntryPoint

```text
POST /activate(input):
  if input.approved is not true: reject
  publish ActivationRequested(input.accountId)
```

## Consumer

```text
on ActivationRequested(accountId):
  write(accountId, status = Active)
```

Only these two excerpts are visible. They do not establish delivery, uniqueness of writers, retries, ordering, authorization or any production behavior.
