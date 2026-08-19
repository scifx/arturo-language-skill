# Arturo Language AI Skill

Agent Skills-compatible Arturo 0.10.0 skill with runtime-first help, an offline 521-entry library index, Python comparison, tested recipes, link/version evidence, and optional MCP tools.

## Fastest use

First make sure an Arturo runtime exists (otherwise the skill falls back to its offline index):

```bash
command -v arturo && arturo --version        # already installed?
curl -sSL https://get.arturo-lang.io | sh    # official installer, if not
```

Then use Arturo's built-in help or the wrapper:

```bash
# Arturo's own built-in help: no skill script needed
arturo --no-color -e "info 'read"

# One wrapper: runtime help + official URL, or offline fallback
./bin/ahelp read
./bin/ahelp '++'
./bin/ahelp -s string
./bin/ahelp --latest accept
```

`bin/ahelp` uses POSIX shell and awk; it does **not** require Python. Override runtime discovery with `ARTURO_BIN=/path/to/arturo`, or copy `config.env.example` to `config.env`.

Cross-platform Python fallback:

```bash
python3 scripts/arturo_help.py map
```

Optional MCP integration is documented in `mcp/README.md`.

## Verify the skill

```bash
./tests/run.sh
```

The test runner always checks the offline index, shell/Python helpers, and MCP
protocol. If `arturo` (or `$ARTURO_BIN`) is available, it also runs the
deterministic Arturo smoke suite and diffs its output.

The entry point for agents is `SKILL.md`. It is deliberately distilled to
contracts supported by runtime evidence or matching-version official
source/examples. Stable documentation links were verified 521/521; this proves
reachability, not behavior. Exact evidence and limitations are in
`references/verified-tests.md`.
