# Host Portability

## Portable core

Use the Agent Skills-compatible package as the semantic source of truth. The core must remain valid when copied between compatible hosts.

Do not require:

- a vendor-private tool-call name;
- a specific model family;
- a fixed install directory;
- Bash/POSIX semantics;
- network access;
- a host-specific metadata file.

Describe capabilities instead: read files, write files, execute a process, access current sources, invoke another specialist, or deliver an artifact.

## Host profiles

The same core is intended for:

- OpenAI/ChatGPT skill hosts;
- Codex Agent Skills;
- Claude Agent Skills;
- GitHub Copilot Agent Skills;
- Cursor Agent Skills;
- other Agent Skills-compatible hosts.

`agents/openai.yaml` is an optional OpenAI UI adapter. Other hosts may ignore it safely.

A host without command execution can still apply the semantic contract but cannot claim the Python validator ran. A host without web/connectors can still decide from supplied evidence, but must use `blocked` or `undetermined` when missing current evidence is material.

Structural portability does not prove identical behavioral routing across different models. Report runtime/model behavior separately when actually measured.
