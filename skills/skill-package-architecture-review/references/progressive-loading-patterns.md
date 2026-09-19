# Progressive Loading Patterns

**Contract version:** 2.0.0

Use for `progressive-loading-review` and whenever context/load shape affects an architecture decision.

## Observable facts first

Record before judgment:

- resources directly declared by `SKILL.md`;
- resources reachable only indirectly;
- branch/mode-specific loading instructions;
- hidden activation/stop rules outside the control plane;
- references always co-loaded;
- deep reference chains;
- scripts/assets without declared invocation/use;
- duplicated rules across control plane and references.

Use `scripts/inventory_skill_package.py` for direct resource/path evidence when available. Its loading map is incomplete for semantic/dynamic relationships; inspect package instructions before judging.

## Healthy control plane

A healthy `SKILL.md`:

1. exposes activation boundaries in frontmatter;
2. defines purpose, authority, modes, and stop conditions;
3. routes to branch-specific references only when needed;
4. names scripts/assets by operational role;
5. keeps output contract visible;
6. avoids embedding long branch-only rubrics, schemas, examples, or policy catalogs.

## Risk patterns

- critical activation or safety rules exist only in deep references;
- simple tasks require loading unrelated branches;
- references chain through multiple layers to discover mandatory rules;
- `SKILL.md` duplicates most reference content;
- a script/template exists but no workflow or consumer explains it;
- evals are described as measured without execution;
- one overloaded reference mixes separable decisions with different consumers.

## Decision implications

Progressive-loading issues alone normally prefer this repair order:

1. clarify direct loading rule;
2. relocate hidden control-plane rules;
3. split an overloaded reference by real branch/consumer;
4. merge always-co-loaded duplicated references;
5. extract a mode only when independent activation/lifecycle evidence also exists;
6. split the skill only when broader separation evidence satisfies rubric v2.0.0.

Never recommend splitting only because `SKILL.md` or a reference is long. Context cost must be tied to actual routing/loading behavior.
