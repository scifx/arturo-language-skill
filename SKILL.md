---
name: arturo-language
description: Write, explain, translate, debug, test, and research Arturo programming language code. Use for .art files, Arturo syntax/API questions, Python-to-Arturo translation, standard-library lookup, CLI/package usage, or when the user mentions arturo-lang.io, pkgr.art, Arturo functions, attributes, literals, blocks, pipes, or right-to-left evaluation.
license: MIT
metadata:
  language: Arturo
  verified-version: 0.10.0
  verified-date: 2026-08-19
  default-arturo-command: arturo
  default-python-command: python3
---

# Arturo Language Skill

Use this skill to produce **version-aware, tested Arturo**, not plausible-looking Rebol/Python.

## Install / get the Arturo runtime (only if it is missing)

Check for a runtime first. If `command -v arturo` finds nothing (or `arturo --version` fails), install the **latest stable** with the official one-liner rather than building from source:

```bash
command -v arturo && arturo --version   # already installed?
curl -sSL https://get.arturo-lang.io | sh          # latest stable (Linux/macOS/FreeBSD/WSL/Git-Bash/MSYS2)
# nightly preview instead:
curl -sSL https://get.arturo-lang.io/latest | sh
```

Other official routes (use these when the installer is unavailable):

| System | Command / route |
|---|---|
| any | Pre-built binaries: official downloads page `https://arturo-lang.io/` → Download, or GitHub Releases `https://github.com/arturo-lang/arturo/releases` (unzip & run; no install needed) |
| macOS | `brew install arturo` |
| Arch Linux | AUR: `yay -S arturo` or `paru -S arturo` |
| Windows | `curl -sSL https://get.arturo-lang.io/ps | powershell -c -` (or WSL/Git-Bash/MSYS2 one-liner) |
| from source | only as last resort: clone `arturo-lang/arturo`, run `./build.nims --install` (needs Nim, GTK/webkit libs) — see `references/resources.md` |

Then verify and make the runtime discoverable by the skill tools:

```bash
arturo --version                 # e.g. 0.10.0
export ARTURO_BIN=$(command -v arturo)   # optional; bin/ahelp also auto-detects from PATH
```

**If no runtime can be installed in this environment**, do not guess signatures: use the offline path `./bin/ahelp name` and the reference files, and say so when reporting results. Do not invent a signature you cannot run.

## Start here: zero/one-step lookup

**If the function name is known, do this first—do not open another reference file:**

```bash
arturo --no-color -e "info 'read"       # zero dependency beyond Arturo itself
arturo --no-color -e "info '++"         # aliases/operators also work
```

Inside the REPL or an `.art` file:

```arturo
info 'read                 ; formatted signature, attributes, returns
meta: info.get 'read       ; same metadata as a dictionary
```

If Arturo is absent, or one command should provide runtime help plus the official URL:

```bash
./bin/ahelp read            # POSIX shell + awk; Python is NOT required
./bin/ahelp '++'
./bin/ahelp -s 'string'     # offline fuzzy search
./bin/ahelp --latest map
# Windows PowerShell: .\bin\ahelp.ps1 read
```

Python is only an optional cross-platform fallback/MCP runtime:

```bash
python3 scripts/arturo_help.py read
```

Executable overrides are environment variables, not hard-coded paths:

```bash
ARTURO_BIN=/opt/arturo/bin/arturo ./bin/ahelp read
PYTHON_BIN=python3 ./bin/ahelp read
```

Copy `config.env.example` to `config.env` for persistent local overrides. Never assume `/usr/bin/arturo` or that the command is named `python`.

### Lookup decision table

| Need | First action | Extra files needed |
|---|---|---|
| Exact API/signature | `info 'NAME` | none |
| Exact API but no runtime | `./bin/ahelp NAME` | none; wrapper reads index |
| Unknown function name/concept | `./bin/ahelp -s TERM` | none |
| Syntax/evaluation question | read this file's quick rules, then `references/syntax-cheatsheet.md` only if needed | at most one |
| Gotchas / idioms / correct usage | `references/practical-rules.md` (string forms, infix right-to-left, `import ...!`, template safety, error handling) | one |
| Python translation | `references/python-to-arturo.md` | one |
| Version/build discrepancy | `references/verified-tests.md` | one |

