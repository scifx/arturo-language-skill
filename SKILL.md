---
name: arturo-language
description: Write, explain, translate, debug, test, and research Arturo programming language code. Use for .art files, Arturo syntax/API questions, Python-to-Arturo translation, standard-library lookup, CLI/package usage, or when the user mentions arturo-lang.io, pkgr.art, Arturo functions, attributes, literals, blocks, pipes, or right-to-left evaluation.
license: MIT
metadata:
  language: Arturo
  verified-version: 0.10.1-dev+43
  verified-date: 2026-08-19
  default-arturo-command: bin/arturo
  default-python-command: python3
  preferred-runtime-source: this repository (bin/arturo, bin/arturo-mini)
---

# Arturo Language Skill

Use this skill to produce **version-aware, tested Arturo**, not plausible-looking Rebol/Python.

## Arturo 的核心思想 (the one-paragraph mental model)

> **Arturo 只有几条基本规则。规则熟悉后,写代码就是"查字典"——每个词都是一个
> 字典条目,边查边写;词后面加 `.属性` 扩展它的功能;按规则把词组合起来,就能
> 写出任何程序。语法上它像 Lisp(代码即数据、前缀调用、无语法),但心智模型上
> 它更接近"字典 + 指针"。**

拆开就是四句话(全部展开在 `references/practical-rules.md`):

1. **词 = 功能条目(查字典写代码)。** 每个词(`print` `map` `sort` `digest`...)
   就是一个函数/值。写代码前先查字典: `info '词`(或 `./bin/ahelp 词`)给出
   签名、属性、返回值和**可运行的官方示例**——照着示例改就是正确代码;`inspect 值`
   查值的运行时结构。521 个词全部可本地查询,不靠猜。
2. **词 + `.属性` = 功能扩展。** `sort` → `sort.descending`(布尔属性)、
   `sort.by: 'x`(带值属性);`join` → `join.with: ","`;`read` → `read.json`
   `read.toml` `read.xml` `read.lines`。同一个词,点号一加就是新变体。属性本质
   是"属性栈"(不是参数),详见下。
3. **规则组合 = 程序。** 前缀调用、右到左求值、无优先级、arity 驱动、块 `[...]`
   是延迟的数据、`|` 管道倒转调用顺序。基本规则就这些。
4. **`'a` 字面量 = 指针,`var 'a` = 解引用。** 字面量是"词本身"(`:literal`),
   把它传给函数 = 传指针,函数可用 `var`(解引用读)/ `let`(解引用写)读写原变量。
   这就解释了全部"魔法": `sort 'xs` 就地排序、`'xs ++ 9` 追加、`inc 'i` 自增、
   `loop xs 'x` 循环注入变量、`info 'print` 传名字而非执行函数。

### 核心关键字最小集 (the six meta-capabilities)

这套"查字典 + 指针"的心智模型能立起来,靠的是六个元能力关键字——它们是
"语言教自己"的基础设施,分三层:

| 层 | 关键字 | 作用 |
|---|---|---|
| 查字典层 | `symbols` | 字典目录: `symbols \| keys \| print` 列出所有可用词 |
| | `info` (+`.get`) | 查词的契约: 签名/属性/返回值,`.get` 拿元数据字典和**官方示例** |
| | `inspect` | 查值的运行时结构: 字典键、嵌套块、错误内容、日期字段 |
| 指针层 | `var` | 解引用读: `var 'a` → a 的值 |
| | `let` | 解引用写: `let 'a v` → 绑定 a = v |
| 执行层 | `do` | 块从"数据"变"代码"的开关: `do [code]` 执行块 |

有了这六个,任何不认识的词都能在本地"自举"出来: `symbols` 找词 → `info`
看契约 → `info.get ... example` 拿可运行示例 → `inspect` 看值 → `var`/`let`
理解指针语义 → `do` 验证。这就是"边查边写"的全部基础设施。

## Get the Arturo runtime — the shortest path: use the one bundled in this repo

**This skill ships its own prebuilt Arturo binaries — no download needed.** Use them directly:

