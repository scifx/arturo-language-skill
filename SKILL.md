---
name: arturo-language
description: Write, explain, translate, debug, test, and research Arturo programming language code. Use for .art files, Arturo syntax or API questions, Python-to-Arturo translation, standard-library lookup, CLI/package usage, arturo-lang.io, pkgr.art, Arturo literals, blocks, pipes, attributes, and right-to-left evaluation.
license: MIT
metadata:
  language: Arturo
  verified-version: 0.10.0
  verified-date: 2026-08-19
  default-arturo-command: arturo
---

# Arturo language

Produce version-aware, tested Arturo—not plausible-looking Rebol or Python.
The target runtime is authoritative. Stable 0.10.0 is the fallback when the
user does not specify a version.

## Mandatory workflow

1. Check `command -v arturo && arturo --version` and identify Full versus Mini.
2. Query each unfamiliar symbol before using it:
   ```bash
   arturo --no-color -e "info 'read"
   arturo --no-color -e "info '++"
   ```
   In Arturo, use `info 'read`; use `info.get 'read` for metadata and
   `info.get 'read | get 'example` for the embedded official example.
3. If the runtime is unavailable, use the offline index:
   ```bash
   ./bin/ahelp read
   ./bin/ahelp '++'
   ./bin/ahelp -s string
   ```
   Do not invent signatures. State that runtime execution was unavailable.
4. Write the smallest runnable program. Prefer explicit iterator parameters
   and explicit parentheses over dense sugar.
5. Run `arturo --no-color file.art` or `arturo --no-color -e 'CODE'`.
6. On failure, trust the diagnostic; check arity/order, literal versus resolved
   word, block evaluation, attributes, grouping, and build variant.

If Arturo is missing and installation is appropriate, use the official stable
installer (`curl -sSL https://get.arturo-lang.io | sh`) or a prebuilt GitHub
Release. Do not build from source unless those routes fail. See
`references/resources.md` for platform-specific routes and checksums.

## Verified core rules (Arturo 0.10.0)

- Bind with `x: 3`; compare with `x = 3`; inequality is `x <> 3`.
- Calls are prefix and arity-driven: `print square 5`.
- Evaluation is generally right-to-left. Infix chains also associate
  right-to-left: `3 * 5 + 2` is `3 * (5 + 2)`, or `21`. Parenthesize mixed
  infix expressions whenever grouping matters.
- `[ ... ]` is a block value/deferred code. `do block` executes it;
  `@block`/`array block` evaluates its items into an array.
- `x` resolves a value; `'x` passes the word itself. Iterators and in-place
  operations commonly require literals.
- Strings are `"text"`; `~"Hello |name|"` is evaluated interpolation.
  Do not interpolate untrusted text as code; use `render.once` when one pass is
  intended.
- Blocks and dictionaries differ: `[1 2 3]` versus `#[name: "Ada"]`.
- Index/member paths use backslash and are zero-based: `xs\0`, `xs\[i]`,
  `user\name`.
- Functions: `square: function [x :integer][x*x]`; `$` aliases `function`.
- Attributes select variants: `sort.descending xs`, `join.with:"," xs`.
- In-place operations take literals/path literals: `append 'xs item`,
  `'xs ++ item`, `inc 'i`.
- Iterators: `map xs 'x -> x*x`, `select xs 'x -> even? x`,
  `loop xs 'x [print x]`.
- Integer `/` truncates (`35 / 4` is `8`); `//` produces floating division
  (`35 // 4` is `8.75`). This spelling is opposite Python's.
- `if` is one-branch. Use `(cond)? -> a -> b` or `switch` for two branches;
  use `when`/`case` for multiple branches.
- `fold` takes its seed as an attribute:
  `fold.seed:0 1..5 [acc x][acc + x]`.
- File writes are content first, path second:
  `write "hello" "out.txt"`; JSON is `write.json value "out.json"`.
- `request` takes URL and data: `request url null`. Query its attributes and
  expect a dictionary or `null`.
- `serve` handlers may return a string or a response dictionary containing
  `body`, `status`, and `headers`.
- `import "module.art"!` executes the imported module in the current context;
  `import.lean` returns a namespaced dictionary.
- Mini omits capabilities including UI, HTTPS, databases, package management,
  and several parsers. Query on the user's actual build.

## Minimal reliable program

```arturo
numbers: 1..10
squares: map numbers 'n -> n * n
evens: select squares 'n -> even? n
print evens
```

## Choose one deeper reference

Load only what the task needs:

| Need | Reference |
|---|---|
| Syntax/evaluation | `references/syntax-cheatsheet.md` |
| Source-verified gotchas | `references/practical-rules.md` |
| Fast tour versus Python | `references/in-a-nutshell-vs-python.md` |
| Python translation | `references/python-to-arturo.md` |
| HTTP/JSON/server contracts | `references/web-and-http-patterns.md` |
| Task recipes | `references/recipes.md` |
| Official links/install/source | `references/resources.md` |
| Evidence, compatibility, limitations | `references/verified-tests.md` |

For unknown names, `./bin/ahelp -s TERM` searches the bundled 521-entry stable
index. Optional MCP tools (`arturo_info`, `arturo_search`, `arturo_doc_url`) are
documented in `mcp/README.md`; MCP is configured by the host, never written as
fictional Arturo source.

## Evidence gate

Promote a rule into generated code only when supported by one of these, in
priority order:

1. execution on the target runtime;
2. `info`/`info.get` from that runtime;
3. matching-version official source declarations and official tests/examples;
4. an HTTP-verified matching-version official documentation page.

Treat project anecdotes, Rosetta Code, community snippets, and latest/nightly
behavior as leads to re-test—not as signatures. Link reachability does not
prove runtime behavior. Full-only behavior was not runtime-tested in this
repository's Mini smoke environment.

## Final check

Before answering, verify `:` versus `=`, blocks versus dictionaries, zero-based
paths, literals for mutation/binding, function arity/order, attribute syntax,
right-to-left grouping, write/request argument order, and Full-versus-Mini
availability. Say exactly what was run and what was only source-checked.
