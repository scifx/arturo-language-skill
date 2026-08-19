# Arturo practical rules, idioms & gotchas (source-verified)

Distilled from hands-on experience and verified against the bundled runtime
(`scifx/Arturo-Future` 0.10.1-dev+43 source: `src/library/*.nim`,
`src/vm/parse.nim`, `src/vm/ast.nim`) and the official examples corpus. Each
rule is labelled **verified** (confirmed against source/examples) or
**corrected** (the naive form is wrong; here is the right form). When in
doubt, always confirm with `info 'name` / `./bin/ahelp`.

## Fast self-education on any keyword

```bash
./bin/arturo -e "symbols | keys | print"      # every defined symbol, as a list/block
./bin/arturo --no-color -e "info 'print"      # help: usage, options, returns (like --help)
./bin/arturo --no-color -e "info.get 'print"  # deeper info as a dictionary object
./bin/arturo --no-color -e "info.get 'print | get 'example"  # the official runnable example block
./bin/arturo --no-color -e "inspect #[a:1]"   # a VALUE's runtime structure
```

**Verified.** `symbols` returns a `:dictionary` of the current symbols;
`keys symbols` is used in real code (`examples/src/rosetta/Introspection.art`).
`info` prints a formatted help block; `info.get` returns a dictionary (the
`.get` attribute is defined on `info`). `example` inside that dictionary holds
the official example(s) — extremely useful for writing correct code locally.

**`inspect` is the value-structure twin of `info`** (signature
`inspect value :any`, options `.muted`/`.compact`/`.index`). Use it to see
what a value *actually* looks like at runtime — recursive, type-annotated:
dictionary keys+types, nested blocks, function params/body, error details
(`inspect (try [1/0])` shows `Arithmetic Error: Division by zero ...`), date
fields (`inspect now` shows year/month/day/hour/...), colors, etc. The
division of labor:

| Need | Use |
|---|---|
| signature of a word / what args it takes | `info 'x` |
| metadata dict + official runnable examples | `info.get 'x` (literal only!) |
| a VALUE's runtime structure (what a function returned, dict keys, error content) | `inspect x` |

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

## The literal-as-pointer mental model (`'a` / `var` / `let`)

**Verified on the bundled runtime (and the model agent-shell.art's author uses
to teach Arturo).** The single most useful way to *think* about literals:

- `'a` is a `:literal` — the **word itself**, not its value. Think: a
  **pointer to the variable `a`**.
- `var 'a` **dereferences**: reads the value the pointer points at.
- `let 'a v` **writes through the pointer**: binds `a` to `v`.
- Passing `'a` to a builtin whose signature accepts `:literal`/
  `:pathliteral` = passing the pointer so the function can **modify the
  original** in place.

```arturo
a: 42
p: 'a
print type p            ; :literal        — p is a pointer
print var p             ; 42              — dereference (read)
print var 'a            ; 42              — same
let 'a 99               ; dereference (write)
print a                 ; 99

xs: [3 1 2]
sort 'xs                ; sort receives the pointer → mutates xs
print xs                ; [1 2 3]
'xs ++ 9                ; append through the pointer
print xs                ; [1 2 3 9]
inc 'a                  ; increment through the pointer
```

This model explains every "why is there a `'`?" in the language:

| Code | Pointer reading |
|---|---|
| `sort 'xs` | "sort, modifying what `xs` points to" (vs `sort xs` = sort a copy, discard result) |
| `'xs ++ item` / `append 'xs item` | append through the pointer to `xs` |
| `inc 'i`, `'total + n` | modify `i`/`total` in place through the pointer |
| `loop xs 'x [...]` | the loop creates a fresh variable `x` and hands its pointer to the body |
| `info 'print` | pass the *name* `print` so info can look it up (passing `print` would call it) |
| `let 'a v` | `let` binds through the pointer = assignment in other languages |
| `var 'a` | read through the pointer = dereference |
| `alias "bar" foo` | `alias` needs the *name* `bar` to bind (`'bar`/`"bar"`), not the value |
| custom in-place fn | `incN: function [s :literal][ let s (var s) + 1 ]` then `incN 'n` mutates outer `n` |

The Lisp connection: blocks `[...]` are data (not executed until `do`/
iterators), code is a stream of words, calls are prefix — "code is data" like
Lisp. But the *working* model for writing Arturo is the dictionary + pointer
one: words are dictionary entries, literals are pointers.

## Words, attributes (method variants), literals