```bash
./bin/arturo --version        # Full build (no UI): big ints, HTTPS, SQLite, regex, parsers, crypto, DOCGEN
./bin/arturo-mini --version   # Mini build: zero extra shared-lib dependencies

# make bin/ahelp and all skill commands use the bundled runtime:
export ARTURO_BIN="$PWD/bin/arturo"
# or install it onto PATH once:
install -m755 bin/arturo ~/.arturo/bin/arturo   # then add ~/.arturo/bin to PATH
```

Both are built from `scifx/Arturo-Future` (0.10.1-dev+43, commit `933420d`,
2026-08-19) and run on **glibc ≥ 2.36** (Debian 12+, Ubuntu 22.04+). They live
in `bin/` so every clone of this repo carries the runtime with it — the fastest
possible path from clone to working Arturo. Checksums: see
`references/runtime-dependencies.md`.

**Runtime dependencies (in this sandbox, Debian 12):** the bundled Full build
needs the system runtimes `libgmp.so.10`, `libmpfr.so.6`, `libssl.so.3`,
`libcrypto.so.3` (all present by default on Debian 12+/Ubuntu 22.04+/Fedora
39+/Arch; `apt-get install -y libgmp10 libmpfr6 libssl3 libsqlite3-0` if
missing) and dlopens `libsqlite3.so.0`. The Mini build has **zero** extra dependencies.
`scripts/get-arturo.sh --check-only bin/arturo` prints a live missing-lib
report; the full matrix is in `references/runtime-dependencies.md`.

Fallback routes (use these only when the bundled binaries are unavailable):

| System | Command / route |
|---|---|
| any | `curl -sSL https://get.arturo-lang.io \| sh` (latest stable) or `https://get.arturo-lang.io/latest` (nightly) |
| any | Pre-built binaries: official downloads page `https://arturo-lang.io/` → Download, or GitHub Releases `https://github.com/arturo-lang/arturo/releases` (unzip & run; no install needed) |
| macOS | `brew install arturo` |
| Arch Linux | AUR: `yay -S arturo` or `paru -S arturo` |
| Windows | `curl -sSL https://get.arturo-lang.io/ps \| powershell -c -` (or WSL/Git-Bash/MSYS2 one-liner) |
| from source | only as last resort: clone `arturo-lang/arturo`, run `./build.nims --install` (needs Nim, GTK/webkit libs) — see `references/resources.md` |

Then verify and make the runtime discoverable by the skill tools:

```bash
./bin/arturo --version                 # e.g. 0.10.1-dev+43 (bundled binary)
export ARTURO_BIN="$PWD/bin/arturo"    # optional; bin/ahelp auto-detects the bundled runtime itself
```

**If no runtime can be run in this environment**, do not guess signatures: use the offline path `./bin/ahelp name` and the reference files, and say so when reporting results. Do not invent a signature you cannot run.

## Start here: the three lookup forms (查字典)

**There are exactly three lookup forms — memorize all three, they are the
whole "dictionary":**

```arturo
info 'x                  ; form #1: print formatted help (signature, attrs, returns)
info.get 'x | get 'example   ; form #2: the official runnable example, offline
inspect x                ; form #3: print a VALUE's runtime structure
```

### Form #1: `info 'x` — human-readable help

```bash
./bin/arturo --no-color -e "info 'read"    # bundled runtime; zero other dependencies
./bin/arturo --no-color -e "info '++"      # aliases/operators also work ('++ → append)
```

Prints the signature, options, and return type — Arturo's `--help`.

### Form #2: `info.get 'x | get 'example` — offline built-in example (KEY)

`info.get 'x` returns the same metadata as a **dictionary** (fields: `name
address type description module args attrs returns example line source`).
The `example` field is a **block of ready-to-run code segments** — every
keyword ships its official examples **inside the runtime, no internet
needed**. Verified on the bundled build:

```arturo
info.get 'map | get 'example | print    ; show all official examples
ex: info.get 'map | get 'example
print ex\0                              ; first segment (a multi-line string)
do ex\0                                 ; RUN it right there
```

- `example` is a `:block` whose items are `:string` code segments; each
  segment is independently runnable with `do` (its `;`-comments show expected
  output, e.g. `print digest "Hello world" ; 3e25960a79...`).
