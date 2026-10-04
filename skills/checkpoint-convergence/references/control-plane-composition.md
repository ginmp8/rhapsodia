# Control-plane composition

RhapsodIA has two orthogonal control planes.

- `adaptive-workflow-orchestration` owns runtime topology and returns structured evidence.
- `checkpoint-convergence` owns reference/oracle/gate/promotion progression.

Exactly one progression owner is active. A nested dynamic workflow is evidence-only with respect to checkpoint promotion. A convergence controller never broadens a dynamic runtime's authority.

Prefer direct execution when neither control plane adds material value.