- **Verified.** A word (`x`) resolves a value; a literal (`'x`) passes the word
  itself — required by many iterator bindings, in-place mutations, and
  references.
- **Corrected (whitespace matters around `'`).** The literal marker must be
  glued to the word: `'x ++ 9` is a literal append, but `' x ++ 9` (space
  after the quote) starts a **char literal** that swallows everything until the
  next `'`, producing errors like "Quoted string contains newline". Always
  write `'name` with no space — this is why real code writes `'msgs ++ ...`,
  not `' msgs ++ ...`.
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

## Importing local files: the `./{file}!` pattern

```arturo
import ./{foo}!
```

**Verified / nuance.** Read the three pieces: `./` is the relative-path
shorthand, `{...}` is the curly-brace string identifier, and the trailing
**`!` is the execute marker** — it wraps the rest in a `do` block (`opExec`),
i.e. it forces the imported module's top-level code to be **applied to the
current stack/scope**. Omitting `!` is the classic pit: the module's
definitions are not applied, and later code cannot find the functions/objects
it defined.

- **Multi-file projects that depend on each other: always use the explicit
  `./{file}!` path form.** It is the most reliable across versions and avoids
  resolution ambiguity (a bare `import "foo"!` first looks for local
  `foo`/`foo.art`, then a folder, then a GitHub repo, then a package — the
  relative form skips that guessing).
- Dynamic paths work too: `p: "./dynmod.art"` then `import p!`.
- `import.lean "pkg"!` gives a namespaced dictionary instead of injecting
  into scope; `import.version:0.0.3 "pkg"!` pins a package version.
- agent-shell.art loads its `tools/*/tool.art` at runtime exactly this way
  (build each path, then `import x!` inside a loop).

## Conditionals: there is no `if/else`

- **Verified.** `if` handles a single branch only (`if cond [...]`).
- **Verified.** Use `switch` (alias `?`) for if/else:
  ```arturo
  (cond)? -> a -> b
  switch (cond) -> a -> b
  switch x=2 -> print "yes" -> print "nope"
  ```
  Both blocks are expected; only one executes. Multi-branch uses `when`/`case`.

## Strings: quotes, curly, verbatim, regex, smart-quotes

| Form | Meaning | Verified |
|---|---|---|
| `"text"` | normal string (escapes apply) | ✅ |
| `« text` | **single-line safe string**: everything after `«` to end of line is ONE raw string, no escapes, no interpolation; leading/trailing whitespace stripped | ✅ |
| `«« text »»` | **multi-line safe string** (the Python `"""..."""` equivalent): raw, keeps newlines & indentation, no interpolation; ends at the FIRST `»»`, a lone `»` is content | ✅ |
| `{...}` | curly/multiline string (indentation-normalized) | ✅ |
| `{:...:}` | **verbatim** string (no normalization) | ✅ |
| `{/.../}` | **regex** string | ✅ (`{/[0-9]+/}`, `{/\w+/}`) |
| `---...---` | triple-dash multiline template | ✅ |
| `~"text \|x\|"` | `render` template with interpolation (evaluates code) | ✅ |

**Safe strings (`«` / `««»»`) — the "never-misparse" pure-string form**
(runtime + source verified: `parseFullLineString` / `parseSafeString` in
`src/vm/parse.nim`):

```arturo
a: « this whole line is one string with "quotes" |pipes| {braces} and no \escapes
b: ««
    multi-line stays exactly as-is
        indentation and blank lines preserved
    » can appear inside; only »» ends it
»»
```

- The point: **zero confusion**. Unlike `"..."` (escapes) or `~"..."`
  (interpolation) or `{...}` (curly nesting rules), `«`-strings take
  everything literally — perfect for HTML/XML/JSON/SQL/code snippets that
  contain quotes, braces, pipes, backslashes.
- **Single `«` eats the ENTIRE rest of the line** — nothing after it is code
  (`x: 1 « comment-ish` leaves `x: 1` and the rest is a string). Do not put
  code after it.
- **Double `««...»»` ends only at `»»`** — a single `»` inside is content,
  but a second `««` or `»»` inside WILL terminate early. Keep `««`/`»»` out
  of the payload.
- Python mapping: `« text` ≈ (no direct equivalent; closest is a line
  continuation comment), `««...»»` ≈ `"""..."""` triple-quoted string.
  Interpolation is NOT performed (unlike `~"..."`), matching Python's plain
  triple-quote behavior.
- `unicode.strip` is applied to single-`«` strings (leading/trailing
  whitespace removed); `««...»»` keeps everything verbatim.