- **Verified: `info.get` only works with a direct literal `'x`.** A variable
  (`info.get w`) or a quoted string (`info.get "map"`) returns `null` on this
  build — always write the literal. (Plain `info "map"` with a string DOES
  print help, but its `.get` variant does not return a dict for strings.)
- Alias symbols work: `info.get '++` → resolves to `append`.
- 20/20 sampled keywords across all modules had an `example`; the standard
  library embeds examples for essentially every keyword.

### Form #3: `inspect x` — see a VALUE's structure (the runtime struct)

While `info`/`info.get` describe the *word* (its signature and metadata),
`inspect` describes the *value*: it recursively prints the type structure of
whatever you hand it — dictionary keys, block nesting, function params/body,
error details, date fields, etc. (signature: `inspect value :any`; options
`.muted` no color, `.compact` omit type annotations, `.index` show block
indexes).

```arturo
inspect #[name: "Ada" age: 37]     ; :dictionary with field types
inspect [1 2 [3 4]]                ; :block, nested block shown
inspect now                        ; :date with all its fields
err: try [ 1 / 0 ]
inspect err                        ; Arithmetic Error: Division by zero...
inspect $[x][x*2]                  ; :function, params and body blocks
inspect.compact meta\attrs         ; compact view of a nested dict
```

Use it to answer "what does this value actually look like at runtime?" —
e.g. what a function *returns*, or what keys a dictionary really has —
when `info` only shows the signature. `inspect` + `info`/`info.get` together
are the local debug loop: check the word's contract, then inspect the actual
value.

**All of this is local and offline.** Once a runtime is installed, these
forms give you usage, options, return type, **and a runnable example for
every keyword without any internet access.** This is the fastest way to write
correct code: query the keyword → read its `example` → adapt it. For symbol
lists use `symbols | keys | print`. (When no runtime exists, `./bin/ahelp -s
TERM` still resolves the doc URL offline.)

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
ARTURO_BIN=/opt/arturo/bin/arturo ./bin/ahelp read   # explicit runtime override
python3 scripts/arturo_help.py read --info --runtime ./bin/arturo
```

Copy `config.env.example` to `config.env` for persistent local overrides. `bin/ahelp` does **not** use Python; `PYTHON_BIN` is only a hint for the optional Python helper. Never assume `/usr/bin/arturo` or that the command is named `python`.

### Lookup decision table

| Need | First action | Extra files needed |
|---|---|---|
| Exact API/signature | `info 'NAME` | none |
| Exact API but no runtime | `./bin/ahelp NAME` | none; wrapper reads index |
| Unknown function name/concept | `./bin/ahelp -s TERM` | none |
| Syntax/evaluation question | read this file's quick rules, then `references/syntax-cheatsheet.md` only if needed | at most one |
| Gotchas / idioms / correct usage | `references/practical-rules.md` (string forms, infix right-to-left, `import ...!`, template safety, error handling) | one |
| Runtime binary / dependencies / distro compatibility | `bin/arturo` (bundled) + `references/runtime-dependencies.md` | none |
| 15-minute tour vs Python (learn fast) | `references/in-a-nutshell-vs-python.md` | one |
| Mind-shift from a traditional language (scope, by-ref, `new`, `++`, JSON, diagnostics) | the **思维模式转换** section above + `references/practical-rules.md` | at most two |
| Default/optional parameters, the attribute stack, `attr`/`attr?`/`attrs` | `references/practical-rules.md` → **Attributes are a stack** + **Default parameters** | one |
| HTTP / JSON / `serve` / file-state (real project) | `references/web-and-http-patterns.md` | one |
| Python translation | `references/python-to-arturo.md` | one |
| Version/build discrepancy | `references/verified-tests.md` | one |

