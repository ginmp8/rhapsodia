# Progressive Loading Patterns

**Contract version:** 3.0.0

Use for `progressive-loading-review` and whenever context/load shape affects an architecture decision.

## Observable facts first

Record before judgment:

- resources directly declared by `SKILL.md`;
- resources reachable only indirectly;
- branch/mode-specific loading instructions;
- hidden activation/stop rules outside the control plane;
- references always co-loaded;
- reference-to-reference chains;
- scripts/assets without declared invocation/use;
- duplicated rules across control plane and references;
- deterministic `context_topology` from the inventory when available.

Use `scripts/inventory_skill_package.py` for direct resource/path evidence. Its semantic/dynamic relationships remain incomplete; inspect package instructions before judging.

## Measured context topology

Treat these as descriptive metrics, not scores:

- `skill_md_line_count` and `skill_md_word_count`;
- `direct_declared_resource_count`;
- `reference_chain_max_depth`;
- `nested_reference_edge_count`;
- `reachable_reference_count` and `unreachable_reference_count`.

A direct `SKILL.md -> reference` relationship is normally easier to reason about than deep discovery chains, but **routing depth is not a universal hard threshold or hard cutoff**. A deeper chain becomes a finding only when evidence shows hidden mandatory rules, unnecessary context discovery, activation ambiguity, maintenance burden, or another concrete operational cost.

## Healthy control plane

A healthy `SKILL.md`:

1. exposes activation boundaries in frontmatter;
2. defines purpose, authority, modes, and stop conditions;
3. routes to branch-specific references only when needed;
4. names scripts/assets by operational role;
5. keeps output contract visible;
6. avoids embedding long branch-only rubrics, schemas, examples, or policy catalogs;
7. keeps mandatory rules discoverable without unnecessary reference chasing.

## Risk patterns

- critical activation or safety rules exist only in deep references;
- simple tasks require loading unrelated branches;
- references chain through multiple layers to discover mandatory rules;
- `SKILL.md` duplicates most reference content;
- a script/template exists but no workflow or consumer explains it;
- evals are described as measured without execution;
- one overloaded reference mixes separable decisions with different consumers;
- unreachable references appear to contain active rules but no routing/consumer evidence explains them.

## Decision implications

Progressive-loading issues alone normally prefer this repair order:

1. clarify direct loading rule;
2. relocate hidden control-plane rules;
3. split an overloaded reference by real branch/consumer;
4. merge always-co-loaded duplicated references;
5. extract a mode only when independent activation/lifecycle evidence also exists;
6. split the skill only when broader separation evidence satisfies rubric v3.0.0.

Never recommend splitting only because `SKILL.md`, a reference, file count, token proxy, or routing depth is large. Context cost must be tied to actual routing/loading behavior.