## String concatenation: `++` is `append`, strings only

**Corrected (important, runtime-verified on 0.10.1-dev+43).** `++` is the
infix alias of `append`, NOT a general "string + anything" operator:

```arturo
print "a" ++ "b"          ; "ab" — fine, both strings
print "a" ++ 0            ; ⚠️ DANGEROUS on this build
```

Mixed operands misbehave in two ways:

- In `print "a" ++ 0`, `append` **consumes both operands and returns
  `:nothing`**, so the following `print` finds an empty stack and you get a
  confusing **`Cannot perform: print — Not enough parameters`** error. The
  real problem is the `++`, not `print`.
- `r: "a" ++ 0` then `print type r` **hangs this build's VM** (reproducible;
  SIGKILL required). The appended value is a broken `:string` whose type
  inspection never returns.

Correct ways to build strings from mixed values:

```arturo
print (to :string 0) ++ "a"   ; convert first (official manual's own fix)
print ~"|0|a"                 ; interpolation
print ["a" 0]                 ; block print = space-joined
```

Rule of thumb: **`++` only ever joins two strings.** Anything else goes
through `to :string`, `~"..."`, or `print [ ... ]`. (The official manual gives
the same example: `to :string 3 ++ "..."` fails; `(to :string 3) ++ "..."`
works.)

## Scope: blocks leak, iterators restore, functions isolate, `.inline` removes

**Verified against the official manual.** Traditional scoping intuition does
not apply:

- **Blocks have no scope.** A variable created inside `do [...]`/`if [...]` is
  visible afterwards; re-assigning an outer variable inside a block persists.
- **Iterators are the exception:** the *injected* loop variables are visible
  only inside the loop body, and any outer binding with the same name is
  restored afterwards.
- **Functions have their own scope.** Variables created inside a function are
  local; outer variables are readable; changes do not leak out. The `.inline`
  attribute makes a function scope-less (its assignments leak to the caller's
  scope), and `.export:` exports a specific symbol.
