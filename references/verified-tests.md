# Verification, compatibility, and known limitations

Verification date: **2026-08-19**. Test platform: Linux amd64 sandbox. Primary runtime under test: **the bundled `bin/arturo` / `bin/arturo-mini` (0.10.1-dev+43, built from `scifx/Arturo-Future`)**; the official stable release **Arturo 0.10.0 “Arizona Bark”** is retained as a documentation/link baseline. This document distinguishes facts directly executed in the sandbox from documentation/link checks and areas that were not exercised. It is deliberately explicit so an agent does not convert a small smoke test into a claim that every library feature was tested.

## 1. Evidence levels

Use these labels when interpreting this skill:

- **Runtime-verified**: executed against the bundled `bin/arturo` / `bin/arturo-mini` binaries in this workspace (earlier 0.10.0 Mini-verification notes are kept as historical baseline).
- **Link-verified**: fetched over HTTPS and returned the recorded HTTP status on the verification date.
- **Source-verified**: checked against shallow clones of official repositories at the commits listed in `resources.md`.
- **Documentation-derived**: stated by official documentation but not necessarily executable in Mini.
- **Not tested**: no claim of runtime behavior is made. Query the target runtime or test in an appropriate environment.

The skill is a navigation and correctness aid, not a substitute for running the user's actual program on the user's target build and operating system.

## 2. Binary/download verification

The stable Full Linux amd64 ZIP was downloaded from:

`https://arturo-lang.io/files/arturo-0.10.0-linux-amd64.zip`

Its SHA-256 matched the official value:

`764e484bf226ed14494b0e87601af4cd399da778d31ea059150bb07a621bb35d`

The Full executable did not start in the sandbox because the host lacked `libwebkit2gtk-4.1.so.0`. This is an environment/dependency limitation, not evidence of an Arturo language defect. It demonstrates why a skill must not promise that a Full binary is completely dependency-free on every Linux image.

The stable Mini Linux amd64 ZIP was downloaded from:

`https://arturo-lang.io/files/arturo-0.10.0-linux-amd64-mini.zip`

Its SHA-256 matched:

`2ff02a02ec4b26916b2a45c585e1bfbcfe14bb5e29e1ea317ccf7ca3ae539077`

The Mini executable launched and reported:

`arturo 0.10.0 Arizona Bark (amd64/linux)`

## 2b. Bundled binary verification (preferred runtime source)

**This repo now ships the runtime** — `bin/arturo` (Full, no UI) and
`bin/arturo-mini` (Mini), both built 2026-08-19 from `scifx/Arturo-Future`
(commit `933420d`, version `0.10.1-dev+43`) with Nim 2.2.6 + GCC 12.2 on
Debian 12 (`--release`, LTO, strip, mimalloc):

- `bin/arturo`: SHA-256 `b7597e9d5ea3d0c0229e37c936518b12c0d69cb9ffe514fad63a9e08f2b0a38d`, 6,519,792 bytes — Full build minus the UI stack (no WEBVIEW/DIALOGS/CLIPBOARD; GMP/ssl/SQLITE/PARSERS/DOCGEN kept)
- `bin/arturo-mini`: SHA-256 `78fbbf467528a8b7e2cc83d5015f5d75c3c6165f7f188ef543b7bcae848705ad`, 5,200,088 bytes — Mini build, zero extra shared-lib deps

Run attempt in this sandbox (Debian 12 bookworm, glibc 2.36, GCC 12):

```
$ ./bin/arturo --version
arturo 0.10.1-dev+43 (amd64/linux)
```

`ldd bin/arturo` / `ldd bin/arturo-mini`: **no `not found` entries**. The
Full build's runtime deps (`libgmp.so.10`, `libmpfr.so.6`, `libssl.so.3`,
`libcrypto.so.3`, dlopen `libsqlite3.so.0`) are all standard on Debian 12+.
Runtime-verified features of the Full build: big integers (`2^300`), MPFR
floats (`sqrt 2.0`), SQLite (create/insert/select), **HTTPS** (`request` →
status 200), PCRE regex, crypto hashes. Full matrix and rebuild notes:
`references/runtime-dependencies.md`.

Historical note: the earlier `scifx/arturo-bin` upload (Full build, SHA-256
`73bda271...`, commit `cc0849a`) required glibc ≥ 2.38 + the webkit/GTK stack
and could not launch on Debian 12 (exit 127). It is superseded by the bundled
binaries above.

## 3. CLI compatibility matrix

