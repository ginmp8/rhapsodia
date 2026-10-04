# Host Portability

Keep the Agent Skills package as the canonical semantic core. Host-specific metadata is optional.

Target profiles: `portable-core`, OpenAI/ChatGPT, Codex, Claude, GitHub Copilot/VS Code, Cursor, and compatible Visual Studio/other hosts that expose the needed capabilities.

Capability model:

- `read-context`: inspect source, tests, contracts, and supplied evidence;
- `write-verification-artifacts`: create/edit only authorized tests/fixtures/evidence;
- `run-bounded-process`: execute the exact selected test/build/validator command;
- `hash-or-identify-candidate`: obtain an immutable revision, supplied identity, or deterministic local tree digest;
- `artifact-delivery`: optional receipt/file delivery.

The bundled validators use only the Python standard library. Do not require Bash, a fixed Python executable spelling, vendor-private agent APIs, or host-specific repository paths. Resolve an available Python 3 launcher as a capability.

If a required capability is unavailable, degrade only to a less powerful mode: execution -> design/review. A host can validate artifact shape without strict runtime proof; never report structural compatibility as executed proof.
