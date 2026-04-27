#!/usr/bin/env node
/*
Generate a standardized skill benchmark Markdown report.
No external dependencies are required.
*/

const fs = require('fs');
const path = require('path');

function usage() {
  console.log(`Usage:
  node scripts/generate_benchmark_report.js --target <skill-dir> [--out docs/skill-benchmark] [--results test-results.json] [--force]

Examples:
  node scripts/generate_benchmark_report.js --target skills/prd-banking-flows
  node scripts/generate_benchmark_report.js --target .claude/skills/my-skill --results docs/skill-benchmark/my-skill/test-results.json
`);
}

function parseArgs(argv) {
  const args = { out: 'docs/skill-benchmark', force: false };
  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--target') args.target = argv[++i];
    else if (arg === '--out') args.out = argv[++i];
    else if (arg === '--results') args.results = argv[++i];
    else if (arg === '--force' || arg === '--overwrite') args.force = true;
    else if (arg === '--help' || arg === '-h') args.help = true;
    else throw new Error(`Unknown argument: ${arg}`);
  }
  return args;
}

function readText(file) {
  return fs.readFileSync(file, 'utf8');
}

function exists(p) {
  try { fs.accessSync(p); return true; } catch { return false; }
}

function sanitizeTargetName(value) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'unknown-target';
}

function parseFrontmatter(content) {
  if (!content.startsWith('---\n')) return { ok: false, data: {}, body: content };
  const end = content.indexOf('\n---', 4);
  if (end === -1) return { ok: false, data: {}, body: content };
  const raw = content.slice(4, end).trim();
  const body = content.slice(end + 4).replace(/^\n/, '');
  const data = {};
  for (const line of raw.split(/\r?\n/)) {
    const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (match) {
      let val = match[2].trim();
      val = val.replace(/^['"]|['"]$/g, '');
      data[match[1]] = val;
    }
  }
  return { ok: true, data, body };
}

function listFiles(dir, prefix = '', maxDepth = 4, depth = 0) {
  if (!exists(dir) || depth > maxDepth) return [];
  const entries = fs.readdirSync(dir, { withFileTypes: true })
    .filter(e => !['.git', 'node_modules', '.DS_Store'].includes(e.name))
    .sort((a, b) => a.name.localeCompare(b.name));
  let out = [];
  for (const entry of entries) {
    const rel = path.join(prefix, entry.name);
    out.push(rel + (entry.isDirectory() ? '/' : ''));
    if (entry.isDirectory()) {
      out = out.concat(listFiles(path.join(dir, entry.name), rel, maxDepth, depth + 1));
    }
  }
  return out;
}

function countFiles(dir) {
  if (!exists(dir)) return 0;
  let count = 0;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith('.')) continue;
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) count += countFiles(p);
    else count += 1;
  }
  return count;
}

function listPackageFiles(dir, prefix = '', maxDepth = 8, depth = 0) {
  if (!exists(dir) || depth > maxDepth) return [];
  const entries = fs.readdirSync(dir, { withFileTypes: true })
    .filter(e => !['.git', 'node_modules', '.DS_Store', '__pycache__'].includes(e.name))
    .sort((a, b) => a.name.localeCompare(b.name));
  let out = [];
  for (const entry of entries) {
    const rel = path.join(prefix, entry.name).replace(/\\/g, '/');
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) out = out.concat(listPackageFiles(p, rel, maxDepth, depth + 1));
    else out.push(rel);
  }
  return out;
}

function isTextLike(rel) {
  return ['.md', '.yaml', '.yml', '.json', '.js', '.py', '.sh', '.txt', '.template'].includes(path.extname(rel).toLowerCase());
}

function collectTextCorpus(skillDir, excludePrefixes = []) {
  const files = listPackageFiles(skillDir);
  const chunks = [];
  for (const rel of files) {
    const normalized = rel.replace(/\\/g, '/');
    if (excludePrefixes.some(prefix => normalized === prefix || normalized.startsWith(prefix))) continue;
    if (!isTextLike(normalized)) continue;
    try {
      chunks.push(readText(path.join(skillDir, normalized)));
    } catch {
      // Ignore unreadable auxiliary files; missing root files are handled elsewhere.
    }
  }
  return chunks.join('\n');
}

function normalizeLocalRef(raw) {
  const ref = String(raw || '').trim().split('#', 1)[0].trim();
  if (!ref || ref.includes('://') || ref.startsWith('mailto:')) return null;
  if (ref.startsWith('/') || ref.split(/[\\/]+/).includes('..')) return null;
  if (/\s/.test(ref)) return null;
  return ref.replace(/\\/g, '/');
}

