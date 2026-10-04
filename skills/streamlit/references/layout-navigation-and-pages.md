# Layout, Navigation, and Pages

## Layout principles

Use layout to express decision hierarchy. Prefer native containers and configuration over custom CSS. Read `references/design-accessibility-and-theme.md` when visual polish or accessibility is in scope.

## Responsive grouping

Use containers for semantic grouping and responsive horizontal rows when the resolved version supports them. Reserve columns for fixed grids or deliberate width ratios. Avoid deeply nested container hierarchies.

## Tabs and expanders

Tabs are alternative views of related information, not independent applications. Hidden/collapsed content may still execute depending on version and container behavior; guard expensive work when the API provides an explicit open/selection state, or move independent workflows to pages/fragments.

## Multipage default

For new apps on versions that support it, prefer `st.navigation` + `st.Page` because page registration, role/feature filtering, URL behavior, shared layout, and testing are explicit. Treat the legacy `pages/` auto-discovery pattern primarily as compatibility for existing apps or older pins.

Keep page files direct and simple. Put shared business/data/security logic in modules, not in duplicated page wrappers.

## Authorization and navigation

Dynamic navigation may hide unavailable pages, but hiding navigation is not authorization. Protected data/actions must perform backend authorization independently.

## Page state

Keep cross-page state small and intentional. Use URL binding for shareable filters when supported, `persist_state` for session/page persistence when supported, and durable storage for data that must survive a session. Do not pass large datasets through session state merely to move between pages.

## UX review

Check title/purpose, global vs local controls, loading/empty/error/success states, navigation back paths, narrow-screen usability, and whether expensive hidden content is computed unnecessarily.
