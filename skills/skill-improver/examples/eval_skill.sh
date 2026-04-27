#!/usr/bin/env bash
set -euo pipefail

# Minimal custom evaluator example. Prefer --evaluator skill-benchmark when available.
# Run from the target skill folder.

score=0
[[ -f SKILL.md ]] && score=$((score + 30))
[[ -d references ]] && score=$((score + 20))
[[ -d scripts ]] && score=$((score + 20))
grep -qi "validation\|gate\|benchmark\|test" SKILL.md && score=$((score + 30))

status="pass"
if [[ ! -f SKILL.md ]]; then
  status="fail"
fi

printf '{"score": %s, "status": "%s", "gates": {"skill_md": "%s"}}\n' "$score" "$status" "$status"