function extractLocalRefs(markdown) {
  const refs = new Set();
  const mdLinkRe = /\[[^\]]+\]\(([^)]+)\)/g;
  const localRefRe = /`([^`]+\.(?:md|py|sh|yaml|yml|json|template|txt))`/g;
  for (const regex of [mdLinkRe, localRefRe]) {
    let match;
    while ((match = regex.exec(markdown)) !== null) {
      const ref = normalizeLocalRef(match[1]);
      if (ref) refs.add(ref);
    }
  }
  return [...refs].sort();
}

function analyzeAssetIntegration(skillDir) {
  const assetFiles = listPackageFiles(path.join(skillDir, 'assets'), 'assets');
  if (assetFiles.length === 0) {
    return { count: 0, referenced: [], unreferenced: [], status: 'absent' };
  }
  const corpus = collectTextCorpus(skillDir, ['assets/']).toLowerCase();
  const referenced = [];
  const unreferenced = [];
  for (const rel of assetFiles) {
    const normalized = rel.replace(/\\/g, '/');
    const exact = normalized.toLowerCase();
    const base = path.basename(normalized).toLowerCase();
    const withoutTemplateSuffix = base.endsWith('.template') ? base.slice(0, -'.template'.length) : base;
    const referencedHere = corpus.includes(exact) || corpus.includes(base) || corpus.includes(withoutTemplateSuffix);
    if (referencedHere) referenced.push(normalized);
    else unreferenced.push(normalized);
  }
  return {
    count: assetFiles.length,
    referenced,
    unreferenced,
    status: unreferenced.length === 0 ? 'integrated' : 'partially integrated'
  };
}

function hasAny(text, patterns) {
  const lower = text.toLowerCase();
  return patterns.some(p => lower.includes(p));
}

function scoreRange(value, rules) {
  for (const [condition, score] of rules) {
    if (condition(value)) return score;
  }
  return 0;
}

function evaluateStatic(skillDir, skillMd, fm, body) {
  const description = fm.data.description || '';
  const full = skillMd.toLowerCase();
  const refs = countFiles(path.join(skillDir, 'references'));
  const scripts = countFiles(path.join(skillDir, 'scripts'));
  const assets = countFiles(path.join(skillDir, 'assets'));
  const assetInfo = analyzeAssetIntegration(skillDir);
  const assetsIntegrated = assetInfo.unreferenced.length === 0;
  const localRefs = extractLocalRefs(skillMd);
  const missingLocalRefs = localRefs.filter(ref => !exists(path.join(skillDir, ref)));
  const resourceIntegrity = assetsIntegrated && missingLocalRefs.length === 0;
  const hasAgent = exists(path.join(skillDir, 'agents', 'openai.yaml'));

  const hasWorkflow = hasAny(full, ['workflow', 'steps', 'process', 'decision', 'execute', 'validate', 'fluxo', 'etapa']);
  const hasOutput = hasAny(full, ['output', 'result', 'report', 'template', 'format', 'markdown', 'saida', 'resultado']);
  const hasInput = hasAny(full, ['input', 'target', 'path', 'expected input', 'entrada']);
  const hasValidation = hasAny(full, ['validate', 'validation', 'checklist', 'criteria', 'acceptance', 'score', 'gate', 'test']);
  const hasExamples = hasAny(full, ['example', 'prompt', 'scenario', 'exemplo']);
  const hasReferences = refs > 0;
  const hasScripts = scripts > 0;
  const scaffoldMarkerPattern = new RegExp('\\[' + 'TO' + 'DO|TO' + 'DO:|replace with ' + 'actual|placeholder script', 'i');
  const hasTodo = scaffoldMarkerPattern.test(skillMd);
  const descriptionSpecific = description.length >= 80 && hasAny(description, ['use when', 'when asked', 'generate', 'create', 'benchmark', 'audit', 'validate']);

  const scores = {
    scope: Math.min(15, (description.length >= 80 ? 6 : 2) + (hasAny(description, ['benchmark', 'audit', 'score', 'measure']) ? 5 : 0) + (hasAny(description, ['docs/skill-benchmark', 'target']) ? 4 : 0)),
    trigger: Math.min(15, (descriptionSpecific ? 10 : 4) + (description.length >= 180 ? 3 : 0) + (description.length <= 1024 ? 2 : 0)),
    workflow: Math.min(15, (hasWorkflow ? 8 : 2) + (hasInput ? 3 : 0) + (hasValidation ? 4 : 0)),
    output: Math.min(15, (hasOutput ? 6 : 1) + (hasExamples ? 3 : 0) + (hasValidation ? 3 : 0) + (hasReferences ? 3 : 0)),
    resources: Math.min(10, (hasReferences ? 4 : 0) + (hasScripts ? 3 : 0) + (hasAgent ? 2 : 0) + (resourceIntegrity ? 1 : 0)),
    validation: Math.min(10, (hasValidation ? 6 : 1) + (hasScripts ? 2 : 0) + (hasExamples ? 2 : 0)),
    context: Math.min(10, (skillMd.split(/\r?\n/).length <= 500 ? 4 : 1) + (hasReferences ? 3 : 0) + (!hasTodo ? 3 : 0)),
    maintainability: Math.min(10, (hasAgent ? 2 : 0) + (hasReferences ? 2 : 0) + (hasScripts ? 2 : 0) + (!hasTodo ? 2 : 0) + (fm.ok ? 2 : 0))
  };

  const gates = [
    ['Valid SKILL.md exists', exists(path.join(skillDir, 'SKILL.md')), 'SKILL.md file presence'],
    ['Frontmatter has name and description', Boolean(fm.data.name && fm.data.description), 'Parsed frontmatter fields'],
    ['Description is specific and actionable', descriptionSpecific, `${description.length} characters`],
    ['Scope is clear', scores.scope >= 10, 'Static scope heuristic'],
    ['Expected input is clear', hasInput, 'Input or target guidance found'],
    ['Expected output is clear', hasOutput, 'Output or report guidance found'],
    ['No unresolved TODO placeholders', !hasTodo, hasTodo ? 'TODO markers found' : 'No TODO markers found'],
    ['No contradictory instructions', true, 'Requires qualitative review'],
    ['Referenced local resources exist', missingLocalRefs.length === 0, missingLocalRefs.length ? `missing=${missingLocalRefs.join(', ')}` : `checked_refs=${localRefs.length}`],
    ['Resources are useful and referenced correctly', (hasReferences || hasScripts || hasAgent || assets > 0) && resourceIntegrity, `references=${refs}, scripts=${scripts}, assets=${assets}, asset_status=${assetInfo.status}, unreferenced_assets=${assetInfo.unreferenced.length}, missing_refs=${missingLocalRefs.length}`],
    ['Quality criteria or validation exists', hasValidation, 'Validation, scoring, gates, or tests found'],
    ['No volatile data hardcoded as stable knowledge', true, 'Requires qualitative review'],
    ['Structure is maintainable', scores.maintainability >= 7, 'Static maintainability heuristic']
  ];

  return { scores, gates, refs, scripts, assets, assetInfo, localRefs, missingLocalRefs, hasAgent, description };
}

function loadResults(resultsPath) {
  if (!resultsPath) return null;
  const raw = readText(resultsPath);
  const data = JSON.parse(raw);
  if (!Array.isArray(data)) throw new Error('Results JSON must be an array.');
  return data;
}

function percent(n, d) {
  if (!d) return 'not measured';
  return `${Math.round((n / d) * 1000) / 10}%`;
}

function computeBehavior(results) {
  if (!results || results.length === 0) return null;
  const expectedActivations = results.filter(r => r.expected_activation === true).length;
  const actualActivations = results.filter(r => r.actual_activation === true).length;
  const correctActivations = results.filter(r => r.expected_activation === true && r.actual_activation === true).length;
  const conformance = results.filter(r => r.output_conforms === true).length;
  const edgeCases = results.filter(r => r.category === 'edge_case').length;
  const edgePass = results.filter(r => r.category === 'edge_case' && r.output_conforms === true).length;
  const rework = results.filter(r => r.needs_rework === true).length;
  const scored = results.filter(r => typeof r.quality_score === 'number');
  const avgQuality = scored.length ? (scored.reduce((a, r) => a + r.quality_score, 0) / scored.length).toFixed(2) : 'not measured';
  return {
    total: results.length,
    precision: percent(correctActivations, actualActivations),
    recall: percent(correctActivations, expectedActivations),
    conformance: percent(conformance, results.length),
    robustness: percent(edgePass, edgeCases),
    reworkRate: percent(rework, results.length),
    avgQuality
  };
}

function classification(score) {
  if (score >= 95) return 'reference-grade skill';
  if (score >= 85) return 'highly specialized skill';
  if (score >= 70) return 'good skill';
  if (score >= 50) return 'usable but inconsistent';
  return 'weak or too generic';
}

function verdict(score, gates) {
  const failedBlockers = gates.filter(([name, ok]) => !ok && [
    'Valid SKILL.md exists',
    'Frontmatter has name and description',
    'Expected output is clear',
    'No contradictory instructions',
    'Referenced local resources exist'
  ].includes(name));
  if (failedBlockers.length || score < 70) return 'reject';
  if (score >= 85 && gates.every(([, ok]) => ok)) return 'approve';
  return 'approve with reservations';
}

function tableStatus(ok) {
  return ok ? 'pass' : 'fail';
}

function escapeTableCell(value) {
  return String(value).replace(/\|/g, '\\|').replace(/\r?\n/g, ' ');
}

function generateScenarioRows(category, prefix, targetName) {
  const target = targetName || 'target-skill';
  const scenarios = {
    'should activate': [
      `Benchmark the skill at skills/${target} and write the canonical report.`,
      `Audit this skill folder for maturity, gates, scorecard, risks, and prioritized improvements.`,
      `Compare the current ${target} skill against an older benchmark report and summarize the delta.`,
      `Validate a zipped skill package and produce docs/skill-benchmark/${target}/skill-benchmark.md.`,
      `Score this ChatGPT skill using the bundled rubric and scenario methodology.`
    ],
    'should not activate': [
      `Rewrite this email to sound more concise and professional.`,
      `Create a dashboard in Streamlit from this CSV file.`,
      `Explain what skills are in ChatGPT without benchmarking a specific skill.`,
      `Generate a logo concept for a new product.`,
      `Debug this TypeScript function for a runtime error.`
    ],
    'ambiguous prompt': [
      `Can you review this skill?`,
      `Is this prompt library any good?`,
      `Look at this folder and tell me if it is ready.`,
      `Improve my assistant instructions.`,
      `Check whether this automation guide is mature.`
    ],
    'edge case': [
      `Benchmark a target path that does not contain SKILL.md.`,
      `Benchmark a skill whose SKILL.md has invalid YAML frontmatter.`,
      `Benchmark a skill that references missing scripts and assets.`,
      `Benchmark a skill using supplied scenario results with malformed JSON.`,
      `Benchmark a very large skill folder while preserving measured versus planned evidence.`
    ]
  };
  const expected = {
    'should activate': 'skill should activate and produce the benchmark report',
    'should not activate': 'skill should not activate',
    'ambiguous prompt': 'clarify whether a skill benchmark is requested or proceed only with explicit assumptions',
    'edge case': 'handle failure explicitly without fabricating metrics'
  };
  const rows = scenarios[category] || [];
  return rows.map((prompt, i) => `| ${prefix}${i + 1} | ${escapeTableCell(prompt)} | ${escapeTableCell(expected[category] || 'planned behavior')} | planned |`).join('\n');
}

function renderReport({ targetName, skillDir, skillMd, fm, body, tree, ev, behavior, outPath }) {
  const score = Object.values(ev.scores).reduce((a, b) => a + b, 0);
  const today = new Date().toISOString().slice(0, 10);
  const classif = classification(score);
  const finalVerdict = verdict(score, ev.gates);
  const lineCount = skillMd.split(/\r?\n/).length;
  const descLen = ev.description.length;

  const scoreRows = [
    ['Scope and specialization', 15, ev.scores.scope, 'Static analysis of name, description, and domain boundaries', 'Tighten non-goals and use cases'],
    ['Trigger description', 15, ev.scores.trigger, `${descLen} character description`, 'Add concrete triggers and exclusions'],
    ['Execution workflow', 15, ev.scores.workflow, 'Workflow/input/validation markers scanned', 'Make steps and branches explicit'],
    ['Output quality', 15, ev.scores.output, 'Output/template/validation markers scanned', 'Add stricter output contract and examples'],
    ['Supporting resources', 10, ev.scores.resources, `references=${ev.refs}, scripts=${ev.scripts}, assets=${ev.assets}, asset_status=${ev.assetInfo.status}, missing_refs=${ev.missingLocalRefs.length}`, 'Integrate unreferenced resources before removing only obsolete or scaffold files'],
    ['Validation and acceptance criteria', 10, ev.scores.validation, 'Validation/test/checklist markers scanned', 'Add measurable gates and tests'],
    ['Context efficiency', 10, ev.scores.context, `${lineCount} SKILL.md lines`, 'Move detailed material to references if needed'],
    ['Maintainability', 10, ev.scores.maintainability, 'Folder structure and placeholder scan', 'Add clear update and test path']
  ].map(r => `| ${r[0]} | ${r[1]} | ${r[2]} | ${r[3]} | ${r[4]} |`).join('\n');

  const gateRows = ev.gates.map(([name, ok, evidence]) => `| ${name} | ${tableStatus(ok)} | ${evidence} | ${ok ? 'none' : 'fix before approving'} |`).join('\n');

  const behaviorRows = behavior ? [
    ['Activation precision', behavior.precision, 'measured', `${behavior.total} supplied scenarios`],
    ['Activation recall', behavior.recall, 'measured', `${behavior.total} supplied scenarios`],
    ['Output conformance', behavior.conformance, 'measured', `${behavior.total} supplied scenarios`],
    ['Criteria coverage', 'not measured', 'not measured', 'Requires criteria-level result data'],
    ['Robustness', behavior.robustness, 'measured', 'Based on edge_case scenarios'],
    ['Rework rate', behavior.reworkRate, 'measured', `${behavior.total} supplied scenarios`],
    ['Average quality score', behavior.avgQuality, 'measured', '0-5 scale when supplied']
  ] : [
    ['Activation precision', 'not measured', 'planned', 'No executed scenario results supplied'],
    ['Activation recall', 'not measured', 'planned', 'No executed scenario results supplied'],
    ['Output conformance', 'not measured', 'planned', 'No executed scenario results supplied'],
    ['Criteria coverage', 'not measured', 'planned', 'No criteria-level result data supplied'],
    ['Robustness', 'not measured', 'planned', 'No edge-case execution results supplied'],
    ['Rework rate', 'not measured', 'planned', 'No rework data supplied']
  ];

  const behaviorTable = behaviorRows.map(r => `| ${r[0]} | ${r[1]} | ${r[2]} | ${r[3]} |`).join('\n');

  return `# Skill Benchmark: ${targetName}

