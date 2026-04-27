# Roadmap

## Context

Workspace administration controls are needed so enterprise admins can explain visibility for shared analytics assets.

## Themes

- Permissions clarity.
- Admin confidence.
- Lower support escalation volume.

## Sequencing

Saved-query sharing controls come first because the scope is narrow and ready for Mago. Dashboard role preview stays later because it depends on the sharing-control model. Admin activity summary remains a future idea.

## Dependencies

- Security input on inherited dashboard permissions.
- Mago candidate `spec022` for saved-query sharing controls.

## Risks

- The first feature may create questions about dashboard inheritance that are intentionally out of scope.

## Open Decisions

- Decide whether dashboard role preview needs discovery before becoming a targeted feature.

## Mago Handoff Candidates

- `saved-query-sharing-controls` -> `spec022`
