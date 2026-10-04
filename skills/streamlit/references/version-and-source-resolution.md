# Version and Source Resolution

## Purpose

Resolve Streamlit API behavior against the project that will run the code. Do not assume the newest public docs match the user's installed or pinned version.

## Evidence order

Use the strongest available evidence in this order:

1. repository lockfile or dependency declaration for the target project;
2. installed `streamlit.__version__` from the same runtime that will execute the app;
3. official agent guidance bundled inside that installed Streamlit package, when present;
4. `streamlit docs st.<command>` from that environment for exact public signatures/docstrings;
5. official documentation or source pinned to the resolved version/tag;
6. current release notes only when deciding whether an upgrade is useful.

A newer web page is not evidence that an older project supports the API. A local installation is not evidence that production uses the same version unless the environment identity matches.

## Deterministic resolver

When command execution is available:

```text
<PYTHON> scripts/resolve_streamlit_context.py --project-root <PROJECT> --json <OUT>
```

The resolver reports project dependency mentions, installed version/module location, bundled official Streamlit agent-skill path when present, and Streamlit CLI discovery. Treat the output as environment evidence, not as a compatibility guarantee.

## Exact API lookup

For a version-sensitive command, prefer the target environment:

```text
streamlit docs st.<command>
```

If that command is unavailable, consult official docs/source for the exact resolved version. Use `references/api-command-guide.md` only for broad discovery and topic routing.

## Upgrade decisions

Recommend an upgrade only after checking:

- requested feature minimum version;
- breaking/deprecated behavior between current and target versions;
- Python/dependency compatibility;
- deployment image or lockfile constraints;
- tests for touched state/rerun/component/server behavior.

Never silently write latest-version code into an older pinned project.

## Source conflicts

When installed docs, release notes, and live web docs disagree, state the conflict and prefer the evidence tied to the target runtime for implementation. Use current release notes for migration advice, not to overwrite project reality.
