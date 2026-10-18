# Changelog

## [0.1.0] - 2026-10-18

First tracked version of the previously unversioned installed skill; previous release history is unknown.

- Adds HTTP alternate-path safety and load-amplification checks and identifies unsafe-method retry defaults for Microsoft.Extensions.Http.Resilience.
- Keeps the .NET 10/C# 14 default and existing version/lockfile policy, with a shorter (<500-character) discovery description.
- No new dependencies, execution tools or host-specific requirements.

- Normalizes the optional OpenAI adapter product values to supported `CHAT`/`CODEX`, without changing host-neutral instructions.

No host-specific runtime is required by the portable core. Structural validation does not prove observed production resilience.