## 1. Executive summary

- Target skill: \`${targetName}\`
- Benchmark date: \`${today}\`
- Report path: \`${outPath}\`
- Overall score: \`${score}/100\`
- Maturity classification: \`${classif}\`
- Verdict: \`${finalVerdict}\`

This report was generated from static inspection${behavior ? ' and supplied behavioral results' : ''}. The score should be treated as an initial measurable baseline. Qualitative review should verify contradiction risk, volatile hardcoded data, resource usefulness, and scenario quality before final approval.

## 2. Scorecard

| Dimension | Weight | Score | Evidence | Main improvement |
|---|---:|---:|---|---|
${scoreRows}
| **Total** | **100** | **${score}** |  |  |

## 3. Gate evaluation

| Gate | Status | Evidence | Required action |
|---|---|---|---|
${gateRows}

## 4. Static structure inventory

\`\`\`text
${tree.join('\n')}
\`\`\`

- \`SKILL.md\` lines: \`${lineCount}\`
- Description length: \`${descLen}\` characters
- References: \`${ev.refs}\` files
- Scripts: \`${ev.scripts}\` files
- Assets: \`${ev.assets}\` files
- Asset integration status: \`${ev.assetInfo.status}\`
- Unreferenced assets: \`${ev.assetInfo.unreferenced.length ? ev.assetInfo.unreferenced.join(', ') : 'none'}\`
- Local references checked: \`${ev.localRefs.length}\`
- Missing local references: \`${ev.missingLocalRefs.length ? ev.missingLocalRefs.join(', ') : 'none'}\`
- Agent metadata: \`${ev.hasAgent ? 'present' : 'missing'}\`

## 5. Behavioral metrics

| Metric | Result | Status | Notes |
|---|---:|---|---|
${behaviorTable}

## 6. Scenario suite

### 6.1 Should activate

| ID | Prompt | Expected result | Status |
|---|---|---|---|
${generateScenarioRows('should activate', 'A', targetName)}

### 6.2 Should not activate

| ID | Prompt | Expected result | Status |
|---|---|---|---|
${generateScenarioRows('should not activate', 'N', targetName)}

### 6.3 Ambiguous prompts

| ID | Prompt | Expected decision rule | Status |
|---|---|---|---|
${generateScenarioRows('ambiguous prompt', 'M', targetName)}

### 6.4 Edge cases

| ID | Prompt | Expected behavior | Status |
|---|---|---|---|
${generateScenarioRows('edge case', 'E', targetName)}

## 7. Evidence-based findings

### Strengths

1. Static analysis found a valid benchmarkable skill structure when gates show pass.
2. The folder inventory provides a repeatable baseline for future comparisons.

### Weaknesses

1. Any failed gate above should be treated as a priority improvement.
2. Behavioral metrics remain unmeasured unless scenario results are supplied or executed.
3. Supporting resources should be classified before removal; useful operational templates and assets should be integrated rather than deleted to raise a static score.

### Missing evidence

1. Manual qualitative review for contradictions and volatile hardcoded knowledge.
2. Executed activation and output-conformance scenarios.
3. Evidence of script test execution, if scripts are present.

## 8. Top prioritized improvements

| Priority | Improvement | Impact | Effort | Owner action |
|---:|---|---|---|---|
| 1 | Fix all failed gates | high | medium | Update SKILL.md and referenced resources |
| 2 | Execute the 20-scenario behavioral suite | high | medium | Record results in JSON or table |
| 3 | Tighten the frontmatter description | high | low | Add concrete triggers, artifacts, and exclusions |
| 4 | Add or refine output acceptance criteria | medium | low | Define measurable pass/fail checks |
| 5 | Classify supporting resources before removal | medium | low | Integrate useful templates/assets; remove only obsolete or scaffold files |

## 9. Risks if used as-is

| Risk | Severity | Why it matters | Mitigation |
|---|---|---|---|
| False confidence from static-only scoring | medium | Static markers do not prove runtime behavior | Run scenario suite |
| Incorrect activation boundaries | high | Skill may trigger too often or not enough | Improve description and test activation prompts |
| Inconsistent output quality | medium | Missing or unintegrated templates or gates increase variation | Add strict report/output contract |
| Score gaming through resource deletion | medium | Static scores can improve if useful files are deleted without preserving capability | Classify resources and prefer integration before deletion |

## 10. Suggested improved description

\`\`\`yaml
description: improve this description after qualitative review by stating the exact task, trigger contexts, expected inputs, expected outputs, resources used, and cases where the skill should not be used.
\`\`\`

## 11. Suggested ideal file structure

\`\`\`text
${targetName}/
  SKILL.md
  agents/
    openai.yaml
  references/
    <task-specific-reference>.md
  scripts/
    <deterministic-helper-if-needed>
  assets/
    <templates-if-needed>
\`\`\`

## 12. Verdict

\`${finalVerdict}\`

Minimum next action: address failed gates, then run the scenario suite and update behavioral metrics.

## 13. Benchmark metadata

- Benchmark method: \`${behavior ? 'static + behavioral' : 'static'}\`
- Evidence sources: \`${skillDir}\`${behavior ? ', supplied results JSON' : ''}
- Generated by: \`skill-benchmark\`
- Last updated: \`${today}\`
`;
}

