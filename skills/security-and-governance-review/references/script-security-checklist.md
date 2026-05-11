# Script Security Checklist

Use this checklist for `script-security-review`.

## Dangerous execution patterns

Inspect for:

- `shell=True`, `os.system`, `popen`, `eval`, `exec`, backticks, unquoted shell variables, and command string concatenation.
- `curl | sh`, `wget | bash`, remote install scripts, implicit package manager lifecycle hooks, and unverified downloads.
- Broad destructive commands such as `rm -rf`, `del /s`, `Remove-Item -Recurse -Force`, `git clean -fdx`, or deletion based on user-controlled paths.
- Running generated code, test fixtures, package hooks, or validators from untrusted inputs.
- Missing timeouts on subprocesses and network calls.
- Commands that mutate `.git`, credentials, local env files, expected outputs, or benchmark fixtures.

## File handling and path safety

Inspect for:

- Path traversal from archive members, uploaded filenames, user-provided paths, or package metadata.
- Archive extraction with `extractall` or equivalents without canonical path checks.
- Symlink traversal, following links into blocked paths, and unsafe recursive copy/delete.
- Writes outside the declared target folder.
- Temporary files with predictable names or world-writable permissions.
- Packaging that accidentally includes `.git`, caches, old zips, reports, credentials, private keys, local env files, or generated evidence.

## Deserialization and parsing

Inspect for:

- `yaml.load` without a safe loader.
- Pickle, marshal, unrestricted json-to-object construction, dynamic imports, or plugin loading from untrusted files.
- Regex denial-of-service risks in validators used on large untrusted files.

## Safer patterns

- Prefer structured argument arrays over shell strings.
- Canonicalize paths and require every write/extract path to remain under the target directory.
- Deny symlink traversal unless explicitly required and validated.
- Use explicit exclusion lists for packaging and scanning.
- Use timeouts, nonzero exit handling, and dry-run modes for mutating scripts.
- Keep validators read-only unless their purpose is explicitly to write a report.
- Check archive contents before extraction.

## Validation probes

- Run syntax checks for modified scripts.
- Run safe scripts against a tiny fixture with a malicious path such as `../escape.txt` when applicable.
- Inspect package contents after zipping.
- Verify output redaction by feeding a fake token and confirming it is masked.
