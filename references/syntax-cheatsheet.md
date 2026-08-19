# Arturo syntax and evaluation cheat sheet

## Values and binding

```arturo
x: 42                       ; bind x
name: "Ada"
ch: 'A'                     ; character
wordLiteral: 'x             ; literal word, used as data/reference
kind: :integer              ; type value
items: [1 2 3]              ; block (data/code)
user: #[name: "Ada" age: 37] ; dictionary
r: 1..10                    ; inclusive range
nothing: null
flag: true                  ; also false, maybe
version: 0.10.0
color: #FF8800              ; or #red
unit: `m
length: 12`cm
```

A colon is overloaded by lexical position: `x:` is a label/assignment form; `:integer` is a type literal; infix `:` aliases `let`.

## Evaluation model

Arturo evaluates **right-to-left** and has **no operator precedence at all** —
infix operators (`+` `*` `=` ...) are just aliases for prefix functions, so
they group right-to-left too. Calls are prefix and arity-driven:

```arturo
print square 5              ; print (square 5)
print 2 * 3 + 4             ; 14 — right-to-left: 2 * (3 + 4), NOT (2*3)+4
print (2 * 3) + 4           ; 10 — parenthesize to force the grouping you want
```

There is no "standard math precedence" to fall back on: `2 * 3 + 4` is **14**
in Arturo, exactly like `2 * (3 + 4)`. When a mixed infix chain's result
matters, parenthesize it.

Blocks do not execute automatically:

```arturo
code: [print "hi"]
do code                      ; executes
values: [1 1+1 1+1+1]
print @values                ; evaluates items => 1 2 3
```

## Functions and methods

```arturo
add2: function [x][x + 2]
add2: $[x][x + 2]            ; `$` aliases function

addNumbers: function [
    x :integer :floating
    y :integer :floating
][x + y]
```

Functions return their final expression unless control flow returns earlier. Separate parameter names with spaces or commas.

## Calls, options, and sugar

```arturo
sort.descending xs           ; boolean attribute
join.with:"," xs             ; value-bearing attribute
if x=2 -> print "yes"        ; -> wraps one terminal value as block
1..5 | map => [2 * &]        ; pipe + implicit parameter sugar
```

Prefer explicit iterator parameters while debugging:

```arturo
map 1..5 'x [2*x]
map 1..5 'x -> 2*x
```

`=>` injects an implicit `&`; `->` wraps one terminal value. Pipes reverse the visual flow into normal calls. Explain the desugared form when teaching.

## Conditionals

```arturo
if x > 0 [print "positive"]
unless empty? xs [print first xs]

switch x > 0 -> "positive"
             -> "not positive"

case key [
    "a" -> print "A"
    "b" -> print "B"
    any -> print "other"
]

when [
    x < 0 -> print "negative"
    x = 0 -> print "zero"
    true  -> print "positive"
]

label: (x > 0)? -> "yes" -> "no"
value: maybeNull ?? fallback
```

Always verify `case`, `when`, `switch`, and logical helpers with `info` for the target version.

## Iteration and functional collection operations

```arturo
loop 1..3 'x [print x]
loop.with:'i items 'item [print [i item]]

squares: map 1..5 'x -> x*x
evens: select 1..10 'x -> even? x
total: fold 1..5 [acc x][acc + x]  ; seed via attribute: fold.seed:0 1..5 [acc x][acc + x]
```

Control words include `break`, `continue`, `return`, `while`, `until`, and `loop`. Query signatures because many iterator functions accept an optional params argument represented by `null`, literal, or block.

## Strings

```arturo
s: "hello"
multi: {
    indentation-normalized multiline text
}
verbatim: {:
  preserved verbatim
:}
regex: {/.../}                 ; regex literal — plain /.../ is division in this build
print ~"Hello |name|, 2+2 = |2+2|"
print ["Hello" name]         ; evaluates block and space-joins
print upper s
print split.words "a b"
print join.with:"," ["a" "b"]
```

`++` is `append`, so string concatenation works **only between strings**:
`"a" ++ "b"` → `"ab"`, but `"a" ++ 0` produces a broken value (silently in
`print`, and `type` of it can hang this build). Convert first:
`(to :string 0) ++ "a"`, or use `~"|0|a"`, or `print ["a" 0]`.

## Scope and in-place modification

```arturo
; blocks have NO scope: variables leak out
do [ x: 1 ]              ; x is visible after this block
print x                  ; 1

; iterators protect outer bindings, and restore them after the loop
loop.with:'i ["a" "b"] 'x [ print [i x] ]   ; 0 a / 1 b
print i                  ; ERROR — i is gone after the loop

; functions DO have their own scope; .inline removes it
helper: function [n][
    localVar: n * 2      ; invisible outside
    return localVar
]
helper: $[n].inline [ leaked: n ]  ; .inline = scope-less
print leaked             ; visible

; values are passed/assigned BY REFERENCE — `new` copies
a: [1 2 3]
b: a
' b ++ 9                  ; a is also [1 2 3 9] now
c: new a                  ; deep-ish copy
' c ++ 9                  ; a unchanged

; in-place mutation via literal: many built-ins accept 'name
sort 'a                   ; sorts a in place (no re-assignment needed)
' total + 5               ; in-place add
```

## Collections and paths

```arturo
xs: ["zero" "one" "two"]
print xs\0                   ; zero-based
print xs\[indexValue]
xs\0: "ZERO"
'xs ++ "three"              ; in-place append via literal
append 'xs "four"
'xs -- "one"

user: #[name: "Ada" tags: [dev admin]]
print user\name
user\age: 37
print keys user
print values user
```

The same backslash syntax is used for indexes, dictionary/object members, and paths. A leading/path literal can be used for in-place mutation.

## Objects/custom types

```arturo
define :person [
    init: method [name age][
        this\name: name
        this\age: age
    ]
    string: method [][~"|this\name| (|this\age|)"]
]

ada: to :person ["Ada" 37]!
print ada
```

Custom types can implement magic methods (`init`, `get`, `set`, comparisons, arithmetic, conversion, append/remove). Consult the Types docs before implementing them.

## Errors and introspection

```arturo
try [riskyOperation]
ensure [condition]            ; inspect runtime help before use
throw valueError "message"

info 'map
meta: info.get 'map
inspect meta
print type meta
print arity\map
print symbols
```

## Frequent traps

1. `=` compares; it does not assign.
2. `[...]` is not always an array literal in the Python sense—it may be deferred code.
3. Passing `x` resolves it; passing `'x` passes the word, often enabling mutation/binding.
4. Arturo's `/` performs integer-style division for integers (`35 / 4` → `8`); `//` floating division (`8.75`). This is the opposite of Python's spelling.
5. Strings/collections are zero-indexed.
6. There are no Python-style commas/colons/indent blocks; whitespace and arity drive parsing.
7. Do not assume left-to-right nested calls.
8. Mini builds omit UI, HTTPS, databases, package manager, and some parsers/precision.