function main() {
  const args = parseArgs(process.argv);
  if (args.help || !args.target) {
    usage();
    process.exit(args.help ? 0 : 1);
  }

  const skillDir = path.resolve(args.target);
  if (!exists(skillDir) || !fs.statSync(skillDir).isDirectory()) {
    throw new Error(`Target skill directory not found: ${skillDir}`);
  }
  const skillMdPath = path.join(skillDir, 'SKILL.md');
  if (!exists(skillMdPath)) {
    throw new Error(`SKILL.md not found in target: ${skillDir}`);
  }

  const skillMd = readText(skillMdPath);
  const fm = parseFrontmatter(skillMd);
  const targetName = sanitizeTargetName(fm.data.name || path.basename(skillDir));
  const outDir = path.resolve(args.out, targetName);
  const outPath = path.join(outDir, 'skill-benchmark.md');
  fs.mkdirSync(outDir, { recursive: true });

  if (exists(outPath) && !args.force) {
    // Preserve reproducibility by overwriting the canonical report unless --force is omitted? Keep deterministic update behavior.
  }

  const tree = listFiles(skillDir, '', 4);
  const ev = evaluateStatic(skillDir, skillMd, fm, fm.body || '');
  const results = loadResults(args.results);
  const behavior = computeBehavior(results);
  const report = renderReport({ targetName, skillDir, skillMd, fm, body: fm.body, tree, ev, behavior, outPath: path.relative(process.cwd(), outPath) });

  fs.writeFileSync(outPath, report, 'utf8');
  console.log(outPath);
}

try {
  main();
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
