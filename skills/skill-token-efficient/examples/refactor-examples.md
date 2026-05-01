# Refactor Examples

## Prose to imperative

Before:
```md
You should make sure that you read the target SKILL.md first before doing any other work because it contains the main instructions.
```
After:
```md
Read target `SKILL.md` first.
```

## Merge negatives

Before:
```md
Do not edit secrets. Do not edit credentials. Do not edit .git. Do not edit benchmark fixtures.
```
After:
```md
Do not edit secrets, credentials, `.git`, or benchmark fixtures.
```

## Keep detail

Bad:
```md
Validate everything.
```
Better:
```md
Validate links, protected regions, semantic invariants, touched scripts, and package gates.
```

## Avoid over-compression

Bad:
```md
No unsafe stuff. Pack if ok.
```
Better:
```md
Do not weaken safety, validation, package, or stop boundaries. Package only after validation passes.
```
