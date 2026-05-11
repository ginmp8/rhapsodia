# Prompt scenarios

## Should activate

- "Audit this skill package and create missing validator tests."
- "Run the build, tests, and lint for this validator script package and fix failures with minimal changes."
- "Create a phased test plan for the scripts in this skill."
- "Generate pytest coverage for `scripts/discover_commands.py` and run the tests."
- "Classify this CI log and tell me whether it is a build, test, lint, environment, or configuration failure."
- "Fix this packaging validator failure, but do not touch fixtures or expected outputs."
- "Produce a validation report with commands, exit codes, changed files, and remaining risks."

## Should not activate

- "Implement a new account-opening feature."
- "Write product release notes for this roadmap item."
- "Do a security review for leaked API keys."
- "Create a stakeholder governance report."
- "Rewrite this README for clarity" unless the README is part of test/validator command evidence.

## Ambiguous prompts

- "Improve this skill."  
  Activate only if the improvement request is about tests, validators, build/test/lint commands, runners, or validation gates. Otherwise use a general skill hardening workflow.

- "Fix this script."  
  Activate if the script is a test, validator, runner, linter, packager, benchmark helper, or command-discovery utility. Otherwise use a code implementation/review workflow.

- "Make CI pass."  
  Activate for build/test/lint/validator failures. Refuse or escalate destructive deploy, release, credential, or infrastructure changes outside test validation scope.

## Common failure prompts

- "Tests fail after generated test phase 2; here is the log."  
  Expected behavior: classify the failure, identify whether the generated tests misunderstood source behavior, patch minimally, rerun the same command when possible.

- "The linter changed 200 files."  
  Expected behavior: stop broad formatting, revert or avoid unrelated files when possible, use scoped formatting for touched files only.

- "The validator fails because expected output differs."  
  Expected behavior: do not edit expected output without explicit authorization; verify whether code or test is wrong.

- "pytest is not installed."  
  Expected behavior: classify as environment unless dependency installation is authorized; use static checks as fallback.
