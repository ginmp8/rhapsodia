# Review Scenarios

## Activating examples

- "Revise esse PR para encontrar bugs e problemas de segurança."
- "Quero estressar esse fluxo SNS/SQS para achar loops e efeitos colaterais."
- "Analise esse consumer C# e veja se retry pode duplicar operação."
- "Faça threat model desse fluxo de abertura de conta."
- "Monte um harness para reprocessar eventos Kafka e validar idempotência."
- "Procure bugs gerais no projeto, começando por autenticação, eventos e banco."

## Non-activating examples

- "Implemente essa feature" -> implementation skill or coding assistant, unless the user asks for review/hardening.
- "Explique o que é Kafka" -> generic explanation, not a bug/security hunt.
- "Crie um roadmap de produto" -> product/planning skill.
- "Escreva um e-mail para stakeholders" -> writing task.

## Ambiguous examples

- "Está certo esse código?" -> activate if code is supplied; use quick triage and ask only if the target is missing.
- "Como melhorar esse fluxo?" -> activate only if the improvement goal is correctness, security, reliability, or validation.
- "Olhe esse projeto" -> proceed with project-wide audit assumptions only if repository/files are available; otherwise request the smallest target artifact or area.

## Example finding

```markdown
1. [high] Retry can duplicate external notification
   - Evidence: `SendNotificationAsync` runs before message acknowledgement, and no idempotency key is passed to the provider.
   - Impact: a crash after provider success can resend the notification on retry.
   - Smallest fix: persist/send an idempotency key based on business operation before calling the provider, or use an outbox-backed notification command.
   - Validation: crash-point test after provider success and before ack; assert exactly one provider call for the business key.
```
