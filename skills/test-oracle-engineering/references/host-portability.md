# Host Portability

Keep the Agent Skills package as the canonical semantic core. Host-specific metadata is optional.

Target profiles for structural portability: `portable-core`, OpenAI/ChatGPT, Codex, Claude, GitHub Copilot/VS Code, and Cursor. Visual Studio or other hosts may consume the same semantics when they expose the required capabilities.

Capability model:

- `read-context`: inspect source, tests, contracts, and supplied evidence;
- `write-verification-artifacts`: create/edit only authorized tests/fixtures/evidence;
- `run-bounded-process`: execute the exact selected test/build/validator command;
- `artifact-delivery`: optional receipt/file delivery.

If a required capability is unavailable, degrade only to a less powerful mode: execution -> design/review. Never report runtime proof from structural compatibility.
