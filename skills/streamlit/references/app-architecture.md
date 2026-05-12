# App Architecture

Use this reference for project shape, rerun flow, state, callbacks, forms, dialogs, fragments, and multipage organization.

## Rerun-aware architecture

Streamlit executes app code top to bottom. Design every interaction as a rerun, not as a persistent frontend event handler.

Good defaults:

- render UI cheaply in the main path;
- push expensive work into cached functions;
- keep side effects behind explicit buttons or forms;
- initialize state before widget creation;
- make page modules import shared helpers rather than duplicating logic.

## Project sizing

Use a single file for a demo, tutorial, or proof of concept. Use a small package layout when the app has multiple pages, repeated charts, reusable queries, business rules, or tests.

Suggested responsibilities:

- application entrypoint: page config, high-level navigation, main page composition;
- pages: page-specific controls and presentation;
- data module: reads, queries, transformations, cache wrappers;
- chart module: reusable plotting functions;
- state module: session initialization and state transitions;
- services module: API clients and external calls;
- settings module: environment and secret loading.

## Multipage apps

For multipage work:

- keep shared state keys documented;
- isolate page-specific state with key prefixes;
- keep navigation side effects minimal;
- avoid each page creating its own incompatible cache or connection.

## Forms, callbacks, dialogs, and fragments

Use forms to batch inputs. Use callbacks only for local state changes such as setting a selected id or clearing filters. Use dialogs for short confirmation flows. Use fragments for isolated refresh areas only when the Streamlit version and hosting target support them.

## Anti-patterns

- expensive database calls directly in the main script;
- hidden business logic inside callbacks;
- widgets without stable keys in conditional layouts;
- session state used as a database;
- duplicated data loading across pages;
- global mutable objects not protected by caching or resource initialization.
