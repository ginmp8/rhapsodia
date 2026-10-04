# Adaptive Effort Policy

## Purpose

Choose the least private reasoning effort that can satisfy the frozen obligations. Effort and representation are orthogonal. This policy controls *how much* reasoning work is justified; `references/compression-protocol.md` controls *how compactly* private state is represented. Keep the two controls independent.

## Effort levels

### direct

Use when the answer is deterministic or immediately known from trusted context and no material multi-step inference, tool call, citation verification, or validation is needed.

### light

Use for bounded low-risk reasoning with stable facts, one or two obvious transformations, and clear success criteria. Escalate if ambiguity, contradiction, external evidence, or validation becomes material.

### standard

Default for genuine multi-step work: synthesis across sources, tool planning, code/artifact analysis, comparisons, evidence handling, or uncertain decisions that still have bounded scope.

### deep

Use when omission is costly: high stakes, destructive/irreversible impact, security/privacy, conflicting sources, difficult code correctness, repeated failed attempts, unclear contracts, or validation that needs adversarial checking.

## Selection rule

Choose the lowest level that satisfies all applicable obligations. Consider:

- task decomposition depth;
- uncertainty and number of plausible interpretations;
- stakes and reversibility;
- evidence/citation burden;
- tool or external dependency count;
- validation/verification burden;
- prior failure or contradiction;
- compatibility and migration risk.

Do not lower effort merely because a user asks for a short answer; visible brevity and private effort are separate.

## Escalation and de-escalation

Escalate when new evidence introduces a contradiction, missing dependency, failed validation, higher stakes, or a materially different interpretation. A risky subproblem may permanently require the higher level even if adjacent work is simpler.

De-escalate only after the risky condition is resolved and the remaining subproblem has stable success criteria. Never oscillate levels just to satisfy a token target.

## Budget rule

Treat token/time/cost budgets as optimization constraints *after* hard obligations and quality are protected. A budget may influence which valid path or tool set to choose, but it may not justify fabricated evidence, skipped validation, unsafe advice, or incomplete required output.

Hard output/context/token caps are not reasoning policies. They may terminate generation before a valid answer exists. If the host reports truncation/incomplete output, propagate it as a failed or incomplete run and either retry with a safer configuration when authorized or report the limitation.

## Host mapping

The portable core uses `direct|light|standard|deep`; it does not depend on provider parameter names. If the host exposes an effort/thinking control, map these levels conservatively through `references/host-capabilities.md`. If no such control exists, implement the policy through scope, context admission, tool selection, stopping, and validation behavior rather than inventing unsupported settings.
