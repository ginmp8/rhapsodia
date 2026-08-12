# Workflow Manifests for Skills and Plugins

## Purpose

A workflow manifest describes requested orchestration. It does not activate or execute skills by itself. An executor must resolve each skill, enforce authority, validate inputs and outputs, and manage state.

## Recommended Step Contract

```json
{
  "id": "planning",
  "skill": "mago",
  "action": "define_spec",
  "instruction": "Produce the technical planning package.",
  "depends_on": ["governance"],
  "input": {
    "source": "$.results.intake"
  },
  "output": {
    "key": "spec",
    "schema": "mago-spec-v2"
  }
}
```

Responsibilities:

- `id`: unique workflow-local identifier;
- `skill`: registered skill identifier;
- `action`: supported mode or operation;
- `instruction`: request specific to this execution;
- `depends_on`: explicit dependencies;
- `input`: data references or literal values;
- `output`: result key and contract identifier.

Do not copy the full permanent skill prompt into `instruction`. The skill package remains the source of truth.

## Execution Modes

- `sequential`: list order is execution order;
- `dependency_graph`: execute when dependencies are satisfied;
- `parallel`: use only for independent steps and bounded concurrency.

## Required Validation

- workflow and schema versions are known;
- step IDs are unique;
- every dependency exists;
- dependency graph has no cycle;
- skill and action are allowlisted;
- handoff schemas are compatible;
- privilege requests are permitted;
- failure and retry policies are bounded;
- output keys do not collide unexpectedly.

## Ownership

When multiple skills govern different artifacts, declare ownership and reject cross-owner writes unless explicitly authorized.

```json
{
  "ownership": {
    "nomia": ["status", "roadmap", "release_notes"],
    "mago": ["technical_design", "tasks", "validation_plan"],
    "magia": ["implementation", "tests", "execution_evidence"]
  },
  "conflict_policy": {
    "cross_ownership_write": "reject",
    "unknown_owner": "stop"
  }
}
```

## State and Evidence

Persist concise machine-readable state, but retain human-readable evidence for review.

```json
{
  "workflow_id": "feature-delivery-014",
  "status": "validation",
  "completed_steps": ["governance", "planning", "implementation"],
  "pending_steps": ["validation"],
  "blockers": []
}
```
