# Orchestration Patterns

## Selection rule

Start with `single`. Move to a more complex strategy only when a concrete dependency, isolation, evidence, or scale requirement justifies it.

## Patterns

### Single

One bounded worker owns one outcome. Prefer this when decomposition would only duplicate context or coordination.

### Sequential

Use explicit dependencies when each stage consumes the previous stage's output or shares mutation state.

### Classify-route

Use one bounded classification to select exactly one known route. Keep route ownership outside the classifier.

### Fan-out/synthesize

Use independent read-mostly stages against frozen inputs, then one synthesis stage that depends on all required units. Do not fan out writes to a shared surface.

### Pipeline

Use repeated ordered stages per independent item. Do not add a global barrier between every item unless one is actually required.

### Adversarial verification

Use an isolated verifier to challenge a producer result. The verifier does not rewrite acceptance criteria or gain executor authority because it found a defect.

### Generate/filter and tournament

Freeze the evaluator before candidate generation. Candidate diversity is useful only when the evaluator can distinguish relevant differences. Keep rejected candidates from silently altering the control policy.

### Bounded loop

Require an objective predicate plus finite iterations/retries. Re-entry without changed evidence/state is a stop condition.

## Anti-patterns

- parallel writers touching the same resource;
- recursively delegating without depth/fan-out limits;
- using multiple agents because multiple agents are available;
- treating a reviewer with the producer's full hidden history as independent;
- changing evaluator or success criteria after seeing a candidate;
- allowing workers to update global orchestration state directly;
- using generated arbitrary code as the only representation of authority or workflow policy;
- installing an external orchestrator solely to reproduce a native host capability.
