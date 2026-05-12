# Source Hygiene and License Safety

## Source hierarchy

Use this hierarchy for Streamlit facts:

1. Official Streamlit documentation and official Streamlit repositories.
2. User-provided app files, repo files, logs, and deployment config.
3. Official documentation of connected libraries such as pandas, SQLAlchemy, Plotly, Altair, Docker, or the deployment platform.
4. Community examples only as inspiration, not source of truth.
5. Model memory only for stable general patterns, never for version-sensitive claims.

## Clean-room rule

When replacing a copied or license-unclear skill:

- Do not preserve the old wording.
- Do not preserve the old reference-file structure solely because it existed upstream.
- Do not paste scraped documentation blocks.
- Rebuild with original summaries, examples, decision trees, validation contracts, and links to official sources.
- If a capability is important, re-express it as a workflow or checklist rather than a copied paragraph.

## Attribution pattern

For a public Apache-licensed repo, include a short attribution note rather than bundling large external docs:

```markdown
This skill uses original guidance written for this package and points to official Streamlit documentation and repositories for source truth. Streamlit itself and its official docs are maintained by the Streamlit project; verify exact API details at https://docs.streamlit.io when version precision matters.
```

## Copy-risk checklist

Before publishing a skill:

- Is any file identical or nearly identical to a third-party skill file?
- Are large documentation excerpts copied instead of summarized?
- Does the upstream repo have a clear license permitting redistribution?
- Does the target repo license match the source license obligations?
- Are attributions preserved where required?
- Does the package include only what is necessary for the skill to work?

## Safe rewrite strategy

1. Identify the user-visible capabilities that must be preserved.
2. Discard old text and write a new control plane.
3. Replace bulk docs with topic-specific guides and decision tables.
4. Write original examples using generic data and placeholders.
5. Add validation scripts and eval scenarios.
6. Add an attribution/source note.
7. Package and inspect the zip for accidental old files.

## When to delete instead of rewrite

Delete or exclude content when:

- the source license is absent or unclear;
- the file is a large copied documentation dump;
- the file is not needed for execution;
- the same value can be provided as a link plus original summary;
- maintaining it would create attribution or update burden.

## Public-repo caution

A public GitHub repo without an explicit open-source license is not automatically MIT, Apache, or public domain. Treat such content as viewable but not broadly reusable unless permission is granted.
