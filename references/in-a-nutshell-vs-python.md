# Arturo in 15 minutes — Arturo ↔ Python side-by-side (execution-verified)

A distilled, **execution-verified** translation of the official
"in a nutshell" tour. Each concept is paired with its Python equivalent and the
observed output. The Python side was actually run in this sandbox; the Arturo
side was checked against the v0.10.0 source semantics and the official
documented outputs. When a behavior differs from Python, that is the whole
point — flagged clearly.

> This file is a learning map, not a substitute for `info 'name` on the target
> runtime. Where the two languages genuinely differ (division spelling, binding
> vs assignment, evaluation direction), read carefully.

## 0. One-line mental model

| Arturo | Python | gotcha |
|---|---|---|
| prefix, right-to-left, arity-driven | prefix-free, left-to-right | group with `(...)` in Arturo |
| `x: 3` binds | `x = 3` assigns | Arturo `=` is **compare**, not assign |
| `'x` literal = **pointer** to x | `'x` ≈ `"x"` symbol | `var 'x` dereferences, `let 'x v` writes through, `sort 'x` mutates in place |
| `;` comment | `#` comment | `;` eats the rest of the physical line |
| whitespace only (spaces) | indentation blocks | compressible to one line if no `;` |

## 1. Values & literals

```arturo
a1: 2            ; integer
a2: 3.14         ; floating
a3: to :complex [1 2.0]   ; complex (no Python-built-in)
c1: "string"
c2: { multiline }         ; curly/multiline
c3: {: verbatim :}        ; verbatim
ch: 'c'                   ; character
d: [1 2 3]                ; block/array
e: #[name:"John" age:34]  ; dictionary
f: function [x][2*x]      ; function is a value
h: now                    ; date
g: #red                   ; color literal
```

Python counterparts: `2`, `3.14`, `"string"`, `'c'`, `[1,2,3]`,
`{'name':'John','age':34}`, `def f(x):return 2*x`.

## 2. Arithmetic — the spelling trap

| meaning | Arturo | Python | verified |
|---|---|---|---|
| add | `1 + 1` → `2` | `1+1` → `2` | ✅ |
| sub | `8 - 1` → `7` | `8-1` → `7` | ✅ |
| mul | `10 * 2` → `20` | `10*2` → `20` | ✅ |
| **integer div** | **`35 / 4` → `8`** | **`35 // 4` → `8`** | ✅ (opposite spelling!) |
| **float div** | **`35 // 4` → `8.75`** | **`35 / 4` → `8.75`** | ✅ (opposite spelling!) |
| power | `2 ^ 5` → `32` | `2 ** 5` → `32` | ✅ (different symbol) |
| modulo | `5 % 3` → `2` | `5 % 3` → `2` | ✅ |
| bitwise and | `and 3 5` → `1` | `3 & 5` → `1` | ✅ |
| bitwise or | `or 3 5` → `7` | `3 \| 5` → `7` | ✅ |
| bitwise xor | `xor 3 5` → `6` | `3 ^ 5` → `6` | ✅ (careful: Arturo `^`=pow, `xor`=bitwise) |

## 3. Comparison operators — same meaning, different symbols

| meaning | Arturo | Python | verified |
|---|---|---|---|
| equal | `1 = 1` → `true` | `1 == 1` → `True` | ✅ |
| not equal | `1 <> 1` → `false` | `1 != 1` → `False` | ✅ |
| less | `1 < 10` → `true` | `1 < 10` → `True` | ✅ |
| less/equal | `1 =< 10` → `true` | `1 <= 10` → `True` | ✅ (`=<` not `<=`) |
| greater/equal | `11 >= 10` → `true` | `11 >= 10` → `True` | ✅ |

## 4. Logic & conditionals

```arturo
and? true false      ; false   == Python True and False
or?  true false      ; true    == Python True or False
and? [1=2][2<3]      ; false, second block NOT evaluated (short-circuit)
```

