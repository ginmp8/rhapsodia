# Scanner Contract

## Purpose

The bundled scanners are deterministic supporting detectors. They increase coverage but do not prove credential validity and do not establish final review severity without semantic context.

## Working-tree scanner

`scripts/scan_secrets.py` accepts exactly one existing file or directory.

### Input and traversal

- resolve the target root once;
- do not follow symbolic-link files/directories outside the scan root;
- traverse directory/file names in canonical lexical order;
- scan supported text-like files, including supported text files under common `build`, `dist`, `bin`, `obj`, and `target` output directories;
- continue to ignore dependency/VCS/runtime caches such as `.git`, `node_modules`, and virtual environments;
- skip over-size/read-error candidates and report them;
- unsupported/binary formats remain outside proof of completeness.

### Detection invariants

- scan all non-overlapping relevant matches, including multiple matches from the same rule on one line;
- stable finding IDs include source location plus match occurrence so same-line matches do not collide;
- provider/pattern matches may carry stronger detector confidence, but generic entropy does not raise final severity;
- generic assignments remain provisional candidates and require semantic review;
- scanner output always redacts matched credential material.

### JSON contract v1

Top level:

- `schema_version`: `1`
- `status`: `complete | partial`
- `target`
- `summary`: detector severity-hint counts
- `scan_stats`: considered/scanned/skipped/finding counts
- `skipped`: path + stable reason
- `findings`: stable redacted candidates

Finding fields remain:

`id, path, line, severity, confidence, rule, evidence`

The scanner `severity` field is a **provisional detector hint**, not final review severity. The semantic reviewer must recalculate final severity using `security-policy.md`.

Stable skip reasons:

`symlink | unsupported-type | too-large | read-error`

`complete` means no supported working-tree text candidate was skipped after discovery. It does not include Git history, remote logs, container images, unsupported binaries, or external systems.

## Git history scanner

`scripts/scan_git_history.py` requires a readable Git repository and Git CLI. It scans added patch lines reachable from the requested revision set (default `--all`) and reuses the redacted detector rules.

History JSON fields:

- `schema_version`: `1`
- `status`: `complete`
- `scope`: `git-history`
- `target`
- `revision`: requested revision expression
- `summary`
- `scan_stats`: commits/files/added-lines/findings
- `findings`: `id, commit, path, line, severity, confidence, rule, evidence`

A history scan covers Git patch text reachable from the requested refs. It does not prove absence from unavailable objects, deleted remote refs, external forks/clones, Git LFS object stores, binary blobs, or hosting-platform collaboration surfaces.

## Redaction invariant

No scanner or validator output may reproduce full provider tokens, bearer values, password-bearing URIs, assignment values, or private-key payloads. Private-key markers may be reported; payload material must not be copied.

## Ordering

Working-tree findings:

`severity hint desc -> path -> line -> rule -> id`

History findings:

`severity hint desc -> commit -> path -> line -> rule -> id`

## Durable output

When `--output` is used, write a temporary sibling and atomically replace only after serialization succeeds. Reject symbolic-link outputs and aliases with the single-file input. Failure must not overwrite an existing good output.
