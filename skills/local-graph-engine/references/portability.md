# Capability-based portability

## Core runtime
One canonical skill directory; no host-specific semantic fork. Resolve Python 3.10+ as python, python3, py -3 or the host's actual executable. Use package-relative resources and resolved data paths. Core Python helpers use only stdlib; optional libraries are never installed implicitly. Browser output needs a modern browser with SVG/JavaScript, not Node, a bundler or an external application.

## Host capabilities, not brand promises
| Available capability | Supported outcome |
|---|---|
| Read source + command execution + writable filesystem | Run local scripts, create/query DB or render HTML as permitted. |
| Read source + no command execution | Discuss/model data; produce a proposed JSON contract; no executed DB/view claim. |
| Browser/runtime test capability | Verify the generated UI in that runtime and report method/limits. |
| MCP subprocess launch | Optional local read-only query tool; host-specific configuration is external. |
| Ephemeral chat sandbox | Deliver files before session expiry; persistence requires an actual saved/exported artifact. |

A cloud chat does not acquire access to a user's local drive merely because a skill is installed. Copy/upload approved inputs or use a supported authorized tool. Do not promise identical availability in every chat, IDE or OS.
Portable structure targets OpenAI/ChatGPT, Codex, Claude, Copilot and Cursor semantics. These are compatibility targets, not certificates of executed clients. Optional agents/openai.yaml is UI metadata only. Client discovery paths and permission policies vary and should be checked against that client's official documentation when installing.

## Optional dependency policy
Select the smallest useful installed open-source capability; record its exact runtime version, inputs and configuration. Missing capabilities must yield an explicit limitation or a supported alternative, not hidden network downloads. Model weights and native compiler/codec dependencies may have independent licenses. A source package for an optional adapter is not a universal prebuilt binary.
