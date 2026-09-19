#!/usr/bin/env node
/*
Legacy compatibility shim. The portable implementation is generate_benchmark_report.py.
This wrapper requires Node only when callers explicitly use the legacy .js entrypoint.
*/
const { spawnSync } = require('child_process');
const path = require('path');

const script = path.join(__dirname, 'generate_benchmark_report.py');
const candidates = [];
if (process.env.PYTHON) candidates.push({ cmd: process.env.PYTHON, prefix: [] });
candidates.push(
  { cmd: 'python3', prefix: [] },
  { cmd: 'python', prefix: [] },
  { cmd: 'py', prefix: ['-3'] },
);

for (const candidate of candidates) {
  const result = spawnSync(candidate.cmd, [...candidate.prefix, script, ...process.argv.slice(2)], { stdio: 'inherit' });
  if (!result.error || result.error.code !== 'ENOENT') {
    process.exit(result.status == null ? 1 : result.status);
  }
}

console.error('No Python 3 launcher found. Use the portable generate_benchmark_report.py entrypoint through your host\'s Python 3.10+ execution method.');
process.exit(2);
