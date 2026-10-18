# Portability and Evaluation

## At a Glance
- **Purpose:** Keep one Agent Skills core that can reason from supplied inputs across hosts with optional deeper execution capabilities.
- **Load when:** Installing in different agent hosts, designing evaluations, comparing results across runtimes, or operating without code tools.
- **Decision impact:** Controls capability fallbacks, evidence-level claims, activation tests, snapshot identity and whether repeatability is measurable.

## Capabilities, not host-name branches

The semantic core uses plain Markdown with only standard `name` and `description` frontmatter. No host-specific tools, absolute paths, symlinks, shell dialect, IDE metadata or external orchestration runtime are required. Distribution surfaces (VS Code, Visual Studio, Cursor, ChatGPT, Codex, Claude) may differ from semantic/runtime profiles; do not fork skill rules by IDE. When host-specific features matter, test them separately.

- With **repo read/search**, trace exact static evidence and cite code/config versions.
- With **runtime/test execution**, inspect authorization and side effects, run existing safe checks, capture environment and test results.
- With **graph/diagram support**, render only source-supported edges; text tables are the portable fallback.
- With **Python 3.10+**, optionally validate structured analysis and package via stdlib scripts.
- With **no file or execution capability**, use supplied snippets only, explicitly limit scope and mark validation `not-run`; do not fabricate a repository scan.

A moved/updated repo or configuration invalidates affected analysis results. Where possible pin VCS commit and record working-tree changes, tool/runtime versions and source-set identities. Paired trials require the same questions, source revision, execution environment and frozen evaluation contract; otherwise label comparisons `not-comparable`. Model wording and interpretations remain nondeterministic; structural JSON and package rules can be enforced mechanically.

## Evaluation tiers

1. **Structural:** `scripts/validate_skill.py` checks metadata, first-100 control plane, references, version/changelog and trace relations.
2. **Contract example:** `scripts/validate_analysis.py examples/sample-analysis.json`; and negative tests for broken sources/unsupported evidence upgrades.
3. **Scenario design:** `evals/activation-scenarios.json` and `evals/behavioral-scenarios.json` are *authored cases*, not executed agent-model results. Test realistic core, nontrigger, ambiguous, adversarial, async and missing-source cases on each chosen host when available.
4. **Outcome:** only compare real target-answer correctness, path coverage, invalid claims, time/tokens and calibration after executing a frozen suite with comparable environment and evaluator. No runtime or quantitative improvement claims without those observations.

## Reproducibility ceiling

Class: `research-analytic`. Deterministic aspects: metadata, typed statuses, source-ID references, package hashes, basic report shape. Model judgment remains necessary for deciding path relevance, completeness of alternative writers, source credibility, causal interpretation and valid counterexamples. Correctness requires inspection, not merely a passing validator.

## Safe stopping and ownership

No approval to mutate source is implied by skill activation. Keep generated JSON/reports separate from the inspected repo unless explicitly directed; ask permission before potentially destructive or production actions. Stop with explicit gaps if the repository is absent, if traversal cannot disambiguate a key dynamic dispatch, if source versions conflict, or if a universal-negative proof requires evidence beyond the available boundary.
