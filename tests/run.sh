#!/bin/sh
# Run dependency-free tooling tests, then Arturo smoke tests when a runtime exists.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m py_compile scripts/arturo_help.py mcp/server.py

ARTURO_BIN=${ARTURO_BIN:-arturo}
if command -v "$ARTURO_BIN" >/dev/null 2>&1; then
    actual=$(mktemp)
    trap 'rm -f "$actual"' EXIT HUP INT TERM
    "$ARTURO_BIN" --no-color tests/smoke.art > "$actual"
    diff -u tests/expected-smoke.txt "$actual"
else
    echo "SKIP: Arturo runtime not found; runtime smoke test was not run." >&2
fi
