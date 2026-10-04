# Research basis and adaptation boundary

This skill generalizes patterns derived from public engineering research. It does not reproduce, implement, or depend on vendor-specific runtimes.

Public engineering material published by Shopify about Helix informed patterns such as small ordered checkpoints, reference-as-spec, oracle-before-candidate, ordered gates, repair and re-review, context-isolated review, accepted feedback, policy-bounded autonomy, and checkpoint promotion.

Other public Shopify engineering material contributed additional patterns: River informed live-state reconciliation and closure verification; ShopGym informed fresh execution contexts built from current code, relevant specifications, and accepted feedback; and Roast informed explicit structured workflows and the migration of deterministic guarantees from prompts into code.

These sources serve solely as research provenance and evidence inputs. The resulting abstractions, contracts, terminology, and implementation are RhapsodIA-specific. RhapsodIA does not depend on Shopify models, architectures, proprietary tooling, runtimes, or exact workflow and gate taxonomies.