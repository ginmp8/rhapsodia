# Progressive Loading Patterns

Use this reference for `progressive-loading-review` and for any package review where `SKILL.md` may be too large, too vague, or poorly connected to supporting files.

## Control-plane standard

A healthy `SKILL.md` should behave like a control plane:

1. Describe activation in frontmatter.
2. Define purpose and non-goals.
3. Select modes or workflows.
4. Point to references only when a branch needs them.
5. Name operational scripts and assets by role.
6. Define output contract and stop conditions.
7. Avoid embedding long rubrics, schemas, examples, or policy catalogs that are needed only for some branches.

## Loading map pattern

Use a simple map in `SKILL.md`:

```markdown
Load only what the run needs:
- `references/rubric.md`: scoring and severity.
- `references/checklist.md`: use for resource integration findings.
- `assets/templates/report.md.template`: use for durable report output.
- `scripts/inventory.py`: run when structural evidence is needed.
```

Every listed resource should be actionable: loaded, copied, filled, executed, validated, or explicitly retained as asset-only.

## Healthy patterns

- Mode table in `SKILL.md`, detailed rules in references.
- Short workflow in `SKILL.md`, branch-specific checklists in references.
- Templates in `assets/templates/` with clear fill instructions.
- Deterministic scripts for fragile inventory, validation, package creation, or schema checks.
- Examples and evals kept separate from measured claims.
- One-level reference graph: `SKILL.md` links directly to resources that may be needed.

## Risk patterns

- `SKILL.md` repeats most of each reference.
- References contain critical activation rules that are not visible in frontmatter or `SKILL.md`.
- A script exists but no workflow says when to run it.
- A template exists but no output contract uses it.
- Evals exist but are reported as measured without execution evidence.
- Deep reference chains require loading many files to understand a simple branch.
- Assets are used as reasoning documents instead of output artifacts.

## Review questions

- Can a model choose the right mode after reading only the frontmatter and `SKILL.md`?
- Does each branch name the smallest resource set needed?
- Are references organized by decision, mode, domain, or output rather than by historical accident?
- Are high-risk rules visible early enough to prevent wrong execution?
- Are local links correct and shallow?
- Does any single file force unnecessary context loading?
- Are script contracts documented where the script is invoked?

## Recommendation patterns

- Move long criteria into references when the control plane exceeds useful routing detail.
- Pull hidden activation or stop rules back into `SKILL.md` or frontmatter.
- Split one overloaded reference into branch references only if it contains separable decisions.
- Merge references when they are always loaded together and duplicate the same decision.
- Add a router section when many modes share a package but need explicit dispatch.
