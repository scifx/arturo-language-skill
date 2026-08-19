# Arturo practical rules, idioms & gotchas (source-verified)

Distilled from hands-on experience and verified against the official Arturo
v0.10.0 source (`src/library/*.nim`, `src/vm/parse.nim`, `src/vm/ast.nim`) and
the official examples corpus. Each rule is labelled **verified** (confirmed
against source/examples) or **corrected** (the naive form is wrong; here is the
right form). When in doubt, always confirm with `info 'name` / `./bin/ahelp`.

## Fast self-education on any keyword

```bash
arturo -e "symbols | keys | print"      # every defined symbol, as a list/block
arturo --no-color -e "info 'print"      # help: usage, options, returns (like --help)
arturo --no-color -e "info.get 'print"  # deeper info as a dictionary object
arturo --no-color -e "info.get 'print | get 'example"  # the official runnable example block
```

**Verified.** `symbols` returns a `:dictionary` of the current symbols;
`keys symbols` is used in real code (`examples/src/rosetta/Introspection.art`).
`info` prints a formatted help block; `info.get` returns a dictionary (the
`.get` attribute is defined on `info`). `example` inside that dictionary holds
the official example(s) — extremely useful for writing correct code locally.

## Installation

**Preferred: use the binary bundled in this repo — no download needed.**

```bash
./bin/arturo --version                 # Full build (big ints, HTTPS, SQLite, regex, parsers, crypto)
./bin/arturo-mini --version            # Mini build (zero extra deps)
export ARTURO_BIN="$PWD/bin/arturo"
```

**Verified.** The bundled binaries (0.10.1-dev+43, built from
`scifx/Arturo-Future`) run on glibc ≥ 2.36 — verified in this sandbox (Debian
12): version, big-int arithmetic, floats, SQLite, HTTPS (`request` → 200),
regex, crypto all exercised. Fallback official installer:

```bash
curl -sSL https://get.arturo-lang.io | sh      # latest stable
curl -sSL https://get.arturo-lang.io/latest | sh  # nightly preview
```

Pre-built binaries are also downloadable from the site/Releases (no install
needed, just unzip and run). macOS: `brew install arturo`; Arch (AUR):
`yay -S arturo`. There is **no** official Debian/Ubuntu `apt install arturo`.
Dependency requirements of the bundled binaries (system libgmp/libmpfr/libssl
for the Full build, none for Mini) are in `references/runtime-dependencies.md`.

## Language model (right-to-left, arity-driven)

- **Verified.** Arturo evaluates mostly **right-to-left**; calls are prefix and
  **arity-driven** — each word consumes exactly the number of arguments its
  signature declares.
- **Verified.** Infix operators exist but group by **right-to-left**, not by
  standard math precedence. Official example `examples/src/rosetta/Operator
  precedence.art`:
  ```arturo
  print 2 + 3 * 5   ; same as 2 + (3 * 5)
  print 3 * 5 + 2   ; same as 3 * (5 + 2)   ; NOT (3*5)+2
  ```
- **Corrected (the real rule).** "Use parens when an infix chain has >2
  operands" is a good safety heuristic, but the *precise* rule is: **mixed
  infix expressions associate right-to-left, so parenthesize anything whose
  grouping is not what standard math would give you.** `2 + 3 * 5` is 17 (it
  happens to match), but `3 * 5 + 2` is **21**, not 17. Write `(3 * 5) + 2`
  when you mean 17.
- **Verified (parenthesize nested/compared infix).** When an infix result feeds
  another comparison or operation, group it explicitly:
  ```arturo
  (1 + 2) * 3            ; parenthesize the addition first
  if (1 > 0) < 3 [ ... ] ; group the comparison so it is the operand
  ```
  Right-to-left association makes ungrouped chains easy to misread; always
  parenthesize mixed infix.
- **Verified (whitespace-only, compress to one line).** Arturo does not care
  about newlines — multi-line code of **any length** can be compressed onto a
  single line, as long as the spaces/separators stay intact and **there is no
  `;` comment anywhere in that one line**. This is safe and common.
- **Corrected (the `;` trap when compressing).** The moment you put a `;`
  comment inside code that is being compressed to one line, everything **after
  the `;` on that same line is silently discarded** — it becomes a comment, so
  the rest of the compressed code never runs (and if the line later references
  those discarded definitions, it errors). Rule of thumb:
  - Single-line/compressed code ⇒ **strip all `;` comments first**; or keep the
    code on multiple lines so each `;` comment ends at its own line's newline.
  - Inline `;` comments (e.g. `i: 1 ; sum 1..100`) are only safe when the line
    genuinely ends right after the comment — never when more real code follows
    on the same physical line.
- **Corrected (inline comments).** Inline `;` comments after code DO work and
  are used throughout the official examples:
  ```arturo
  i: 1 ; sum 1..100
  this\table: (shuffle this\table) ; creates a random game
  ```
  A `;` comment ends at end of line; it is the parser that treats the whole
  rest of the line as a comment. No need to move code to a separate line.

## Words, attributes (method variants), literals

