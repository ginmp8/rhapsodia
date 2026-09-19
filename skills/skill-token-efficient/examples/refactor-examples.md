# Refactor Examples

## Safe imperative shortening

Before: `You should make sure that you read the target SKILL.md first before doing any other work.`

After: `Read target SKILL.md first.`

## Merge duplicate negatives

Before: `Do not edit secrets. Do not edit credentials. Do not edit .git. Do not edit benchmark fixtures.`

After: `Do not edit secrets, credentials, .git, or benchmark fixtures.`

## Reject false efficiency

Bad: `Validate everything. No unsafe stuff. Pack if ok.`

Why rejected: it removes specific safety, evidence/citation, validation, and output duties. Fewer tokens do not demonstrate equivalence.
