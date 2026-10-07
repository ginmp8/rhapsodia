# Interaction design

## At a Glance
- **Purpose:** Define the graph explorer as a dense technical workspace rather than a generic dashboard.
- **Load when:** Modifying the HTML shell, filters, inspector, selection, path, color, motion, or accessibility.
- **Decision impact:** Preserves information density, directional meaning, keyboard access, and no-ambient-motion behavior.

## Workspace
Use one persistent shell: compact command bar, filters left, graph canvas dominant, inspector right, status strip below. Do not split graph operations into unrelated cards.

Color must encode information. Node kind may use a small stable palette. When a node is selected, incoming edges use the incoming semantic color and outgoing edges the outgoing color. Path highlighting uses the interaction accent. Neutral surfaces remain grayscale.

Search resolves/selects existing nodes only. Filters hide existing nodes/relations only. Path highlighting runs deterministic BFS over the currently loaded directed edges. The inspector renders labels/properties/evidence as text, not HTML.

No automatic/persistent motion. Dragging/zooming is user-driven. Changing layout/filter may redraw instantly. Respect `prefers-reduced-motion` and visible keyboard focus.
