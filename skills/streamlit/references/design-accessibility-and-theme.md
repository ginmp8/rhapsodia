# Design, Accessibility, and Theme

## Native-first order

Prefer:

`native Streamlit element -> theme/config API -> supported component API -> custom CSS/HTML/JS`

Custom CSS against internal DOM selectors is fragile across Streamlit releases. Use it only when the user explicitly needs styling that native/theme APIs cannot express.

## Theme

Use `.streamlit/config.toml` and supported theme APIs for palette, typography, radii, and other appearance settings. When a component is used, consume Streamlit theme variables rather than hard-coding separate light/dark palettes when possible.

## Layout

Prefer semantic containers, bordered grouping, and responsive horizontal layouts when supported. Use columns for fixed grids/ratios, not every row of actions. Keep slow output positions stable so reruns do not unnecessarily reset stateful elements.

## Labels and icons

Use meaningful labels and sentence casing. Do not use empty widget labels; hide/collapse a real label when the surrounding UI supplies context. Prefer supported Material Symbols/icons over emoji-heavy navigation/control chrome when appropriate.

## Accessible content

Use short, specific `alt=`/accessible names where the resolved API supports them. Keep headings hierarchical, do not encode meaning only with color, and preserve readable contrast in custom themes.

## Custom HTML

Do not recreate native Streamlit widgets in HTML. For static trusted markup, use the least-powerful supported surface. For interactive custom behavior, use Components v2 rather than script injection into ordinary Markdown/HTML.
