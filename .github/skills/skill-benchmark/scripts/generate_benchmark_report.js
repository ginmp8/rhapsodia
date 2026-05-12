#!/usr/bin/env node
/* Compatibility wrapper for the legacy skill-improver default path. */

const fs = require('fs');
const path = require('path');

const self = fs.realpathSync(__filename);
const cwd = process.cwd();
const here = __dirname;

const candidates = [
  path.resolve(cwd, 'skills/skill-benchmark/scripts/generate_benchmark_report.js'),
  path.resolve(cwd, 'skill-benchmark/scripts/generate_benchmark_report.js'),
  path.resolve(here, '../../../../skills/skill-benchmark/scripts/generate_benchmark_report.js'),
  path.resolve(here, '../../../../skill-benchmark/scripts/generate_benchmark_report.js'),
  path.resolve(here, '../../../skill-benchmark/scripts/generate_benchmark_report.js'),
];

const target = candidates.find((candidate) => {
  if (!fs.existsSync(candidate)) {
    return false;
  }
  return fs.realpathSync(candidate) !== self;
});

if (!target) {
  console.error('Could not resolve skill-benchmark generator script.');
  for (const candidate of candidates) {
    console.error(`- ${candidate}`);
  }
  process.exit(1);
}

require(target);
