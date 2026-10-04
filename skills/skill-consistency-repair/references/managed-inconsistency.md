# Managed Inconsistency

Some understood inconsistencies can be retained temporarily without pretending they are resolved.

## Waiver contract

A temporary waiver must identify:

- stable waiver id and affected finding/relation ids;
- owner;
- rationale and direct evidence;
- impact/consumers;
- acceptance date;
- expiry date or explicit recheck condition;
- required validation while the waiver is active;
- state: `active`, `expired`, `resolved`, or `revoked`.

Use `assets/templates/inconsistency-waiver.json.template` for an external work artifact. Do not package run-specific filled waivers into the target unless the target explicitly owns them.

## Non-waivable hard gates

A waiver must never override:

- ambiguous target identity;
- candidate/report/package identity mismatch;
- mutation of frozen evaluator/protected evidence during acceptance;
- unsafe deletion without required consumer/compatibility evidence;
- secret/credential exposure;
- output aliasing that can overwrite protected evidence;
- failed mandatory validator/package integrity gate;
- a requirement to weaken safety/evidence/acceptance criteria merely to pass.

An expired or ownerless waiver is a live inconsistency, not an accepted trade-off.
