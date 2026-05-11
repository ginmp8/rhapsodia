# Order mode

Use order mode when the request is about sequence, catalog maintenance, inserting work packages, reconciling dependencies, or deciding the next ordered items in a cycle.

## Scope
- planning-only
- operate on exactly one active `<cycle_version>/spec-catalog.yaml`
- do not create or modify spec package files unless the caller explicitly asks for a combined order plus define pass

## Required catalog shape
`spec-catalog.yaml` must contain:

- `schema_version`
- `cycle_version`
- `cycle_status`
- `specs`

Each `specs` entry must include:

- `order`
- `spec_id`
- `feature_key`
- `title`
- `type`
- `classification`
- `depends_on_features`
- `depends_on_specs`
- `status`
- `feature_version`

## Rules
- preserve existing `spec_id`, `order`, `feature_key`, and dependency relationships unless evidence requires change
- use `specNNN` ids
- keep `order` sortable and usually increment by 10
- allow gaps
- do not casually renumber existing specs
- keep `depends_on_features` and `depends_on_specs` separate
- use `type: fix` only for bugfix-style work
- otherwise default to `type: feature`
- discovery is upstream evidence only and must not define `spec_id`, `order`, `cycle_version`, or `feature_version`

## Final check
Before finishing, verify that:
- the catalog is internally consistent
- sequence and dependency summary are explicit
- `spec_id` and `feature_key` are not mixed
- no spec folder was created during a pure order pass
