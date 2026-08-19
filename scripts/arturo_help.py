#!/usr/bin/env python3
"""Resolve Arturo docs and optionally ask a local runtime for authoritative help."""
from __future__ import annotations
import argparse, csv, os, pathlib, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "references" / "library-index.csv"
CONCEPTS = {
    "string interpolation": ["render", "print", "express"],
    "loop": ["loop", "while", "until", "map", "select", "fold"],
    "list comprehension": ["map", "select", "collect"],
    "dictionary": ["dictionary", "get", "set", "keys", "values", "key?"],
    "file": ["read", "write", "exists?", "file?", "relative", "absolute"],
    "http": ["request", "download", "read", "serve"],
    "json": ["parse", "to"],
    "error": ["try", "throw", "ensure", "panic"],
    "type": ["type", "to", "define", "is", "conforms?"],
}
ALIASES = {"++": "append", "--": "remove", "+": "add", "-": "sub", "*": "mul",
           "/": "div", "//": "fdiv", "%": "mod", "^": "pow", "=": "equal?",
           "<": "less?", ">": "greater?", "=<": "lessOrEqual?", ">=": "greaterOrEqual?",
           "<>": "notEqual?", "..": "range", "@": "array", "#": "dictionary",
           "$": "function", "~": "render", "<<": "read", ">>": "write", "??": "coalesce"}

def rows():
    with INDEX.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def search(query: str):
    q = query.strip().lower()
    q = ALIASES.get(query.strip(), q).lower()
    allrows = rows()
    exact = [r for r in allrows if r["name"].lower() == q]
    if exact: return exact
    targets = CONCEPTS.get(q, [])
    if targets:
        rank = {n:i for i,n in enumerate(targets)}
        found = [r for r in allrows if r["name"] in rank]
        return sorted(found, key=lambda r: rank[r["name"]])
    return [r for r in allrows if q in r["name"].lower() or q in r["module"].lower()]

def runtime_info(symbol: str, runtime: str) -> int:
    exe = shutil.which(runtime) if not pathlib.Path(runtime).exists() else runtime
    if not exe:
        print(f"runtime not found: {runtime}", file=sys.stderr)
        return 127
    code = "info '" + symbol
    cp = subprocess.run([str(exe), "--no-color", "-e", code], text=True)
    return cp.returncode

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("query", help="function, operator alias, module, or concept")
    p.add_argument("--latest", action="store_true", help="print latest/nightly URL")
    p.add_argument("--info", action="store_true", help="also run runtime `info`")
    p.add_argument("--runtime", default=os.environ.get("ARTURO_BIN", "arturo"),
                   help="runtime executable (default: $ARTURO_BIN or PATH lookup for arturo)")
    p.add_argument("--limit", type=int, default=20)
    a = p.parse_args()
    found = search(a.query)
    if not found:
        print("No indexed match. Try a shorter term; then inspect resources.md/source.", file=sys.stderr)
        return 1
    for r in found[:a.limit]:
        if a.latest and r.get("latest_http_status") != "200":
            url = r["stable_url"]
            note = f"\tlatest={r.get('latest_http_status', 'unverified')}; stable fallback"
        else:
            url = r["latest_url"] if a.latest else r["stable_url"]
            note = ""
        print(f"{r['name']}\t{r['module']}\t{url}{note}")
    if len(found) > a.limit:
        print(f"... {len(found)-a.limit} more matches", file=sys.stderr)
    if a.info:
        symbol = a.query.strip()
        # For concepts/modules, use first concrete function. Keep aliases for runtime alias lookup.
        if symbol.lower() in CONCEPTS or not any(r["name"].lower() == ALIASES.get(symbol, symbol).lower() for r in found):
            symbol = found[0]["name"]
        print(f"\n--- runtime: info '{symbol} ---")
        return runtime_info(symbol, a.runtime)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
