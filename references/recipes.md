# Arturo practical recipes

Run `info 'FUNCTION` before adapting these to a different version.

## Script/REPL

```bash
arturo program.art
arturo --no-color -e 'print 2+2'
arturo                         # REPL
arturo --compile program.art   # experimental bytecode
arturo --execute program.bcode
arturo --bundle program.art --as myapp
```

## Read arguments and environment

```arturo
print args
print arg\0
print env
```

Query `info 'arg`, `info 'args`, and `info 'env` because access behavior and script-name inclusion matter.

## File I/O and paths

```arturo
text: read "input.txt"
write "output.txt" text
p: relative "data/input.txt"
print extract p
```

Before destructive code, query `read`, `write`, `exists?`, `file?`, `directory?`, `absolute`, `relative`, `extract`, `delete`, `move`, `copy`.

## HTTP/network

```arturo
body: read "https://example.com"
print body
```

Use Full build for HTTPS. Query `request`, `download`, `serve`, sockets functions, and returned types. Never assume Python `requests` semantics.

> For a real HTTP server + JSON + file-state project, see
> `references/web-and-http-patterns.md` (call via `do [...]`/`call`, `serve`
> returning strings, `write` two-arg rule, `request` two-arg, curl fallback,
> `{/.../}` regex `}` gotcha, read-state via JSON not `:store` handles).

## JSON/structured parsing

Arturo's `parse`/`to` operations are type/format sensitive. Query:

```arturo
info 'parse
info 'to
```

Then use the target runtime's documented attributes; do not invent `json.loads` equivalents.

## SQLite/database

Database support is Full-only. Query `database?`, `open`/database module entries, `execute`, `close`, and inspect returned values. Note that generic names such as `close` can belong to a specific module/context.

## Simple module/file import

```arturo
; local module.art defines pi and hello
import "module.art"!
hello "Ada"
print pi
```

Alternative legacy loading with `do relative "module.art"` may require using newly loaded functions inside a later `do [...]`; `import ...!` is usually clearer.

## Package import with isolation

```arturo
pkg: import.lean "dummy"!
print pkg\dummyFunc 10
```

## Pipelines

Readable explicit form:

```arturo
values: map 1..10 'x -> 2*x
values: select values 'x -> even? x
print values
```

Concise form after verification:

```arturo
1..10 | map => [2 * &]
      | select 'x -> even? x
      | print
```

## Custom type

```arturo
define :counter [
    init: method [start :integer][this\value: start]
    inc: method [][inc 'this\value]
    string: method [][to :string this\value]
]

c: to :counter [0]!
c\inc
print c
```

Check `define`, `method`, `to`, and magic methods against Types docs.

## Testing pattern

Arturo's separate `unitt` package is listed at https://unitt.pkgr.art/. For dependency-free smoke tests, print deterministic values and compare process output:

```bash
arturo --no-color tests/smoke.art > actual.txt
diff -u expected.txt actual.txt
```

For API discovery during a test:

```arturo
inspect info.get 'map
```
