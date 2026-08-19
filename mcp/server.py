#!/usr/bin/env python3
"""Dependency-free MCP stdio server for Arturo help/search.

Implements the JSON-RPC methods needed for initialize, tools/list, tools/call,
ping, and notifications/initialized. Messages are newline-delimited JSON, as
used by MCP stdio transports. Logs go to stderr; stdout is protocol-only.
"""
from __future__ import annotations
import csv, json, os, pathlib, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "references" / "library-index.csv"
with INDEX.open(encoding="utf-8", newline="") as f:
    ROWS = list(csv.DictReader(f))

ALIASES = {"++":"append", "--":"remove", "+":"add", "-":"sub", "*":"mul",
           "/":"div", "//":"fdiv", "%":"mod", "^":"pow", "=":"equal?",
           "<":"less?", ">":"greater?", "=<":"lessOrEqual?", ">=":"greaterOrEqual?",
           "<>":"notEqual?", "..":"range", "@":"array", "#":"dictionary",
           "$":"function", "~":"render", "<<":"read", ">>":"write", "??":"coalesce"}

def matches(query: str, exact: bool = False):
    q = ALIASES.get(query, query).lower()
    if exact:
        return [r for r in ROWS if r["name"].lower() == q]
    return [r for r in ROWS if q in r["name"].lower() or q in r["module"].lower()]

def doc_line(r, channel="stable"):
    if channel == "latest" and r.get("latest_http_status") == "200":
        return r["latest_url"]
    suffix = " (latest unavailable; stable fallback)" if channel == "latest" else ""
    return r["stable_url"] + suffix

def arturo_info(args):
    symbol = str(args.get("symbol", "")).strip()
    if not symbol:
        raise ValueError("symbol is required")
    # Prevent source injection; info accepts a single symbol/literal.
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_?+*/%<>=!~|@#$^.-")
    if any(ch not in allowed for ch in symbol):
        raise ValueError("symbol contains unsupported characters")
    # Prefer the runtime bundled in this repo (bin/arturo); env override wins.
    bundled = ROOT / "bin" / "arturo"
    if not os.environ.get("ARTURO_BIN") and bundled.is_file() and os.access(bundled, os.X_OK):
        runtime = str(bundled)
    else:
        runtime = os.environ.get("ARTURO_BIN", "arturo")
    exe = shutil.which(runtime) if not pathlib.Path(runtime).exists() else runtime
    chunks = []
    if exe:
        cp = subprocess.run([str(exe), "--no-color", "-e", "info '" + symbol],
                            text=True, capture_output=True, timeout=20)
        chunks.append(cp.stdout or cp.stderr or f"Arturo exited {cp.returncode}")
    else:
        chunks.append(f"Arturo runtime not found ({runtime}); index-only result.\n")
    rows = matches(symbol, exact=True)
    if rows:
        chunks.append("Official docs: " + doc_line(rows[0], str(args.get("channel", "stable"))))
    else:
        chunks.append("No exact entry in the stable 521-symbol index.")
    return "\n".join(x.rstrip() for x in chunks)

def arturo_search(args):
    query = str(args.get("query", "")).strip()
    limit = max(1, min(int(args.get("limit", 20)), 100))
    if not query:
        raise ValueError("query is required")
    rows = matches(query)[:limit]
    if not rows:
        return "No indexed match."
    return "\n".join(f"{r['name']}\t{r['module']}\t{r['stable_url']}" for r in rows)

def arturo_doc_url(args):
    symbol = str(args.get("symbol", "")).strip()
    channel = str(args.get("channel", "stable"))
    if channel not in ("stable", "latest"):
        raise ValueError("channel must be stable or latest")
    rows = matches(symbol, exact=True)
    return doc_line(rows[0], channel) if rows else "No exact indexed match."

TOOLS = [
    {"name":"arturo_info", "description":"Get authoritative runtime info and official docs URL for an Arturo symbol or operator alias.",
     "inputSchema":{"type":"object", "properties":{"symbol":{"type":"string"}, "channel":{"type":"string", "enum":["stable","latest"]}}, "required":["symbol"]}},
    {"name":"arturo_search", "description":"Search the offline 521-entry Arturo standard-library index by name or module.",
     "inputSchema":{"type":"object", "properties":{"query":{"type":"string"}, "limit":{"type":"integer", "minimum":1, "maximum":100}}, "required":["query"]}},
    {"name":"arturo_doc_url", "description":"Resolve a symbol to a tested official stable/latest documentation URL.",
     "inputSchema":{"type":"object", "properties":{"symbol":{"type":"string"}, "channel":{"type":"string", "enum":["stable","latest"]}}, "required":["symbol"]}},
]
CALLS = {"arturo_info": arturo_info, "arturo_search": arturo_search, "arturo_doc_url": arturo_doc_url}

def response(req):
    method = req.get("method")
    if method == "initialize":
        return {"protocolVersion":"2025-03-26", "capabilities":{"tools":{}},
                "serverInfo":{"name":"arturo-language-help", "version":"1.1.0"}}
    if method == "ping": return {}
    if method == "tools/list": return {"tools": TOOLS}
    if method == "tools/call":
        params = req.get("params") or {}; name = params.get("name")
        if name not in CALLS: raise ValueError(f"unknown tool: {name}")
        text = CALLS[name](params.get("arguments") or {})
        return {"content":[{"type":"text", "text":text}], "isError":False}
    if method and method.startswith("notifications/"): return None
    raise ValueError(f"unsupported method: {method}")

def send(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        try:
            req = json.loads(line)
            result = response(req)
            if "id" in req and result is not None:
                send({"jsonrpc":"2.0", "id":req["id"], "result":result})
        except Exception as e:
            rid = req.get("id") if isinstance(locals().get("req"), dict) else None
            send({"jsonrpc":"2.0", "id":rid, "error":{"code":-32603, "message":str(e)}})

if __name__ == "__main__": main()
