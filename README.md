# Arturo Language AI Skill

Agent Skills-compatible Arturo skill with **a bundled prebuilt runtime**, runtime-first help, an offline 521-entry library index, Python comparison, tested recipes, link/version evidence, and optional MCP tools.

## Fastest use

**The runtime ships in this repo** (`bin/arturo` Full build with big ints/HTTPS/SQLite/regex/parsers/crypto, `bin/arturo-mini` zero-dep Mini build) — no download needed:

```bash
./bin/arturo --version                 # arturo 0.10.1-dev+43 (amd64/linux)
export ARTURO_BIN="$PWD/bin/arturo"    # point the skill helpers at it (ahelp auto-detects too)
```

Both binaries are built from `scifx/Arturo-Future` (0.10.1-dev+43) and run on glibc ≥ 2.36 (Debian 12+, Ubuntu 22.04+); the Full build uses the standard system libs `libgmp.so.10` / `libmpfr.so.6` / `libssl.so.3` / `libcrypto.so.3` (+ dlopen `libsqlite3.so.0`). If those are ever missing, `scripts/get-arturo.sh --check-only bin/arturo` prints install hints; the full dependency spec is in `references/runtime-dependencies.md`.

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

The entry point for agents is `SKILL.md`. Stable documentation links were verified 521/521; exact evidence and test scope are in `references/verified-tests.md`.
