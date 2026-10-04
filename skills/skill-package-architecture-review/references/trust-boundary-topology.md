# Trust Boundary Topology

**Contract version:** 1.0.0

Use when package architecture depends on executable resources, filesystem mutation, external tools, network access, host permissions, provenance, or another authority boundary.

This reference owns **architectural topology**, not a vulnerability audit. Hand detailed security analysis to the relevant security-review capability.

## Map the topology

Record only observed/declared evidence for:

- executable scripts/binaries and how they are invoked;
- network requirements or remote services;
- filesystem read/write scope;
- external tools, package managers, MCP/connectors, or subprocess dependencies;
- host-specific adapters/permission metadata;
- source/provenance or trust assumptions when supplied;
- secrets/credentials surfaces without opening or reproducing secret values.

Use `unknown` when a required surface cannot be inspected.

## Architectural questions

Ask whether:

- one mode requires materially stronger authority than the rest;
- a host adapter is optional metadata or a semantic runtime dependency;
- trusted and untrusted inputs/resources cross the same execution boundary;
- a proposed split/router would actually isolate authority or merely move files;
- a portable core can remain understandable when host-specific permission metadata is ignored.

Different privilege levels are a separation signal only when they create a real authority/safety boundary that cannot be governed clearly within one package.

## Security handoff

Trigger a security handoff when the conclusion depends on vulnerability analysis, secret handling, injection/command/path traversal, dependency/supply-chain risk, authorization, sandbox escape, or detailed threat modeling.

The handoff should include:

1. exact package/evidence identity already inspected;
2. executable/network/permission surfaces observed;
3. the specific architecture question or suspected security boundary;
4. protected paths and evidence gaps;
5. the acceptance question to return to architecture review.

Do not label a package secure because its topology is clean, and do not label executables unsafe merely because they exist.
