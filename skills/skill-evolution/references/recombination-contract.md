# Recombination Contract

Recombine semantic transformations, not arbitrary diffs.

## Operators

### transformation-merge

Use when two survivors contain compatible transformations affecting different capabilities or complementary failure modes. The child request names one base parent, one or more donors, and the exact transformation ids to retain/apply.

### backcross

Use when a novel candidate adds useful behavior but regresses toward a weaker canonical property. Use the canonical candidate as base or donor, retaining only the proven novel transformation(s) that justify the child.

### repair-crossover

Use when a strong candidate has one evidenced deficit and another candidate/registry entry contains a transformation specifically addressing that deficit. Do not import unrelated donor changes.

### bounded-mutation

Add, remove, replace, or parameterize one evidence-backed transformation or strategy choice. This is not random prompt rewriting.

## Compatibility

Before emitting a child request:

1. reject transformation conflicts declared in the registry;
2. include required dependencies;
3. check affected capability invariants;
4. keep one causal question per child when practical;
5. prefer already accepted/validated transformations over speculative ones unless novelty is the explicit purpose;
6. never use evaluator feedback that violates holdout blindness.

## Candidate request

```json
{
  "candidate_id": "C07",
  "operator": "transformation-merge",
  "base_parent_id": "C03",
  "donor_parent_ids": ["C05"],
  "transformation_ids": ["T002", "T008"],
  "expected_capability_effects": ["activation", "validation"],
  "reason": "complementary non-conflicting transformations"
}
```
