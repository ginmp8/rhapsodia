# Runtime Control and Agent Inventory

Use when reviewing agent authority, runtime policy enforcement, or a deployment whose effective model/tool/configuration can differ from its source tree.

## Control-effectiveness ladder

Classify a control at the strongest level directly supported by evidence:

1. `declared` — policy/documentation/config intent exists, but implementation is not established.
2. `statically-present` — code/config/hook implementing the control is inspectable, but execution is not demonstrated.
3. `behaviorally-demonstrated` — an executed scenario shows the control producing the expected allow/deny/modify/ask/defer or equivalent outcome under a frozen scenario/evaluator identity.
4. `runtime-observed` — production/runtime telemetry or equivalent supplied evidence shows the control operating in the relevant environment.

Never infer a higher level from a lower one. `runtime-observed` is environment-specific and may still leave untested paths.

## Enforcement-point record

For every high-impact action, record when material:

| Field | Meaning |
|---|---|
| action | read/write/execute/delete/send/publish/schedule/deploy/approve/delegate |
| resource_scope | exact affected resource or boundary |
| policy_source | user/policy/config/system source controlling the action |
| enforcement_point | pre-action hook, gateway, tool wrapper, authorization check, or `none/unknown` |
| disposition | allow/deny/modify/ask/defer/not-applicable or target-native equivalent |
| failure_mode | fail-closed, fail-open, degrade, retry, or unknown |
| effectiveness | declared/statically-present/behaviorally-demonstrated/runtime-observed |
| evidence_refs | exact structural/behavioral/runtime evidence identities |
| rollback_containment | how harmful effects are prevented, reversed, or bounded |

A high-impact action with policy but no verifiable enforcement point remains a governance risk or needs-verification condition; do not call the policy effective merely because it is documented.

## Runtime inventory

When runtime composition can affect the review, capture an inventory separate from the source-tree receipt. Include only relevant components, with identity when available:

- agent/workflow identity and version/revision;
- model/provider/deployment identifier;
- prompts/system policies or policy bundle identity;
- tools and executable capabilities;
- MCP servers, plugins, connectors, gateways, or remote services;
- packages/runtime dependencies when material;
- memory/vector/retrieval stores and tenant/session scope;
- environment/runtime configuration that changes authority or controls.

Use a portable component model. Optional BOM mappings such as CycloneDX/SPDX/SWID may be referenced when supplied, but no external BOM format is required for core correctness.

## Identity and drift

Source-tree identity and runtime-inventory identity are different evidence objects. A unchanged tree with a different model, tool catalog, MCP server, policy bundle, or runtime configuration can invalidate prior runtime conclusions. Record drift explicitly rather than silently reusing assurance.
