#!/bin/sh
# Optional POSIX adapter. Core behavior does not require this shell.
set -eu
case "$0" in /*) script=$0 ;; *) script=$PWD/$0 ;; esac
dir=$(CDPATH= cd -P "$(dirname "$script")" && pwd)
probe='import sys; sys.exit(2) if sys.version_info < (3,10) else print(sys.executable)'
python_path=''
if [ -n "${RHAPSODIA_PYTHON:-}" ]; then
  if [ ! -x "$RHAPSODIA_PYTHON" ]; then
    printf '%s\n' 'RHAPSODIA_PYTHON must name an executable file.' >&2
    exit 127
  fi
  python_path=$("$RHAPSODIA_PYTHON" -I -S -c "$probe") || exit 2
else
  for candidate in python3 python; do
    located=$(command -v "$candidate" 2>/dev/null || true)
    [ -n "$located" ] || continue
    if python_path=$("$located" -I -S -c "$probe" 2>/dev/null); then
      break
    fi
    python_path=''
  done
fi
if [ -z "$python_path" ]; then
  printf '%s\n' 'Python 3.10+ unavailable. Set RHAPSODIA_PYTHON to a trusted interpreter. Nothing was installed.' >&2
  exit 127
fi
exec "$python_path" -I -S -B "$dir/runtime.py" "$@"
