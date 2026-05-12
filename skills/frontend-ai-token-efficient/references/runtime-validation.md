# Runtime validation

Use this reference when static review is not enough and the frontend behavior must be checked in a browser or with Playwright.

## When runtime validation is required

Use browser validation for changes involving:

- forms, validation errors, focus, and submit behavior;
- modals, dialogs, drawers, overlays, and menus;
- keyboard navigation and screen-reader-sensitive behavior;
- responsive layout and mobile input behavior;
- loading, empty, error, disabled, permission, and success states;
- routing, redirects, guards, and deep links;
- charts, canvas, drag-and-drop, file upload, or browser APIs;
- visual regression risk.

## Evidence hierarchy

Prefer executed evidence over static claims:

1. command output from typecheck, tests, lint, and Playwright;
2. screenshots, traces, videos, console logs, and network logs;
3. inspected code paths and component states;
4. static reasoning and recommended checks.

Always label what was executed versus recommended.

## Playwright plan template

```md
## Scope
- feature:
- route:
- browsers/viewports:
- data setup:

## Checks
1. load route and verify initial state;
2. complete the primary path;
3. trigger validation errors and verify focus;
4. check loading/error/empty states;
5. verify keyboard behavior;
6. capture mobile screenshot;
7. inspect console and network errors.

## Evidence
- command:
- screenshots/traces:
- failures:
- gaps:
```

## Modal and dialog checks

- Initial focus moves into the modal.
- Tab stays within the modal while open.
- Escape closes the modal when allowed.
- Click outside behavior matches product expectation.
- Focus returns to the trigger after close.
- Screen reader label and description are present.
- Background content is inert or otherwise protected.

## Form checks

- Required fields show specific messages.
- Submit with invalid data focuses the first invalid field.
- Input is not cleared after validation or API failure.
- Async validation has loading and retry/error behavior.
- Mobile keyboards match input type.
- Masks and formatting do not corrupt submitted value.
- Server errors are mapped to field or form-level messages.

## Responsive checks

Test at least one small viewport and one desktop viewport when layout changes. Capture screenshots for:

- first render;
- error state;
- long content or overflow state;
- primary action area;
- navigation or sticky footer/header behavior.

## Accessibility smoke checks

- Keyboard-only completion for the main path.
- Visible focus indicator.
- Semantic headings and landmarks.
- Label and error associations for inputs.
- Announcements for dynamic errors or success messages.
- Color contrast and non-color-dependent meaning.
- Reduced-motion path when animations are meaningful.

## Console and network checks

Report:

- console errors or warnings that affect the flow;
- failed network requests;
- unexpected retries;
- sensitive data in request URLs, logs, or analytics;
- unhandled promise rejections.

## Specialist browser agents

If the environment supports specialized browser agents, split responsibilities:

- implementation agent: changes code;
- QA/browser agent: runs flows and captures evidence;
- accessibility agent: checks keyboard, ARIA, focus, and screen reader-sensitive patterns;
- performance agent: checks bundle, route load, and runtime performance when relevant.

Keep artifacts small and cite them in the final response.
