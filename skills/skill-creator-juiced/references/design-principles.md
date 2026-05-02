# Design Principles

Use this reference when deciding what the skill should contain and how to structure it.

## 1. Start from real work

Build from concrete user requests, examples, corrections, artifacts, repository evidence, internal conventions, schemas, runbooks, and failure history. Avoid generic best-practice text that the base model already knows.

Keep an instruction only when it changes likely behavior. Remove definitions, background, and motivational prose unless they prevent a recurring error.

## 2. Cohesion beats size

The main design question is not whether the skill is small or large. The question is whether the package has one coherent operational responsibility.

Healthy large skill:
- one role or capability;
- shared vocabulary;
- related inputs and outputs;
- related evidence and validation;
- modes that are variants of the same work.

Unhealthy small skill:
- unrelated topics grouped by user preference;
- activation description must say "x, y, z, and also w";
- modes have different evidence, tools, risks, and output contracts;
- one mode's instructions can interfere with another.

## 3. Modes versus router

Use modes when the skill executes variants of one role.

Example: a product-owner skill can include problem framing, prd refinement, risk review, acceptance criteria, stakeholder summary, and next steps.

Use a router when the package should classify a request and hand off to separate specialist skills.

Example: an engineering-intake router can classify product, architecture, implementation, security, migration, or documentation work and produce a handoff.

Extract a mode when it has:
- independent activation triggers;
- different tools or evidence;
- different owner or authority boundary;
- independent validators or evals;
- separate failure modes;
- frequent use without the parent skill.

## 4. Progressive loading

`SKILL.md` is a control plane, not a knowledge dump. It should contain the mission, core rules, workflow, resource map, stop conditions, and output contract.

Put branch-specific detail in `references/`. Keep references one level away from `SKILL.md` and link them directly.

Use `scripts/` for repeatable deterministic actions. Use `assets/` for files used in outputs, not reasoning.

## 5. Activation quality

The frontmatter description is the primary trigger surface. It should describe what the skill does and when to use it using phrases users are likely to write.

A good description covers:
- triggers;
- target artifacts;
- common synonyms;
- boundaries with adjacent skills;
- specific workflows, file types, or tasks when relevant.

Avoid vague descriptions such as "helps with product" or "assists with code".

## 6. Output consistency

If output shape matters, include a template. If style matters, include input/output examples. If safety or correctness matters, include gates and stop conditions.

Prefer defaults over menus. State the preferred path, then exceptions.

## 7. Evidence and validation

Separate planned scenarios from executed results. Do not claim scores, pass rates, precision, recall, or robustness unless captured by an executed harness or supplied evidence.

Validation can include:
- structure validation;
- local link checks;
- placeholder checks;
- script syntax and smoke tests;
- activation and non-activation scenarios;
- package validation;
- security or governance review;
- benchmark reports when requested.
