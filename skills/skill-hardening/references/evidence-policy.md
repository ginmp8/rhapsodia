# Evidence Policy

## Evidence order

1. Exact target package/current filesystem.
2. User constraints, failed prompts, prior outputs, benchmark/harness evidence.
3. Repository/domain truth or official docs for external tools/formats.
4. Current primary specification/vendor docs for skill format, security, portability, packaging, or runtime behavior.
5. Independent research/production evidence for trade-offs and emerging risks.
6. Model judgment only for bounded prioritization/semantic interpretation, never sole proof of an objective gate.

## Research-backed mutation

Research only concrete gaps. When research materially changes a skill, preserve a bounded corpus/result and trace material evidence through:

`source -> atomic finding -> disposition -> requirement -> change -> evaluation`

Account for every material finding as `implement`, `already-covered`, `rejected`, `not-applicable`, `uncertain`, or `conflict`. Require reverse justification for each substantive change. Mechanically complete links do not prove semantic truth; independently review whether the source supports the finding, the finding supports the requirement, the change satisfies it, and the evaluation can falsify it.

Claim only corpus-bounded completeness (for example, “100% of recorded findings were dispositioned”), never universal research completeness unless an external research method separately proves it.

## Claim vocabulary

- `measured`: executed in this run or supplied as exact execution evidence;
- `observed`: direct inspection;
- `derived`: deterministic calculation from evidence;
- `supplied`: user-provided result not independently rerun;
- `planned`: defined but unexecuted;
- `blocked`: required evidence unavailable.

Scenario definitions, structural scores, and plausible reasoning do not become measured behavioral evidence.

## Freshness and identity

Snapshot exact mutable local/repository evidence when it materially determines a decision. For live web evidence, preserve the research artifact plus URL/date/version metadata. If material source identity changes, continue against the frozen evidence or explicitly re-baseline; never mix revisions silently.