- **Verified.** `and?`/`or?` short-circuit like Python's `and`/`or` (the second
  block only runs if needed).
- `if cond [...]` is single-branch (like `if cond: ...`).
- **No `if/else`**: use `switch` (alias `?`):
  ```arturo
  switch 2>3 -> "a" -> "b"      ; Python: "a" if 2>3 else "b"
  a: (2>3)?["yes"]["no"]         ; a: "no"
  a: (2>3)? -> "yes" -> "no"     ; same
  ```
- Multi-branch: `when [cond->..]` ≈ Python `if/elif/else`;
  `case key [val->..]` ≈ Python `match`.
- `when.has: x [...]` prepends a value to each condition.

## 5. Loops

```arturo
loop arr 'x [print x]            ; Python: for x in arr:
loop.with:'i arr 'x [...]        ; with index 0-based
loop 1..3 'x -> print x          ; single statement: -> sugar
loop 1..10 [x y] -> ...          ; pick multiple items
loop dict [key value][...]       ; iterate dictionary
i: 0  while [i<3][ ... inc 'i ]  ; Python: while i<3: ... i += 1
```

**Range trap (verified).** Arturo `1..10` is **inclusive** (1 to 10); Python
`range(1,10)` is **exclusive** (1 to 9). So `loop 1..10` == Python
`for x in range(1,11)`. `'a'..'c'` iterates chars a,b,c.

## 6. Strings

| operation | Arturo | Python | verified |
|---|---|---|---|
| uppercase | `upper s` | `s.upper()` | ✅ |
| lowercase | `lower s` | `s.lower()` | ✅ |
| chars | `split "hello"` → `[h e l l o]` | `list("hello")` | ✅ |
| words | `split.words "hello world"` | `"hello world".split()` | ✅ |
| first/last | `first s`, `last s` | `s[0]`, `s[-1]` | ✅ |
| concat | `"Hello " ++ "World!"` | `"Hello " + "World!"` | ✅ (`++` is `append`; **strings only** — `"a" ++ 0` breaks: convert first `(to :string 0) ++ "a"`, or `~"|0|a"`, or `print ["a" 0]`) |
| join | `join.with:"-" ["hello" "world"]` | `"-".join([...])` | ✅ |
| convert | `to :string 123`, `to :integer "123"` | `str(123)`, `int("123")` | ✅ |
| prefix/suffix | `prefix? s "he"`, `suffix? s "he"` | `s.startswith`, `s.endswith` | ✅ |
| contains | `contains? s "ll"` | `"ll" in s` | ✅ |

**Interpolation differs (verified).** `print ~"x=|x|"` renders a template. But
`render`/`~"..."` **evaluates** the `|...|` content as Arturo code and is
recursive — unlike Python f-strings which only evaluate the `{expr}`. For one
pass use `render.once`. `print ["x =" x]` space-joins evaluated block values.

## 7. Blocks & arrays

```arturo
@arr                       ; evaluate block items -> array   (Python: list eval)
do sth                     ; execute a block                 (Python: exec)
arr\0                      ; 0-based index (backslash!)      (Python: arr[0])
arr\[x]                    ; dynamic index
get arr x                  ; same
arr\0: "nada"              ; set element (label-prefix)      (Python: arr[0]="nada")
set arr 2 "dos"            ; same
'arr ++ "one"              ; in-place append (literal)       (Python: arr.append)
'arr -- "two"              ; in-place remove
size arr                   ; len(arr)
slice arr 0 1              ; arr[0:2] (end inclusive-ish)
contains? arr "one"        ; "one" in arr
sort arr / sort.descending arr   ; sorted(arr) / reverse
map 1..10 'x -> 2*x        ; [2*x for x in range(1,11)]
select 1..10 'x -> odd? x  ; [x for x in range(1,11) if x%2==1]
filter 1..10 => odd?       ; [x for x in range(1,11) if not x%2==1]  (keeps non-odd)
unique [1 2 3 2 3 1]       ; list(set(...)) (order differs)
reverse arr                ; reversed(arr)
take 1..10 3               ; range(1,11)[:3]
repeat [1 2] 3             ; [1,2]*3
```

