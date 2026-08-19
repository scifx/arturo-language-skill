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
| Python translation | `references/python-to-arturo.md` | one |
| Version/build discrepancy | `references/verified-tests.md` | one |

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

1. Identify target version/build. Default to stable `0.10.0` if unspecified.
2. Query every unfamiliar API with `info 'name`; if no runtime, use `./bin/ahelp name`.
3. Write the smallest runnable `.art` program. Prefer explicit iterator parameters before dense pipe/sugar forms.
4. Run `arturo --no-color file.art` or `arturo --no-color -e 'CODE'` when a runtime exists.
5. On failure, trust the diagnostic. Check literal vs resolved word, arity/order, block evaluation, attributes, right-to-left grouping, and build variant.
6. Read at most the one relevant deep reference unless diagnosing version drift:
   - syntax → `references/syntax-cheatsheet.md`
   - Python comparison → `references/python-to-arturo.md`
   - task recipes → `references/recipes.md`
   - links/source/package routes → `references/resources.md`
   - compatibility/evidence → `references/verified-tests.md`

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
