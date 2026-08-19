# Arturo project patterns: HTTP, JSON, `serve`, and file state (real-world verified)

Distilled from a working Arturo web/RSS project and verified against the
v0.10.0 source. These are the hard-won pitfalls that bite when writing a real
server + frontend, not just syntax snippets. Each is labelled **verified**
(confirmed against `src/library/*.nim` / `src/vm/parse.nim`) or **project
experience** (behavioral, from running code; re-verify on your target build).

## Call functions reliably: `do [...]` or `call 'fn @[args]`

**Verified.** Arturo calls are prefix and arity-driven, but a bare call like

```arturo
r: fetchFeed url
```

can be parsed as `r:` bound to the *function value* `fetchFeed` rather than the
result, especially when the callee is a user-defined function or a dictionary
member. Two robust forms:

```arturo
r: do [fetchFeed url]          ; evaluate the block -> call result
h: do [store.json "data/readstate"]
rawTitle: call 'tagInner @[chunk "title"]   ; explicit fn + block of params
```

`call` takes `(function, params-block)`; `do` evaluates a block as code. If a
variable ends up holding a string/path instead of the expected value, this is
usually the cause.

## No `else` — use `(cond)? [a] [b]`

**Verified.** `if` is single-branch; there is no `else` keyword (it would be an
undefined name). Two-way branch:

```arturo
(cond)? [then-block] [else-block]
title: (empty? title)? [url] [title]
(result\ok)? [ø] [return jsonErr result\error]
```

Use `[ø]` for an intentionally empty branch. Multi-branch: `when`/`case`.

## `write` always takes two arguments

**Verified** (`Files.nim`). `write` args are `content` + `file`. `.directory`,
`.json`, `.compact`, `.append` are **attributes**, not extra positional args:

```arturo
write.directory ø "data"                ; NOT write.directory "data"
write.json store "data/feeds.json"
write.json.compact val "data/_out.json"
write.json [] "data/seen.json"
```

The buggy `write.directory "data"` fails inside `ensureDir` with
`write / Required: 2` because the path was consumed as the `content` argument.

## Regex: `{/pattern/}` — and the `}` gotcha

**Verified** (`parse.nim`). A curly regex `{/.../}` ends at the **first literal
`}`**, so a pattern that contains `}` will terminate early and the rest leaks
(commonly as a parse error). Keep `}` out of the pattern or avoid `{...}`.

**Refined (source-verified, corrects overbroad advice).** The parser DOES
support trailing flags after the closing `/`: `{/pattern/im}` is valid and is
compiled to inline `(?i)(?m)...`. So:

- Use **inline `(?i)`** inside the pattern for case-insensitivity when you want
  maximum clarity: `{/(?i)<item[\s\S]+?<\/item>/}`.
- `{/pattern/i}` also parses (flag `i` → `(?i)`), but many agents have hit
  confusing failures when the pattern also contained a `}` — that is the real
  cause, not the trailing `i` itself. Prefer `(?i)` inline to avoid confusion.
- `to :regex` takes a **bare string**, not `/.../` delimiters:

```arturo
src: "(?i)<" ++ tag ++ {[^>]*>([\s\S]*?)</} ++ tag ++ ">"
pat: to :regex src
```

- Do **not** build a regex with the `~{|...|}` template — `~` is `render` and
  **evaluates** interpolated content as code (see `practical-rules.md`).

## Avoid mixing `->` with an assignment on the same statement

**Project experience.** `if empty? x -> x: y` can bind/consume `x` incorrectly
because `->` wraps the following terminal value and interacts badly with the
`:`. Use `?`/`[ ]` or put the assignment in its own block:

```arturo
; prefer
if empty? x [ x: y ]
x: (empty? x)? [y] [x]
```

## Avoid standard-library names as local variables

**Project experience.** Don't reuse built-in names like `date`, `link`,
`title`, `url`, `type` as your own bindings — they shadow the built-in and
break subsequent calls. To read a dict field that shares a reserved-ish name,
use `get obj "title"` instead of `obj\title`.

## Appending to a dictionary-in-block: wrap with `@[...]`

**Project experience.** `store\feeds ++ feed` (where `feed` is a dictionary and
`feeds` a block) can **splice/open** the dictionary into the block instead of
appending it as one item. Append a block-wrapped value:

```arturo
store\feeds ++ @[feed]
```

## `serve` handlers must return strings

**Verified** (`Net.nim`). The `serve` route handler should return a **string**
body. Returning a dictionary (`#[status: body:]`) is not handled as expected on
0.10 mini and can produce HTTP 500. Start a server with:

```arturo
serve.port: 8765 [     ; port is an attribute
    GET "/" [ "home" ]
    POST "/api/feeds" $[url][ ... ]   ; url comes from the query string
]
```

Default port is 18966; set `.port:` explicitly.

## HTTP: use `request` first, curl as fallback

**Verified** (`Net.nim`). `request` takes **two** args (url + data):

```arturo
r: request.get.timeout: 25 .agent: "AetherRSS/1.0" url ø
; r is a dictionary: status / body / headers; may be null on failure
```

Pattern: try `request` (native Net), and if it fails (or returns `null`), fall
back to a curl command. The **mini** build often returns `null` for HTTPS
`request`, so a curl fallback is important there. Build curl args with `++`
concatenation, not `~{|url|}` (template would execute interpolation).

## Read-state: don't rely on a `:store` handle inside functions

**Verified** (`Collections.nim`). `key?` accepts only `:dictionary`/`:object`,
not a `:store` (SQLite) value, so a DB handle can't be checked like a dict.
Also, `db: store.json "data/readstate"` inside a function frequently binds the
**string path** `"data/readstate"` rather than a handle (see the `do [..]`
note above). For simple read/unread state, keep a JSON array of link strings on
disk (`data/seen.json`) with `loadSeen`/`saveSeen` helpers, and mark items via
a `seen` field. This avoids DB-handle pitfalls entirely.

## A minimal HTTP+JSON+serve scaffold

```arturo
; load & save JSON state
saveState: function [path val][
    write.json.compact val path
]
loadState: function [path][
    if exists? path -> do [parse read path]
    else -> []
]

; one endpoint
serve.port: 8765 [
    GET "/api/items" $[
        items: loadState "data/items.json"
        print render.json items      ; returns a JSON string body
    ]
]
```

Query `info 'request`, `info 'serve`, `info 'write`, `info 'parse`, and
`info 'render` on your target build before relying on exact attribute names.