**Fast keyword self-education** (mirrors the user's workflow, all verified):
`symbols | keys | print` lists every defined symbol; `info 'NAME` shows help;
`info.get 'NAME | get 'example` shows the official runnable example block.
See `references/practical-rules.md`.

## 思维模式转换: from traditional languages to Arturo (5 minutes)

The fastest way to stop writing "Python with `:`" is to internalize these six
mental shifts. Full runtime-verified details live in
`references/practical-rules.md` and `references/in-a-nutshell-vs-python.md`
(step-by-step Python ↔ Arturo side-by-side).

1. **No syntax, just values.** No commas, no mandatory parens, no indentation,
   no reserved keywords. Code is a stream of words/labels/symbols/values;
   blocks `[...]` are inert data until executed (`do`, iterators, etc.).
2. **Calls are prefix and arity-driven; evaluation is right-to-left; there is
   NO operator precedence.** `2 * 3 + 4` is **14** (= `2 * (3+4)`), and
   `print square 5` means `print (square 5)`. Parenthesize any mixed infix
   chain whose grouping matters.
3. **`=` compares, `:` binds.** `+ * ++ ? ??` etc. are just *infix aliases*
   of prefix functions (`add`, `mul`, `append`, `switch`, `coalesce`).
   `++` concatenates **strings only**; for mixed values convert first
   (`(to :string n) ++ "x"`) or use `~"|n|x"` / `print [n "x"]`.
4. **`'a` is a pointer; `var 'a` dereferences it; `let 'a v` writes through
   it.** This one model explains everything "magic": `sort 'a` mutates in
   place, `'xs ++ item` appends, `inc 'i` increments, `loop xs 'x` injects a
   variable, `info 'print` passes the name instead of executing it. Values
   themselves are by-reference too: `b: a` aliases `a` — use `new a` for an
   independent copy.
5. **Blocks have no scope; functions isolate; `.inline` opens them up.**
   Iterator variables are restored after the loop. Errors are values:
   `err: try [...]`, then `error? err`; `err\kind`/`err\msg`.
6. **OOP is opt-in and data-light:** `define :type [init: method [...]...]`,
   `to :type [...]!`, `this\field`, magic methods (`string:`, `add:`, ...).
   JSON/TOML are first-class data: `read.json s|file`, `write.json v null`,
   `read.toml f`.
7. **Attributes are a stack, not kwargs.** `.words` in `split.words x` is not
   an argument — it is a value pushed onto a stack that the function pops.
   They can sit anywhere (even before unrelated code) until consumed. That is
   also why **functions need ≥1 parameter to read attributes**, and why
   "default parameters" are built as `(attr 'x) ?? fallback` (see the
   `default` helper in Core rules / practical-rules.md).

## Core rules (enough for most tasks)

- Binding is `x: 3`; equality is `x = 3`; inequality is `x <> 3`.
- Calls are prefix and arity-driven: `print square 5`. Evaluation is
  **right-to-left with no operator precedence** — infix operators are just
  aliases of prefix functions, so `2 * 3 + 4` is `2 * (3 + 4)` = **14**.
  Parenthesize mixed infix chains.
- Blocks `[ ... ]` are values/deferred code. `do block` executes one; `@block`/`array block` evaluates its items into an array.
- A word (`x`) resolves a value. A literal (`'x`) passes the word itself—required by many iterator bindings and in-place operations.
- Strings are `"text"`; interpolation is `~"Hello |name|"`; **safe strings** `« text` (rest of line, raw) and `«« ... »»` (multi-line raw, the Python `"""..."""` equivalent) hold literal text with no escapes/interpolation — safest for HTML/SQL/JSON snippets.
- Regex literals use the curly form `{/.../}` in this build (e.g. `match.once "xabcy" {/abc/}`). Plain `/.../` is **division**, and passing a mis-parsed `/.../` expression to `match`/`contains?` can hang the runtime — verify with `info 'match` and test small regexes before relying on them. Put flags inline (`{/(?i)abc/}`), not after the closing `/`.
- Blocks and dictionaries differ: `[1 2 3]` vs `#[name: "Ada"]`.
- Index/member access uses backslash and is zero-based: `xs\0`, `user\name`, `xs\[i]`.
- Functions: `square: function [x :integer][x*x]`; call with `square 4`. `$` aliases `function`: `square: $[x][x*x]`.
- OOP-lite custom types: `define :person [init: method [n][this\n: n] string: method [][~"I am |this\n|"]]`, construct with `to :person ["Ada"]!`, access `this\field`. Magic methods (`string:`, `add:`, `inc:`, ...) overload stdlib behavior.
- Attributes/options: `sort.descending xs`, `join.with:"," xs`, `request.get url #[]`, `write.json v null`. **Attributes are a stack, not function params** — they float until a function pops them (`.by: "l"` before a `split` works). To read them in your own function: `attr 'name` pops, `attr? 'name` checks, `attrs` copies+clears; the function **must have ≥1 parameter** (use a `placeholder` that callers fill with `null`).
- **Default/optional parameters** (no Python-style defaults exist): attributes + `??` fallback via the `default` helper — `default: function.inline [name value][let name ((attr name) ?? value)]`, then `default 'x "fallback"` inside the function; callers pass `.x: "a"` or omit it. Full rules in `references/practical-rules.md`.
- In-place forms receive a literal/path literal: `append 'xs item`, `'xs ++ item`, `inc 'i`, `sort 'a`.
- **Values are passed by reference**: `b: a` aliases `a` — use `new a` for an independent copy before mutating.
- **Blocks have no scope** (variables leak out); iterators restore injected vars; functions isolate; `.inline` makes a function scope-less (`function.inline [..][..]`).
- Iteration: `map xs 'x -> x*x`, `select xs 'x -> even? x`, `loop xs 'x [print x]`. Sugar: `=>` injects implicit `&` (`map xs => [2 * &]`); `|` pipes reverse prefix calls (`1..5 | map => [2*&] | print`).
- Integer operands: `/` gives integer-style division; `//` gives floating division—the spelling differs from Python.
- A trailing `!` is parser/evaluation sugar: it wraps the rest in a `do` block, used after `import "pkg"!`, `to :type [...]!`, and computed calls.
- JSON/TOML as data: `read.json` parses a JSON string *or* file path; `write.json value null` returns a JSON string (and `write.json value "file"` writes); `read.toml` reads config. Do **not** use `parse.json` — `parse` has no `.json` attribute in this build (it silently returns the input string).
- Full and Mini builds differ. Mini lacks UI, HTTPS, database, package-manager, parser, and arbitrary-precision features listed in official build docs.
- **The whole language is discoverable locally.** Every keyword lives in the standard library; `symbols | keys | print` lists them all, `info 'x` / `info.get 'x | get 'example` reveal usage, options, returns, **and a runnable example**, and `inspect value` shows a value's runtime structure. With these, you can look up and write almost any Arturo program without the internet — so query before you guess.
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

1. Ensure a runtime is available: `ls bin/arturo` or `command -v arturo`. The bundled binary is preferred (see **Get the Arturo runtime** above); do not build from source unless that fails.
2. Identify target version/build. Default to the bundled `0.10.1-dev+43` if unspecified; confirm with `./bin/arturo --version`.
3. Query every unfamiliar API with `info 'name`; if no runtime, use `./bin/ahelp name`.
4. Write the smallest runnable `.art` program. Prefer explicit iterator parameters before dense pipe/sugar forms.
5. Run `./bin/arturo --no-color file.art` or `./bin/arturo --no-color -e 'CODE'` when a runtime exists.
6. On failure, trust the diagnostic. Check literal vs resolved word, arity/order, block evaluation, attributes, right-to-left grouping, and build variant.
7. Read at most the one relevant deep reference unless diagnosing version drift:
   - syntax → `references/syntax-cheatsheet.md`
   - gotchas/idioms → `references/practical-rules.md`
   - 15-min tour vs Python (learning) → `references/in-a-nutshell-vs-python.md`
   - HTTP/JSON/serve/web project → `references/web-and-http-patterns.md`
   - Python translation → `references/python-to-arturo.md`
   - task recipes → `references/recipes.md`
   - links/source/package routes → `references/resources.md`
   - runtime binary/deps (bundled bin/arturo, missing libs) → `references/runtime-dependencies.md`
   - compatibility/evidence → `references/verified-tests.md`

**If no runtime is available**, verify signatures and idioms against source instead of guessing: the bundled binaries come from `scifx/Arturo-Future` (fork of `arturo-lang/arturo`); clone it (`git clone --depth 1 https://github.com/scifx/Arturo-Future`), then check the built-in's `builtin "name"` declaration in `src/library/*.nim` and its official examples in `tests/unittests/*.art`. Example checks that already passed against source:

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