| Capability | Mini 0.10.0 observed | Full 0.10.0 in this sandbox | Status |
|---|---:|---:|---|
| run `.art` file | yes | not launchable here | runtime-verified on Mini |
| `-e`, `--evaluate` | yes | not exercised | runtime-verified on Mini |
| `-r`, `--repl` shown in help | yes | not exercised | runtime/help-verified |
| `-h`, `--help` | yes | not exercised | runtime-verified |
| `-v`, `--version` | yes | not exercised | runtime-verified |
| `--no-color` | yes | not exercised | runtime-verified |
| `-c`, `--compile` | shown as experimental | not exercised | help-derived, not functional-tested |
| `-x`, `--execute` | shown as experimental | not exercised | help-derived, not functional-tested |
| `-b`, `--bundle`, `--as` | shown as experimental | not exercised | help-derived, not functional-tested |
| package-manager commands | absent | not executable here | expected Mini limitation |

Do not infer that experimental bytecode or bundling behavior is stable merely because the flags appear in help.

## 4. Full versus Mini scope

Official build-variant documentation says Mini omits UI/webview capabilities, arbitrary-precision features, HTTPS, package-manager functionality, databases, and built-in HTML/Markdown/TOML/XML parsers. The smoke suite intentionally uses core/collection/string/reflection functionality expected in Mini.

Full-only areas were **not runtime-tested** here: UI, webview, HTTPS requests, database drivers, package installation/update, and the omitted parsers. When writing code for any of these areas, an agent must:

1. identify that Full is required;
2. query `info 'name` on the user's Full runtime;
3. run a minimal environment-specific test;
4. avoid treating a Mini “identifier not found” or unsupported-protocol failure as proof that the API does not exist in Full.

## 5. Documentation and resource-path verification

The stable library page was parsed and its alphabetical function/predicate/constant links were extracted. The resulting index has **521 data rows**. Every stable function page was fetched: **521 returned HTTP 200; zero failed** on the verification date.

Each corresponding `/latest` URL was also fetched: **514 returned HTTP 200; seven returned HTTP 404**. The seven are stable Sockets routes:

- `accept`
- `connect`
- `listen`
- `receive`
- `send`
- `send?`
- `unplug`

For these entries, `bin/ahelp --latest` and the Python helper intentionally fall back to the tested stable URL instead of presenting a known-dead link.

Additional route checks:

| Route | Observed status |
|---|---:|
| `https://arturo-lang.io/stable/documentation/` | 200 |
| `https://arturo-lang.io/latest/documentation/` | 200 |
| `https://arturo-lang.io/v0.10.0/documentation/` | 404 |
| `https://arturo-lang.io/master/documentation/` | 404 |
| `https://get.arturo-lang.io` | 200 |
| `https://get.arturo-lang.io/latest` | 200 |
| `https://pkgr.art/list.art` | 200 |
| `https://dummy.pkgr.art/spec` | 200 |

The nginx source supports a `/v<version>` routing pattern, but that does not mean every version tree is deployed. Therefore version URLs must be HTTP-checked before use. Search-engine results containing `/master/...` were stale at verification time.

## 6. Runtime smoke suite

`tests/smoke.art` was run as:

```bash
arturo --no-color tests/smoke.art > actual.txt
diff -u tests/expected-smoke.txt actual.txt
```

The output matched exactly. Covered behaviors:

- comments and basic output;
- binding with `x:`;
- integer arithmetic;
- a typed function declared with `function`;
- the `$` alias for `function`;
- prefix function calls;
- `map` with a literal iterator parameter;
- `select` with a predicate;
- inclusive integer ranges;
- dictionary construction and backslash member access;
- interpolated strings;
- `join.with:` value-bearing attribute syntax;
- ternary/switch sugar;
- `when` branching;
- in-place numeric modification through a literal word;
- `info.get` returning metadata, with its `name` field accessed by path.

This is a deterministic syntax/API smoke suite. It is **not** exhaustive testing of 521 functions. The CSV's 521/521 result proves page reachability, not execution correctness for each function.

## 7. Introspection behavior directly verified

These forms work in Mini 0.10.0:

```arturo
info 'append
info '++
meta: info.get 'map
print arity\map
print symbols
inspect value
print type value
```

Important negative checks:

- `info :append` fails because `:append` is a type value, while `info` expects a string/word/literal/path literal/symbol literal.
- `info append` resolves/calls `append` first and fails for missing parameters. It does not mean “help for append.”
- `arity` takes no argument and returns a dictionary. Use `arity\append`; `arity 'append` is not the intended lookup form.
- `attrs` reports attributes active inside the current call. It is not a function-documentation database. Use `info.get 'functionName` to retrieve documented attributes.
- No `help` symbol was found in stable Mini 0.10.0.
- No `source` symbol was found in stable Mini 0.10.0.