**Fast keyword self-education** (mirrors the user's workflow, all verified):
`symbols | keys | print` lists every defined symbol; `info 'NAME` shows help;
`info.get 'NAME | get 'example` shows the official runnable example block.
See `references/practical-rules.md`.

## Core rules (enough for most tasks)

- Binding is `x: 3`; equality is `x = 3`; inequality is `x <> 3`.
- Calls are prefix and arity-driven: `print square 5`. Evaluation is normally **right-to-left**, except infix operators. Parenthesize ambiguity.
- Blocks `[ ... ]` are values/deferred code. `do block` executes one; `@block`/`array block` evaluates its items into an array.
- A word (`x`) resolves a value. A literal (`'x`) passes the word itself—required by many iterator bindings and in-place operations.
- Strings are `"text"`; interpolation is `~"Hello |name|"`.
- Blocks and dictionaries differ: `[1 2 3]` vs `#[name: "Ada"]`.
- Index/member access uses backslash and is zero-based: `xs\0`, `user\name`, `xs\[i]`.
- Functions: `square: function [x :integer][x*x]`; call with `square 4`.
- Attributes/options: `sort.descending xs`, `join.with:"," xs`.
- In-place forms receive a literal/path literal: `append 'xs item`, `'xs ++ item`, `inc 'i`.
- Iteration: `map xs 'x -> x*x`, `select xs 'x -> even? x`, `loop xs 'x [print x]`.
- Integer operands: `/` gives integer-style division; `//` gives floating division—the spelling differs from Python.
- A trailing `!` is parser/evaluation sugar used especially in `import "pkg"!`.
- Full and Mini builds differ. Mini lacks UI, HTTPS, database, package-manager, parser, and arbitrary-precision features listed in official build docs.
- **Never invent a standard-library signature. Query `info` first.**

## Common symbols: direct official pages

These cover frequent tasks; use `ahelp` for all 521 indexed entries.

| Task | Symbols | Stable documentation |
|---|---|---|
| console/output | `print`, `prints`, `input`, `inspect` | `documentation/library/io/<name>` or Reflection for `inspect` |
| files | `read`, `write`, `exists?`, `file?`, `delete`, `copy`, `move` | `documentation/library/files/<slug>` |
| paths | `relative`, `absolute`, `extract` | `documentation/library/paths/<slug>` |
| collections | `append`, `remove`, `get`, `set`, `size`, `first`, `last`, `sort` | query `ahelp`; modules vary |
| iteration | `loop`, `map`, `select`, `fold`, `arrange` | `documentation/library/iterators/<slug>` |
| strings | `split`, `join`, `replace`, `upper`, `lower`, `render` | `documentation/library/strings/<slug>` |
| conditions | `if`, `unless`, `switch`, `case`, `when` | `documentation/library/core/<name>` |
| types | `type`, `to`, predicates such as `integer?` | `documentation/library/types/<slug>` |
| reflection/help | `info`, `arity`, `symbols`, `inspect` | `documentation/library/reflection/<name>` |
| network | `request`, `download`, `serve` | `documentation/library/net/<name>` |

Base URL: `https://arturo-lang.io/`. Predicate `?` often becomes `-` in a slug, but do not guess—`ahelp` resolves it.

## Required coding workflow

1. Ensure a runtime is available: `command -v arturo`. If missing, install it (see **Install / get the Arturo runtime** above); do not build from source unless that fails.
2. Identify target version/build. Default to stable `0.10.0` if unspecified; confirm with `arturo --version`.
3. Query every unfamiliar API with `info 'name`; if no runtime, use `./bin/ahelp name`.
4. Write the smallest runnable `.art` program. Prefer explicit iterator parameters before dense pipe/sugar forms.
5. Run `arturo --no-color file.art` or `arturo --no-color -e 'CODE'` when a runtime exists.
6. On failure, trust the diagnostic. Check literal vs resolved word, arity/order, block evaluation, attributes, right-to-left grouping, and build variant.
7. Read at most the one relevant deep reference unless diagnosing version drift:
   - syntax → `references/syntax-cheatsheet.md`
   - gotchas/idioms → `references/practical-rules.md`
   - Python comparison → `references/python-to-arturo.md`
   - task recipes → `references/recipes.md`
   - links/source/package routes → `references/resources.md`
   - compatibility/evidence → `references/verified-tests.md`

**If no runtime is available**, verify signatures and idioms against the official source instead of guessing: clone the matching tag (`git clone --depth 1 --branch v0.10.0 https://github.com/arturo-lang/arturo`), then check the built-in's `builtin "name"` declaration in `src/library/*.nim` and its official examples in `tests/unittests/*.art`. Example checks that already passed against v0.10.0 source:

- `fold` uses a seed via **attribute**, not a positional arg: `fold.seed:0 1..5 [acc x][acc + x]`.
- Ternary uses `(cond)? -> a -> b`.
- In-place arithmetic accepts a literal/path-literal (`'total + n`) because `add` accepts `Literal`/`PathLiteral` as `valueA`.
- `map 1..5 'x -> 2*x`, `select 1..10 'x -> even? x`, `join.with:","`, `sort.descending xs` match their `builtin` declarations.

## Minimal reliable template

```arturo
numbers: 1..10
squares: map numbers 'n -> n * n
evens: select squares 'n -> even? n
print evens
```

Explicit equivalent:

```arturo
squares: map 1..10 'n [n * n]
evens: select squares 'n [even? n]
print evens
```

## Final correctness check

Confirm `:` vs `=`, blocks vs dictionaries, zero-based backslash paths, literals for mutation/binding, function arity/order, attribute syntax, grouping under right-to-left evaluation, and Full-vs-Mini availability. State when code could not be run.

## Optional MCP integration

A real dependency-free stdio server is included at `mcp/server.py`. It exposes `arturo_info`, `arturo_search`, and `arturo_doc_url`. It is optional and requires Python 3 only; normal lookup does not. See `mcp/README.md`. Do not emit fictional `mcp({...})` Arturo syntax—MCP is configured by the host client, not called from Arturo source.

## Source-of-truth policy

Priority: target runtime `info` → matching version docs (only if HTTP-verified to exist) → stable docs → latest docs → current source → examples/community. Library pages are generated from metadata in `src/library/*.nim`. Rosetta Code is useful for idioms, not authoritative signatures.
