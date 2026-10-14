# Edit-fields workflow

1. Resolve one workspace and read `fields.yaml` with the sibling outline and relevant results.
2. Preserve existing categories, unknown metadata, reserved `uncertain: []` and item identities. Apply explicit edits before suggesting additional comparison dimensions.
3. Deduplicate names and semantic equivalents; do not merge fields that are genuinely distinct. Every field has `name`, informative `description`, valid `detail_level` (`brief|moderate|detailed`) and optional explicit `required: false`.
4. All fields without `required: false` are required. Changing type, name, meaning, category or required status requires migration analysis and affected-result revalidation. Do not rewrite prior results just to pass a new schema.
5. Validate the workspace. Report added/removed/renamed/moved fields, required-field impact, schema drift and which historical results require research or revalidation.
