# Source and License Notes

## Purpose

Keep the Streamlit skill useful without copying a third-party skill package whose license is unclear. This file records source policy, attribution, and safe update rules.

## Official sources

Use these as the preferred source references:

- Streamlit documentation repository: https://github.com/streamlit/docs
- Streamlit source repository: https://github.com/streamlit/streamlit
- Streamlit public docs: https://docs.streamlit.io
- Streamlit component gallery: https://streamlit.io/components

The Streamlit docs repository and Streamlit source repository include Apache License 2.0 license files. This skill is an original synthesis and operational guide derived from official Streamlit concepts, public APIs, and common application patterns.

## What is allowed

- Reference official documentation URLs.
- Summarize and reorganize official docs into task-oriented guidance.
- Write original examples that demonstrate API usage.
- Include short names of public Streamlit commands such as `st.button`, `st.cache_data`, and `st.session_state`.
- Attribute official sources when making source or license claims.

## What is not allowed

- Copy a third-party skill package verbatim or near-verbatim.
- Preserve a third-party skill's exact section order, wording, examples, or generated documentation dump when the license is unclear.
- Claim this package is byte-identical or derived from a third-party skill.
- Copy large blocks from official docs when a synthesized explanation would work.

## Update workflow

1. Prefer official docs and official source code as source truth.
2. Rewrite guidance for ChatGPT's job: code generation, debugging, review, tests, deployment, and safety.
3. Keep `SKILL.md` as a router/control plane. Put depth in `references/`.
4. Add official URLs near concepts and commands so future maintainers can verify details.
5. Validate with `scripts/validate_streamlit_skill.py` and package with `scripts/package_skill.py`.
6. When exact API signatures matter, open official docs before finalizing code.

## Apache 2.0 redistribution hygiene

If distributing this skill in an Apache-2.0 repository, retain license notices in the repository root and keep this attribution file. If copying any material from official Streamlit repositories beyond short factual names or URLs, preserve required notices and document the change.