- Real-world pattern (agent-shell.art's `lib/py.art`): helper functions are
  declared `function.inline [..][..]` precisely because they must *define*
  names in the caller's scope.

## Values are passed by reference — `new` copies

**Verified (manual's word of caution).** `b: a` makes `b` refer to the *same*
value as `a`; mutating one mutates both:

```arturo
a: [1 2 3]
b: a
append 'b 9               ; a is now [1 2 3 9] too!
c: new a                  ; c is a copy
append 'c 9               ; a unchanged
```

Use `new` whenever you assign a mutable value (block/dictionary/string) and
plan to mutate one of the two independently. This is a top-3 "why did my
variable change?" cause for people coming from Python (where `b = a` on a list
*also* aliases, but Arturo does it for *all* mutable values, including when
passing into functions).

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

## Misleading diagnostics: "Not enough parameters: X"

**Runtime-verified.** When a line fails with `Cannot perform: X — Not enough
parameters` but `X` clearly received its arguments, the cause is usually **one
expression to the left** that *consumed* operands and returned `:nothing`
instead of a value. Common triggers:

- `++` with mismatched types (see the string-concat section above):
  `print "a" ++ 0` reports `print / Not enough parameters`, not an append
  error.
- A helper that returns nothing on one code path (e.g. an `if` with no
  `else`-branch value).

Debug by simplifying the line: bind the suspect expression to a variable first
and print its `type` — but beware that `type` of the broken `++` value itself
can hang this build (see above).

## Renaming functions: avoid `let x (var y)!`; use a wrapper

**Corrected (runtime-verified).** The `alias` builtin and the idiom
`别名: $[x y] [let x (var y)!]` seen in some projects do **not** reliably
produce a callable new name on this build:

- `alias "bar" foo` then `bar 21` → `Identifier not found: bar`.
- `let 'bar (var 'foo)!` then `bar 21` → binds something that does not call
  correctly ("Not enough parameters: bar"), because `!` wraps the rest in a
  `do` block and the binding semantics get subtle.

The robust, boring way that always works:

```arturo
foo: $[x][ x * 2 ]
bar: $[x] -> foo x        ; wrapper — reliable rename
print bar 21              ; 42
```

If you only need an alias *inside one expression*, just re-assign the value:
`bar: foo` then call `bar` (functions are values). But for long-lived
renames across the file, the one-line wrapper above is the safe form.

## Attributes are a stack, not function parameters (the real model)

**Verified against the language author's explanation (issue #2136).** The
single most misunderstood feature. Attributes (`sort.descending xs`,
`join.with:"," xs`) look like optional function arguments, but they are NOT.
An attribute is just a **"push this key/value pair onto the attribute stack"
command**. It can appear *anywhere*, even at the start of a statement, and it
sits there until some function consumes it:

```arturo
.by: "l"                      ; push an attribute — nothing consumes it yet
print "This an example"       ; print ignores it
print split "Hello world"     ; split CONSUMES .by: → ["He" "" "o wor" "d"]
print split "Hello world"     ; attribute already popped → default split by char
```

Think CSS, not Python kwargs: attributes float in the current evaluation
context until a function that recognizes them pops them. This also means
**attribute order does not matter** and attributes can be spread across
statements — flexible, but easy to leak into a call you did not intend.

### The three reflection functions

- `attr 'name` — **pops** the named attribute and returns it; `null` if absent.
- `attr? 'name` — **only checks** presence; does NOT pop.
- `attrs` — returns a **copy** of the whole attribute dictionary **and clears
  it**.

**Do not mix `attr`/`attrs` in the same function** — both clear the
dictionary, so the second call finds nothing. Pick one.

### Rule: a function must have ≥ 1 parameter to see attributes

**Verified on the bundled runtime.** Attributes are captured *right before the
last function parameter*. A zero-argument function (`$[]`) never sees them —
calls like `foo.online` leave the attribute unconsumed and `attr 'online`
returns `null`:

```arturo
f0: $[][ print attr 'online ]   ; f0.online → null  (attribute NOT captured)
f1: $[x][ print attr 'online ]  ; f1.online 10 → true (captured)
```

This is an AST-construction constraint (the author: "it *has to* have an
argument"), not a bug. The standard workaround is a **placeholder parameter**
named `null` or `placeholder` that callers fill with `null`:

```arturo
models: $[placeholder][ ... ]   ; callers write: models.online null
```

## Default parameters: the `default` helper (issue #2136, author-approved)

There is no optional-parameter syntax in Arturo; the official recommendation
is attributes + `coalesce` (`??`). This helper — contributed by the
agent-shell.art author in issue #2136 and confirmed by the language author
("quite accurate and it would work") — packages that pattern into a reusable,
Nim-`default`-style form:

```arturo
default: function.inline [name value][
    let name ((attr name) ?? value)
]
alias.infix ":" 'default!       ; optional: enables 'x: value form

foo: $[placeholder][
    default 'x "value0"         ; x = .x: attr if passed, else "value0"
    'y: "value1"                ; same via the infix alias
    print [x y]
]

foo null                        ; → value0 value1   (placeholders = null)
foo .x: "a" .y: "b" null        ; → a b
```

How it works, reading right-to-left:

1. `attr name` — pop the `.name:` attribute off the stack (`null` if absent).
2. `?? value` — `coalesce`: pick the default when the attribute was `null`.
3. `let name (...)` — bind the result to the caller's variable. This is why
   the helper must be `function.inline`: a normal function would keep the
   binding in its own scope and the caller would never see `x`.
4. `alias.infix ":" 'default!` — lets you write `'y: "value1"` sugar, but only
   if you want it; plain `default 'y "value1"` is fine.

Pitfalls:

- **The function still needs its placeholder parameter** (see the rule
  above) — the attributes are captured only because `foo` has ≥1 param.
  Callers pass `null` for it.
- **Never name a parameter `null`** — it shadows the built-in `null` constant
  and causes hidden bugs. Use `placeholder` or similar (the author's own
  advice).
- `if?` is **deprecated/removed** — it does not exist on 0.10.1-dev+43. Use
  `if` / `case` / `when`. (It appeared in older attribute examples.)
- The official `attr` documentation example is wrong
  (`print multiply.with: 6 5` outputs 30, not 60 as documented); trust the
  runtime, not that page.

This is the idiomatic way to emulate Python's `def f(x=1, y=2)` — there is no
`def f(x=1, y=2)` equivalent in the language itself. agent-shell.art's
`lib/py.art` uses exactly this helper for its `.pypy:`/`.file:` flags.

### Style note: the `'x: null` declaration form (version-dependent)

agent-shell.art's `ai.art` declares attribute-style parameters like this:

```arturo
ai: function [msg][
    'history: null        ; "declare attribute-style param, default null"
    'tools: null
    'system: null
    ...
]
```

**Runtime-verified caveat:** on the bundled build (0.10.1-dev+43) the
attribute is **NOT** auto-bound to the same-named variable — `'tools: null`
followed by a call `ai.tools: "T" "msg"` leaves `tools` as `null`. You must
read attributes explicitly (`attr 'tools` / `attr? 'tools` / the `default`
helper), as shown above. The `'x: null` form only *declares* the variable with
a null default; whether attributes flow into it depends on the runtime
version. For portable code, always pair the declaration with an explicit
`attr`/`default` read.

## Doc strings: make `info` document YOUR functions (`;;` data comments)

**Runtime + official-doc verified (`documentation/library/core/function`,
"adding complete documentation for user function using data comments").**
Just as builtins carry `info` metadata, *your* functions can too: put
`;; key: value` **data comments** at the top of the function body, and
`info 'fn` / `info.get 'fn` will show them — description, custom options,
returns, and a runnable example, exactly like builtins:

```arturo
addThem: function [
    x :integer :floating
    y :integer :floating
][
    ;; description: « takes two numbers and adds them up
    ;; options: [
    ;;      mul: :integer « also multiply by given number
    ;; ]
    ;; returns: :integer :floating
    ;; example: {
    ;;      print addThem 10 20
    ;;      print addThem.mult:3 10 20
    ;; }

    mult?: attr 'mult
    switch not? null? mult?
        -> return mult? * x + y
        -> return x + y
]

info 'addThem
; |--------------------------------------------------------------------------------
; |        addThem  :function
; |--------------------------------------------------------------------------------
; |                 takes two numbers and adds them up
; |          usage  addThem x :integer :floating
; |                         y :integer :floating
; |        options  .mul :integer -> also multiply by given number
; |        returns  :integer :floating
; |--------------------------------------------------------------------------------
```

Verified details:

- **Supported keys (function-level):** `description`, `options: [...]`,
  `returns`, `example: {...}`. `name`/`module`/`author` are NOT overridable
  at function level (name stays the binding; module/author are script-level
  `;;` keys via the `script` builtin).
- **Value forms:** single-line `« text` (safe string) or `{...}` for
  multi-line; `options` is a block of `label: :type « explanation` entries.
- **`example` behaves exactly like a builtin's**: `info.get 'fn | get
  'example` returns a `:block` of string segments, each runnable with `do`.
- **`info.get 'fn`** returns the same 7 keys as user functions:
  `name address type description args attrs returns example`.
- **Pairs perfectly with the `default`/`attr` helper**: declare your
  attribute-style options in the doc string AND read them via
  `default 'timeout 30`, so callers get documented keyword arguments.
- `;;` collects script-level metadata too (author/year/license/description/
  hint/export) — read it with the `script` builtin (`inspect script`); but
  inside a function body it attaches to THAT function's info.
- Rule of thumb: write the doc string for every non-trivial function you
  define — it makes your whole module self-documenting through the same
  `info`/`info.get` loop used for builtins.

## The `standalone?` main-guard idiom (project pattern)

Files that double as libraries and programs wrap their entry code in
`if standalone? [...]` (a reflection builtin — true when the file is the main
script, false when it is imported):

```arturo
; every module in agent-shell.art ends with:
if standalone? [
    print ai "你是谁？"
]
```

This is the Arturo equivalent of Python's `if __name__ == "__main__":` — use
it so imported modules don't run demo code.

## Shell out with structured output: `execute.code`

**Runtime-verified.** `execute "cmd"` returns the raw string; the `.code`
attribute returns a **dictionary** with `\output` and `\code`:

```arturo
r: execute.code "echo hello"
print r\output            ; hello
print r\code              ; exit code
```

agent-shell.art's shell tool uses exactly this, plus `ensure.that:` to
validate the result:

```arturo
data: execute.code c
ensure.that:"data.output为空" -> not? null? data\output
```

## Dynamic import: `import x!` with a variable path

**Runtime-verified.** `import` accepts a computed path, not only string
literals. agent-shell.art loads tools at runtime by building paths and
importing each one:

```arturo
p: "./dynmod.art"
import p!                  ; works — dynamic path
```

(Also `import "./{relative/file}!"` and `import.lean "pkg"!` for isolation.)

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

## What is NOT in the runtime

- **Corrected (typo).** There is no `reader` builtin — "reader" is a
  misspelling of **`render`**, which is the one that can evaluate interpolated
  `|...|` content (see the template-safety section above). Do not look for a
  `reader` keyword; the risk lives in `render`/`~"..."`.
- Always confirm a suspected keyword with `symbols | keys | print` before using
  it.