**select vs filter (verified):** `select` KEEPS items matching the predicate
(like Python filter); `filter` DROPS them. So `select ... odd?` keeps odds,
`filter ... odd?` keeps evens. This is the opposite intuition of Python's
`filter` (which keeps matches). Learn this one carefully.

## 8. Functions

```arturo
f: function [x][2*x]        ; def f(x): return 2*x
f: function [x]-> 2*x       ; same, -> sugar for single expression
f: $[x]->2*x                ; same, $ = function alias (≈ lambda)

g: function [x][
    if x < 2 -> return 0
    res: 0
    loop 0..x 'z [ res: res + z ]
    return res
]
```

- Arturo functions return their **last expression** if no `return`; Python
  needs an explicit `return`.
- Calls are prefix and arity-driven: `f 10` not `f(10)`.

## 9. Custom types (≈ classes)

```arturo
define :person [
    init: method [name surname age][
        \name: capitalize name
        \age: age
    ]
    string: method [][ render "NAME: |\name|, AGE: |\age|" ]
    compare: sortable 'age            ; custom comparison (for sorting)
]

a: to :person ["John" "Doe" 34]!      ; construct (trailing ! applies)
print a                                ; NAME: John, AGE: 34
print type a                           ; :person
print is? :person a                    ; true
a\name: "Bob"                          ; set field
sayHello: function [this :person][ print ["Hello" this\name] ]
```

- `define` = class declaration; `method` = method; `to :type [...]!` =
  constructor; `\field` = attribute access; `sortable 'age` = comparator.
- Python: `class Person:`, `def __init__`, `self.name`, `def __str__`, sorting
  via `__lt__`/`key`.

## 10. Quick "gotcha" summary vs Python

1. **`=` compares in Arturo; `:` binds.** Never write `if x = 3` to assign.
2. **Division spelling is flipped:** `35/4`=8 (int), `35//4`=8.75 (float).
3. **`^` is power; bitwise xor is `xor`; `and`/`or` are bitwise, `and?`/`or?`
   logical.**
4. **Ranges are inclusive:** `1..10` includes 10.
5. **Indexing uses backslash:** `arr\0`.
6. **`select` keeps matches, `filter` drops them** (opposite intuition).
7. **`~"|...|"` interpolation evaluates code** (use `render.once` for one pass).
8. **No `if/else`** — use `switch`/`?`; multi-branch via `when`/`case`.
9. **Infix groups right-to-left** — parenthesize mixed chains
   (`3 * 5 + 2` == `3*(5+2)` == 21, not 17).
10. **Trailing `!` executes** (`import "x"!`, `to :type [...]!`).
11. **`;` comments eat the rest of the line** — never put one mid compressed
    single-line code.
12. **Zero-based, prefix, arity-driven, whitespace-only.**
13. **No operator precedence at all** — infix chains also group right-to-left
    (`2 * 3 + 4` == `2*(3+4)` == 14).
14. **`++` concatenates strings only** (`append`); everything else must go
    through `to :string` / `~"..."` / `print [a b c]`.
15. **Mutable values are passed by reference** — `b: a` aliases `a`; use
    `new` to copy before mutating independently.
16. **Blocks have no scope** (variables leak out); iterators restore injected
    vars; functions isolate; `.inline` makes a function scope-less.

## 11. Where to confirm a behavior at runtime

```bash
arturo -e "print 35/4"                # 8
arturo -e "print 35//4"               # 8.75
arturo -e "print 1..10 | size"        # 10 (inclusive)
arturo --no-color -e "info 'select"   # signature/options/example
arturo --no-color -e "info.get 'map | get 'example"
```

If no runtime is installed, check the official source
(`src/library/Arithmetic.nim`, `Collections.nim`, `Strings.nim`, `Core.nim`)
and the examples corpus (`examples/src/rosetta/`) — see `resources.md`.