- **Verified.** A word (`x`) resolves a value; a literal (`'x`) passes the word
  itself — required by many iterator bindings, in-place mutations, and
  references.
- **Verified.** Attributes / method variants are `.name` suffixes that select a
  variant of the keyword and may consume extra arguments:
  ```arturo
  sort.descending xs        ; boolean attribute
  join.with:"," xs          ; value-bearing attribute
  import.lean "dummy"!      ; returns a dictionary instead of injecting into scope
  ```
- **Verified.** `define` declares a custom type; `module` creates a module;
  `import` loads packages. Query each with `info` before relying on a variant.
- **Verified (attribute capture on the stack).** A keyword consumes arguments
  arity-driven; attributes select the variant. A subtle consequence: if a
  keyword with the same name is declared as an attribute on the stack, the
  keyword will **capture and consume** that attribute when it evaluates. This
  is a real mechanism (attributes sit on the stack and get consumed), but it is
  fragile — **do not rely on it**. Prefer explicit attribute syntax
  (`sort.descending xs`, `join.with:\",\" xs`).

## Importing local files: the `./...!` pattern

```arturo
import "./foo.art"!
```

**Verified / nuance.** `import "foo"` resolves a local `foo` or `foo.art` file
first (see `processLocalFile` in `src/vm/packager.nim`), then a local folder,
then a GitHub repo, then a local/remote package. So `./` is a valid relative
path but not strictly required for a sibling file — `import "foo.art"!` works.
The trailing **`!` is the execute marker**: it wraps the remaining expression
in a `do` block (`opExec`), i.e. it forces the imported module's top-level code
to be **applied to the current stack/scope**. Omitting it is a common pit —
top-level definitions from a file may not become available to later code.
`import.lean` gives a namespaced dictionary instead. For files that depend on
each other, use explicit paths.

## Conditionals: there is no `if/else`

- **Verified.** `if` handles a single branch only (`if cond [...]`).
- **Verified.** Use `switch` (alias `?`) for if/else:
  ```arturo
  (cond)? -> a -> b
  switch (cond) -> a -> b
  switch x=2 -> print "yes" -> print "nope"
  ```
  Both blocks are expected; only one executes. Multi-branch uses `when`/`case`.

## Strings: quotes, curly, verbatim, regex

| Form | Meaning | Verified |
|---|---|---|
| `"text"` | normal string | ✅ |
| `{...}` | curly/multiline string | ✅ |
| `{:...:}` | **verbatim** string (no normalization) | ✅ |
| `{/.../}` | **regex** string | ✅ (`{/[0-9]+/}`, `{/\w+/}`) |
| `---...---` | triple-dash multiline template | ✅ |
| `~"text \|x\|"` | `render` template with interpolation | ✅ |

**Corrected.** The form `{::}` is **not** a distinct "extremely complex string"
form — `{:}` is the verbatim string opener and `{::}` is simply an *empty*
verbatim string (used as an empty line in the official examples). There is no
`{::}` special-cased literal. For regex use `{/.../}`, not `{::}`.

## Template strings can execute code — be careful

**Verified (important).** `render` (the `~"..."` template) does **not** just
substitute text: the `|...|` interpolation region is parsed and **evaluated as
Arturo code** (`doEval` + `execUnscoped` in `src/library/Strings.nim`), and it
is recursive by default. So:
- Complex/render-sensitive content inside `|...|` can be executed rather than
  substituted, causing errors or side effects.
- If you only want one-pass substitution, use `render.once`:
  ```arturo
  name: "Ada"
  print ~"Hi |name|"        ; Hi Ada
  print render.once "Hi |name|"   ; one-pass, no recursion
  ```
- Prefer simple variables inside `|...|`; avoid dropping arbitrary/code-like
  text into an interpolation.

## Error handling (Go-style)

```arturo
err: try [ riskyOperation ]
if error? err [ print err\kind ]
```

**Verified.** `try` returns an `:error` value on failure or `null` on success.
`error?` is the type predicate. `err\kind` holds the error kind and `err\msg`
the message. Pattern from the official `try` example:

```arturo
(genericError = err: <= try -> val: f)?
    -> print err      ; error happened
    -> print val      ; success path
```

## Learning from real code

The official examples corpus is the best reference for idioms:

```bash
git clone https://github.com/arturo-lang/examples
# query by keyword, e.g.
rg 'fold.seed|switch .*->' examples/src/rosetta/
```

**Verified.** The `examples/src/rosetta/` directory contains hundreds of `.art`
programs (914 `.art` files across the repo). Search by keyword to see how a
symbol is actually used, but treat Rosetta Code as idiom reference — the
authoritative signatures still come from `info 'name`.

## What is NOT in v0.10.0

- **Corrected (typo).** There is no `reader` builtin in v0.10.0 — "reader" is a
  misspelling of **`render`**, which is the one that can evaluate interpolated
  `|...|` content (see the template-safety section above). Do not look for a
  `reader` keyword; the risk lives in `render`/`~"..."`.
- Always confirm a suspected keyword with `symbols | keys | print` before using
  it.
