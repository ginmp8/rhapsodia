# Activation Scenarios

## Should activate

- "think through the smallest safe fix for this failing workflow and report validation gaps"
- "optimize your reasoning tokens while analyzing this pull request"
- "use compact thinking, but keep citations and checks intact"
- "plan the minimum tool calls needed to answer this multi-step question"
- "review this design for hidden assumptions without overexplaining"

## Should not activate

- "rewrite this email to be more formal"
- "translate this paragraph"
- "what is 2 + 2"
- "make this answer shorter for the user"
- "generate an image of a dashboard"

## Ambiguous

- "be concise" means shorten visible output unless the task is complex enough to need private reasoning discipline.
- "think less" means reduce wasted reasoning, not skip checks.
- "use caveman" means use filler-free compression only if the user also accepts professional readability; do not use comedy or broken language by default.

## Edge cases

- If citations are required, keep enough reasoning to verify source support.
- If code validation cannot run, label checks as not executed.
- If the user asks for raw chain of thought, provide a concise rationale instead.
- If over-compression would hide uncertainty, expand the internal ledger.
