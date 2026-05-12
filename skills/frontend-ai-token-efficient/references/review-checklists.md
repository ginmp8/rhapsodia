# Review checklists

Use these checklists for frontend architecture, PR, security, UX, runtime validation, and AI-maintainability reviews. Do not treat checklist completion as proof of correctness; it is triage plus reasoning.

## Architecture checklist

- [ ] The feature owner is clear.
- [ ] The change can be understood by reading a small, local file set.
- [ ] Business rules are not placed in `shared`.
- [ ] `shared` does not import features.
- [ ] Feature-to-feature imports are avoided or explicitly justified.
- [ ] API transport, mappers, schemas, and UI rendering are separated.
- [ ] Global state is justified by stable cross-cutting use.
- [ ] New abstractions have repeated, stable use cases.
- [ ] Documentation explains non-obvious constraints.

## PR review checklist

- [ ] The PR states the user-facing or developer-facing outcome.
- [ ] The touched file set is minimal for the change.
- [ ] Existing design-system and architecture conventions are preserved.
- [ ] Loading, empty, error, disabled, success, and permission states are handled when relevant.
- [ ] Forms preserve input on error and focus the first invalid field.
- [ ] API contracts are confirmed or assumptions are explicit.
- [ ] Sensitive data is not logged, stored, exposed in URLs, or sent to analytics.
- [ ] Tests match the risk level.
- [ ] Runtime/browser validation is included for interactive behavior.
- [ ] Validation evidence separates executed commands from recommended checks.

## AI-maintainability checklist

- [ ] A future agent can identify where to make the next related change.
- [ ] File and folder names reflect ownership and purpose.
- [ ] Broad barrels do not hide dependencies.
- [ ] Types and schemas are close to the boundary they protect.
- [ ] Mappers avoid leaking transport shapes into UI components.
- [ ] Comments explain constraints, not obvious code.
- [ ] AI-facing docs are short and current.
- [ ] There is no generated-looking over-abstraction.

## UX and CRO checklist tied to implementation

- [ ] The primary user task is clear.
- [ ] The first screen tells the user what to do next.
- [ ] Required fields are justified by value, compliance, or backend need.
- [ ] Labels stay visible; placeholders are examples only.
- [ ] CTAs describe the action or result.
- [ ] Error messages are specific and close to the problem.
- [ ] The flow reduces time to first value.
- [ ] Empty states explain value and offer a next action.
- [ ] Mobile layout and input types are appropriate.
- [ ] Accessibility is not sacrificed for visual polish.

## Runtime validation checklist

- [ ] Browser and viewport are specified.
- [ ] Main path and failure path are covered.
- [ ] Form error focus is checked.
- [ ] Modal focus trap, Escape behavior, and return focus are checked.
- [ ] Keyboard-only navigation is checked.
- [ ] Console errors are reviewed.
- [ ] Network failures or API error states are simulated when relevant.
- [ ] Screenshots, traces, or videos are captured when useful.
- [ ] Known gaps are documented.

## Frontend security checklist

- [ ] No secrets or secret-like names in public environment variables.
- [ ] No service token, client secret, private key, or password in frontend code.
- [ ] Sensitive auth/session tokens are not stored in localStorage or sessionStorage.
- [ ] Logs and analytics avoid payloads, raw personal data, financial data, and tokens.
- [ ] Sensitive data is not exposed in URL paths or query strings.
- [ ] `dangerouslySetInnerHTML` or HTML injection has sanitizer and explicit approval.
- [ ] CSP, source map, cache, and third-party script posture are considered.
- [ ] Frontend permission checks are treated as UX only; backend authorization is required.

## Documentation checklist

- [ ] `AI_CONTEXT.md` explains the project structure and change rules.
- [ ] `ARCHITECTURE.md` explains dependency direction and ownership.
- [ ] `DEPENDENCY_RULES.md` is consistent with actual imports.
- [ ] `TESTING_GUIDE.md` maps risks to test types.
- [ ] `API_GUIDE.md` explains contracts, mappers, and error handling.
- [ ] `SECURITY_FRONTEND.md` blocks common leak paths.
- [ ] Docs avoid stale framework tutorials and focus on project decisions.
