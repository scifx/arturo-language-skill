# Arturo HTTP, JSON, and server contracts (source-verified)

These contracts were checked against the Arturo v0.10.0 built-in declarations
and official examples. Query `info` and run a minimal test on the target build,
especially for network and Full-only behavior.

## Files and JSON: argument order matters

`write` always receives **content, then destination**. Its `.directory`,
`.json`, `.compact`, and `.append` forms are attributes, not alternate arities.

```arturo
write "hello" "data/message.txt"
write.directory null "data"
write.json state "data/state.json"
write.json.compact state "data/state.json"
state: read.json "data/state.json"
```

For in-memory encoding, official v0.10.0 code uses `null` first; this returns
the encoded JSON string instead of writing a file:

```arturo
body: write.json null state
```

Keep this form distinct from the normal file-writing form above, and query
`info 'write` when targeting another version.

`parse` parses Arturo source/data syntax; use `read.json` for a JSON file rather
than assuming `parse read path` is JSON decoding.

## HTTP client: `request` has two positional arguments

`request` receives **URL, then data** and returns a response dictionary or
`null`. Its method, headers, agent, timeout, proxy, certificate, and raw modes
are attributes.

```arturo
response: request.get.timeout:25 "https://example.com/api" null
if response <> null [
    print response\status
    print response\body
]
```

For query/form data, pass a dictionary as the second argument. Query
`info 'request` before choosing `.json`, `.headers:`, or another attribute.
HTTPS is unavailable in Mini builds; use Full and test TLS support in the
actual environment.

## Server: route handlers and response values

`serve` takes a routes block/function and `.port:` is an attribute. According
to the v0.10.0 declaration and official example, a handler may return either:

- a string body; or
- a dictionary with `body`, `status`, and `headers` fields.

```arturo
serve .port:8765 [
    GET "/" ["home"]

    GET "/api/items" [
        items: read.json "data/items.json"
        write.json null items
    ]
]
```

A response dictionary shape is:

```arturo
#[
    body: "created"
    status: 201
    headers: #[]
]
```

Do not encode undocumented framework conventions into generated code. Start
with a string response, then verify status/header behavior on the target Full
runtime.

## Conditionals: no `else` keyword

`if` is one-branch. Use `switch`/`?` for two-way flow:

```arturo
loadState: function [path][
    (exists? path)?
        -> read.json path
        -> []
]
```

Use `when` or `case` for multiple branches.

## Reliable explicit calls

Ordinary assignment calls are valid and used in official examples:

```arturo
response: request url null
body: read.json response\body
```

When generated code becomes hard to parse, use parentheses or `do [...]` to
make evaluation explicit, but do not claim every bare user-function assignment
is broken:

```arturo
result: do [transform value]
result: (transform value)
```

`call` takes a function and a parameter block; query it before using a literal
function name or dynamically built argument list.

## Regex and template safety

A regex literal is `{/pattern/}`. In v0.10.0's parser, the first literal `}`
ends the curly literal, so keep `}` out of that form or build a regex from a
plain string with `to :regex`. Use inline flags such as `(?i)` rather than
assuming trailing regex flags work on every build.

Do not use `render` (`~"..."`) merely to concatenate untrusted URLs or regex
fragments. Interpolation regions are evaluated as Arturo code and rendering is
recursive by default. Prefer ordinary concatenation or simple pre-bound values;
use `render.once` when only one rendering pass is intended.

## Build and evidence boundary

The repository's deterministic runtime suite used Mini 0.10.0 and does not
exercise HTTPS or a live server. The contracts above are source/official-example
verified; deployment behavior, TLS, sockets, response transport, ports, and
filesystem permissions must be runtime-tested on the target environment.
