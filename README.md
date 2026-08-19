# Arturo Language AI Skill

Agent Skills-compatible Arturo 0.10.0 skill with runtime-first help, an offline 521-entry library index, Python comparison, tested recipes, link/version evidence, and optional MCP tools.

## Fastest use

First make sure an Arturo runtime exists (otherwise the skill falls back to its offline index). The **preferred source is the maintainer's prebuilt-binary repo `scifx/arturo-bin`**:

```bash
command -v arturo && arturo --version        # already installed?
scripts/get-arturo.sh                        # fetch from scifx/arturo-bin + sha256 verify + dep check
```

(`scripts/get-arturo.sh` tries git clone → codeload → raw URL → GitHub API blob, verifies the pinned SHA-256, and reports any missing local libraries with per-distro install hints; the full dependency spec is in `references/runtime-dependencies.md`. Official installer fallback: `curl -sSL https://get.arturo-lang.io | sh`.)

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
