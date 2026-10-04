# Language clarity and global readiness

Use this reference for DQ-09 or when the audience spans teams, locales, language proficiency levels, or translation/localization workflows. Apply the clarity rules broadly; apply global-readiness rules only when audience/context makes them relevant.

## Clarity and terminology

Check that:

- one concept uses one preferred term unless a distinction is intentional;
- pronouns and vague references have clear antecedents;
- conditions appear before dependent actions when order affects execution;
- modal words (`must`, `should`, `may`) match the actual contract;
- sentences separate distinct technical claims when combining them creates ambiguity;
- acronyms are expanded when the intended audience may not know them;
- established domain terms are preserved rather than simplified into less precise synonyms.

Do not use readability formulas, sentence length, or vocabulary rarity as hard correctness gates unless the target explicitly owns such a threshold. They may be supporting heuristics only.

## Global-readiness overlay

When relevant, prefer:

- unambiguous dates, times, units, and number formats;
- consistent terminology, capitalization, and formatting;
- literal wording over idioms, slang, humor, or culture-specific metaphors;
- text labels instead of directional phrases such as "on the right" when location is not semantically stable;
- examples that do not depend on one geography or culture unless the domain requires it.

Global readiness does not require removing legitimate locale- or jurisdiction-specific content. Scope it explicitly instead.

## Translation and localization boundary

Do not claim that documentation is translation-ready merely because English prose is simple. Actual localization may depend on product strings, UI labels, units, legal requirements, screenshots, and target-language review that are outside the documentation file.