Therefore the zero-step built-in help mechanism is `info`, not an invented Python-like `help()`.

## 8. Arithmetic and evaluation facts checked

Official examples and runtime behavior agree that integer operands behave as follows:

```arturo
35 / 4     ; 8
35 // 4    ; 8.75
```

This spelling is easy for Python users to reverse accidentally. `%` is modulo and `^` is power. Arturo's general right-to-left evaluation and infix precedence can make visually nested calls surprising; parentheses are recommended when translating nontrivial Python expressions. The smoke suite confirms representative prefix/infix combinations, not every precedence edge case.

## 9. Source/version drift

The stable website index contains 25 modules and 521 entries. The checked current source has `Events.nim`, `Streams.nim`, and `Tasks.nim` in addition to the modules represented by the stable index. The current website repository also has documentation module pages for Events, Streams, and Tasks. Conversely, seven stable Sockets URLs are absent under `/latest`.

This means “latest” is not always a strict superset of stable. APIs may move, merge, disappear, or be generated under a different module. For nightly/current-development work, use the target runtime's `info`, then `/latest`, then current `src/library/*.nim`. Do not mechanically rewrite a stable URL by adding `/latest` and assume it exists.

## 9b. Practical-rules source verification

The following gotchas/idioms documented in `references/practical-rules.md` were
verified against the v0.10.0 source checkout and the official examples corpus:

- `symbols` returns a `:dictionary`; `keys symbols` is used in real code
  (`examples/src/rosetta/Introspection.art`). `info` prints help; `info.get`
  returns a dictionary with an `example` field (attribute `.get` defined on
  `info` in `src/library/Reflection.nim`).
- `import` resolves local file → local folder → repo → local/remote package
  (`getEntryForPackage`/`processLocalFile` in `src/vm/packager.nim`); trailing
  `!` is an execute marker that wraps the rest in a `do` (`opExec`,
  `src/vm/ast.nim`).
- Infix operators associate **right-to-left**: official example
  `examples/src/rosetta/Operator precedence.art` shows `3 * 5 + 2` ==
  `3 * (5 + 2)` == 21, not 17. Parenthesize mixed infix chains.
- `render` (alias `~`, `src/library/Strings.nim`) **evaluates** the `|...|`
  interpolation regions as Arturo code and is recursive by default;
  `render.once` disables recursion. This confirms the "template can execute
  content" caution.
- String forms: `"..."` plain, `{...}` multiline/curly, `{:...:}` verbatim,
  `{/.../}` regex, `---...---` triple-dash multiline. There is **no** special
  `{::}` literal; `{::}` is just an empty verbatim string
  (confirmed in `src/vm/parse.nim` and `examples/src/rosetta/Determine if a
  string is collapsible.art`). No `reader` builtin exists in v0.10.0.
- `try` returns an `:error` on failure or `null`; `error?` is the type
  predicate; `err\kind`/`err\msg` hold error details
  (`src/library/Exceptions.nim`, `Types.nim`).
- Inline `;` comments after code are valid (used throughout official
  examples), e.g. `i: 1 ; sum 1..100`.
- `switch` (alias `?`) is the if/else construct; `if` is single-branch only;
  multi-branch uses `when`/`case` (`src/library/Core.nim`).
- Attributes sit on the stack and a keyword can capture/consume an attribute of
  the same name when it evaluates; it is real but fragile, so prefer explicit
  attribute syntax (`sort.descending`, `join.with:"`). Consistent with the
  attribute model in `src/library/*.nim` and `src/vm/ast.nim`.
- Newlines are insignificant (whitespace-only syntax): multi-line code of any
  length can be compressed onto one line if spaces stay intact. But a `;`
  comment discards everything after it on that physical line — so compressed
  single-line code must have **no** `;` comments, or the rest of the line is
  silently dropped. Confirmed by official examples and parser behavior.

## 9c. In-a-nutshell vs Python execution verification

Every row in `references/in-a-nutshell-vs-python.md` was verified: the Python
expressions were **executed** in this sandbox (Python 3.11) and produced the
recorded outputs; the Arturo side was checked against v0.10.0 source semantics
and the official in-a-nutshell documented outputs. Spot-checked equivalences
(all matched): `35/4`↔`35//4`=8, `35//4`↔`35/4`=8.75, `2^5`↔`2**5`=32,
`1..10` inclusive vs Python `range` exclusive, `select` keeps / `filter` drops,
`and?`/`or?` short-circuit, string upper/lower/split/join/contains, list
map/select/filter/unique/slice/repeat, and 0-based backslash indexing.

## 9d. Web/HTTP project-pattern source verification

