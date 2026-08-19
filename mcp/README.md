# Optional Arturo MCP server

This is a real, local stdio MCP server; it is not Arturo source syntax. It uses only Python 3's standard library and the bundled CSV index.

Tools:

- `arturo_info(symbol, channel?)` — invokes `info 'symbol` when `ARTURO_BIN` is available and adds the official URL.
- `arturo_search(query, limit?)` — offline name/module search.
- `arturo_doc_url(symbol, channel?)` — stable/latest URL resolution with known-404 fallback.

## Client configuration

MCP clients normally require absolute paths. Replace both placeholders:

```json
{
  "mcpServers": {
    "arturo-help": {
      "command": "python3",
      "args": ["/ABSOLUTE/PATH/arturo-language-skill/mcp/server.py"],
      "env": {
        "ARTURO_BIN": "/ABSOLUTE/PATH/TO/arturo"
      }
    }
  }
}
```

`ARTURO_BIN` is optional. Without it, index and URL tools still work and `arturo_info` returns index-only information.

## Manual protocol smoke test

```bash
printf '%s\n' \
 '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
 '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
 '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"arturo_doc_url","arguments":{"symbol":"read"}}}' \
 | python3 mcp/server.py
```

The server writes one JSON-RPC response per line to stdout. Host clients manage calls; do not write `mcp(...)` in Arturo programs.
