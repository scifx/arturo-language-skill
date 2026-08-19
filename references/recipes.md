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

The runtime-verified equivalents of Python's `json.loads`/`json.dumps` are:

```arturo
; json.loads(s)  ->  read.json s          (parses a JSON *string* or a file path)
j: read.json "{\"a\": 1}"
j: read.json ./"tools.json"

; json.dumps(v)  ->  write.json v null    (null file arg => return the string)
s: write.json #[a: 1] null

; json.dump(v, f)  ->  write.json v "f.json"  (or .compact for minified)
write.json.compact val "data/_out.json"

; TOML config    ->  read.toml "config.toml"
c: read.toml ./"config.toml"
print c\local\model
```

**Do not use `parse.json`** — `parse` only has `.data` here, so `parse.json`
silently returns the input string unchanged. Use `read.json` for JSON text.
Query `info 'parse`, `info 'read`, `info 'write`, `info 'to` on your target
build before relying on attribute names.

## Main-guard / running as a script

```arturo
if standalone? [
    ; demo/entry code — only runs when this file is the main script
    print ai "你是谁？"
]
```

`standalone?` is the Arturo equivalent of Python's
`if __name__ == "__main__":`.

## Shell commands with structured output

```arturo
out: execute.code "ls -la"        ; dictionary with \output and \code
print out\output
print out\code
```

`execute` returns the raw string; `.code` returns `#[output: ... code: ...]`.

## Dynamic import by variable path

```arturo
p: "./dynmod.art"
import p!                          ; computed path works
import ./{sibling/file}!           ; curly-brace relative import (bang outside)
```

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