The real-world web/RSS patterns in `references/web-and-http-patterns.md` were
checked against v0.10.0 source:

- `request` args are `url` + `data` (`Net.nim`); `serve` handlers return
  strings and `.port:` is an attribute (`Net.nim`).
- `write` args are `content` + `file`; `.directory`/`.json`/`.compact`/`.append`
  are attributes (`Files.nim`).
- `call` takes `(function, params-block)`; `do` evaluates a block (`Core.nim`).
- `{/.../}` curly regex ends at the first literal `}` (`parse.nim`). Tested
  experience: appending flags after the closing `/` (`{/pattern/i}`) is **not
  reliable** — use inline `(?i)` inside the pattern instead, and keep `}` out
  of the pattern.
- `key?` accepts only `:dictionary`/`:object`, not `:store` (`Collections.nim`).
- No `else` keyword; two-way branch via `(cond)? [a] [b]` (`Core.nim`).

Some items (e.g. `do [fn arg]` vs bare-call misbinding, `++ @[feed]` not
splicing a dict, mini-HTTPs `request` returning `null`, serve returning a dict
→ 500) are behavioral and marked "project experience"; re-verify on the target
build with `info 'name` and a minimal test before relying on them.

## 10. Helper verification

The following helper paths were exercised:

```bash
./bin/ahelp read
./bin/ahelp '++'
./bin/ahelp -s string
./bin/ahelp --latest accept
python3 scripts/arturo_help.py map
python3 scripts/arturo_help.py '++'
python3 scripts/arturo_help.py map --info --runtime /path/to/arturo
```

`scripts/get-arturo.sh` was exercised: with the bundled binaries present it
uses `bin/arturo` with **no download** (installs to `~/.arturo/bin/arturo`,
dependency report shows no missing libs on Debian 12); `--check-only` works
on both bundled binaries. `bin/ahelp` auto-detects the bundled `bin/arturo`
and returns real runtime `info` output.

The shell helper requires POSIX `sh` and `awk`, auto-detects the bundled `bin/arturo` (falling back to `$ARTURO_BIN`/PATH), skips the runtime in `-s` search mode, and does not require Python. The Python helper uses `python3` through its environment shebang, auto-detects the bundled `bin/arturo`, and accepts an explicit `--runtime` path. Neither helper downloads or executes remote documentation. A native PowerShell counterpart exists at `bin/ahelp.ps1` (same bundled-binary default and `-Search` behavior); it was source-reviewed but not executed in this Linux sandbox because `pwsh` was unavailable.

The MCP server was smoke-tested with newline-delimited JSON-RPC requests for `initialize`, `tools/list`, and `tools/call`. It is optional. MCP client configuration varies; clients normally require absolute paths. The MCP server's index tools work without Arturo, while runtime `arturo_info` degrades to index-only output if `ARTURO_BIN` cannot be found.

## 11. Known limitations and safe interpretation

- Link status is time-sensitive. Re-run `python3 scripts/verify_links.py` when freshness matters.
- The standard-library index is stable 0.10.0-oriented and does not automatically regenerate itself from a future release.
- Runtime help is authoritative for the installed build, but project-local definitions can shadow symbols. Test in a clean process when diagnosing built-ins.
- The shell CSV reader relies on the current index schema and on the relevant fields not containing commas. It is intentionally simple and fast.
- Windows without WSL/Git Bash may not run `bin/ahelp`; use `python3`/`py -3 scripts/arturo_help.py` or MCP.
- The old scifx/arturo-bin Full upload could not launch in this Debian 12 sandbox (needed glibc ≥ 2.38 + webkit/GTK; see §2b historical note). The bundled `bin/arturo` (no-UI Full) and `bin/arturo-mini` both **run and are runtime-verified** on Debian 12, including HTTPS/SQLite/big-int for the Full build.
- Network, databases, sockets, UI, packaging, bundling, bytecode compilation, and cross-platform behavior were not comprehensively exercised.
- Examples and Rosetta Code are secondary sources for idioms. They can target older language versions.
- Generated documentation describes intended signatures but cannot guarantee environmental resources such as TLS libraries, GUI libraries, database drivers, file permissions, or open network ports.

## 12. Reverification checklist

For a future Arturo version:

1. download from the official home page and verify the published checksum;
2. record `arturo --version` and `arturo --help` for Full and Mini separately;
3. run `tests/smoke.art` and inspect any signature drift with `info`;
4. regenerate the library index from the new stable page;
5. run stable and latest link checks;
6. compare `src/library/*.nim` module names with stable website modules;
7. test Full-only features in a host with required dependencies;
8. update `verified-version`, `verified-date`, checksums, commits, and this evidence matrix.
