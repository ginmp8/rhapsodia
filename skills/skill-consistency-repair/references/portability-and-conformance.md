# Portability and Conformance

Keep three claims separate.

## 1. Portable-core/spec conformance

Evaluate the host-neutral Agent Skills package contract: root `SKILL.md`, portable frontmatter, package-local resources, safe relative paths, and target-owned contract gates. Internal static checks and external reference validators are evidence for this claim.

A reference validator is supplemental. Its success does not prove package-wide ownership, semantic consistency, validator equivalence, runtime behavior, or packaging integrity.

## 2. Host compatibility

Host compatibility is a separate claim about a concrete client/runtime profile. A host may tolerate a portable-core violation or add optional metadata/discovery behavior. Such tolerance never converts a portable-core failure into conformance.

Report each requested host independently as `pass`, `pass-with-warnings`, `fail`, `not-run`, `blocked`, or `not-proven`. Preserve `agents/openai.yaml` and other host adapters as optional adapters unless the user explicitly asks to normalize them.

## 3. Runtime behavior

Runtime/tool behavior requires executed evidence in that environment. Static conformance is not runtime proof.

## Multi-platform rule

Core correctness must not depend on vendor-private tool names, fixed installation paths, one shell, one path separator, or one host adapter. Use package-relative paths and standard-library filesystem APIs. Before packaging, reject casefold/Unicode-normalization path collisions that can collapse on common case-insensitive or Unicode-normalizing filesystems.
