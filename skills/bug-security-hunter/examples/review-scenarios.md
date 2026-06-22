# Review Scenarios

## Activating examples

- "Review this PR for bugs and security issues. Use severity emojis for BLOCKER, MAJOR, MINOR, NIT, and QUESTION."
- "Stress this SNS/SQS flow to find loops, duplicated retries, and side effects."
- "Analyze this C# consumer and check whether retry can duplicate the operation."
- "Threat-model this account-opening flow."
- "Design a harness to reprocess Kafka events and validate idempotency."
- "Look for general bugs in this project, starting with authentication, events, and database access."
- "Give me concise comments that I can post on this PR."
- "Can this migration merge safely with the current deployment strategy?"

## Non-activating examples

- "Implement this feature" -> implementation skill or coding assistant, unless the user asks for review, validation, or hardening.
- "Explain what Kafka is" -> generic explanation, not a bug/security hunt.
- "Create a product roadmap for onboarding" -> product planning.
- "Write an email to stakeholders" -> writing task.

## Ambiguous examples

- "Is this code correct?" -> activate as quick triage only if code or another artifact is supplied; otherwise ask for the target artifact.
- "How can this flow be improved?" -> activate only if the improvement goal is correctness, security, reliability, or validation.
- "Look at this project" -> proceed with project-wide audit assumptions only if repository/files are available; otherwise request the smallest useful target area.

## Example finding

```markdown
1. 🔴 `BLOCKER` - Retry can duplicate external notification
   - File/line: `src/Notifications/SendNotificationHandler.cs:L42-L58`
   - Security confidence: Not applicable
   - Evidence label: confirmed
   - Evidence: `SendNotificationAsync` runs before message acknowledgement, and no idempotency key is passed to the provider.
   - Impact: a crash after provider success can resend the notification on retry.
   - Smallest fix: persist/send an idempotency key based on business operation before calling the provider, or use an outbox-backed notification command.
   - Validation: crash-point test after provider success and before ack; assert exactly one provider call for the business key.
   - Blocks merge: Yes
   - Expected treatment: Fix in this PR
```


## Example suggested PR comment

```markdown
🔴 `BLOCKER` - `SendNotificationAsync` runs before durable acknowledgement and no idempotency key is sent to the provider. A crash after provider success can duplicate the external side effect on retry. Please add an idempotency key or outbox-backed command and validate with a crash-point retry test.
```
