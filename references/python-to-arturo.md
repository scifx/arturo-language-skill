# Python → Arturo comparison

> See also `in-a-nutshell-vs-python.md` for an execution-verified, side-by-side
> 15-minute tour (values, arithmetic, loops, strings, blocks, functions, custom
> types) with observed outputs. This file is the compact conceptual map.

This is a conceptual translation map, not a claim of identical semantics.

| Intent | Python | Arturo |
|---|---|---|
| Bind variable | `x = 3` | `x: 3` |
| Equality | `x == 3` | `x = 3` |
| Inequality | `x != 3` | `x <> 3` |
| Null | `None` | `null` |
| Booleans | `True`, `False` | `true`, `false` (also `maybe`) |
| Comment | `# text` | `; text` |
| List-ish block | `[1, 2, 3]` | `[1 2 3]` |
| Dict | `{"name": "Ada"}` | `#[name: "Ada"]` |
| Inclusive range | `range(1, 6)` | `1..5` |
| Function | `def f(x): return x*x` | `f: function [x][x*x]` |
| Lambda/map | `[f(x) for x in xs]` | `map xs 'x -> f x` |
| Filter | `[x for x in xs if p(x)]` | `select xs 'x -> p x` |
| For loop | `for x in xs:` | `loop xs 'x [...]` |
| While | `while cond:` | `while [cond][...]` |
| Conditional | `if cond: ...` | `if cond [...]` |
| Ternary | `a if cond else b` | `cond ? [a] [b]` or `cond ? -> a -> b` |
| f-string | `f"Hi {name}"` | `~"Hi |name|"` |
| Length | `len(xs)` | `size xs` |
| First/last | `xs[0]`, `xs[-1]` | `first xs`, `last xs` |
| Index/member | `xs[i]`, `obj.x` | `xs\[i]`, `obj\x` |
| Append copy/in-place | `xs + [x]`, `xs.append(x)` | `xs ++ x`, `'xs ++ x` |
| Type conversion | `int(s)` | `to :integer s` |
| Type check | `isinstance(x, int)` | `integer? x` |
| Import package | `import pkg` | `import "pkg"!` |
| Print | `print(x)` | `print x` |
| Integer/floor division | `35 // 4` | `35 / 4` |
| Floating division | `35 / 4` | `35 // 4` |
| Exponentiation | `2 ** 5` | `2 ^ 5` |
| Modulo | `5 % 3` | `5 % 3` |

## Translation strategy

1. Translate the **data model**, not punctuation: Python lists may become Arturo blocks, dictionaries, ranges, or evaluated arrays.
2. Replace nesting with prefix calls, then add parentheses where right-to-left evaluation could surprise.
3. Replace comprehensions with `map`, `select`, `fold`, `arrange`, `cluster`, etc.; query each signature.
4. Decide whether mutation is intended. Arturo mutating calls commonly take literals: `'xs`, `'counter`, or path literals.
5. Replace methods (`s.upper()`) with functions (`upper s`) unless working with an Arturo custom object method.
6. Test arithmetic division explicitly.

## Examples

### FizzBuzz

Python:

```python
for n in range(1, 101):
    if n % 15 == 0: print("FizzBuzz")
    elif n % 3 == 0: print("Fizz")
    elif n % 5 == 0: print("Buzz")
    else: print(n)
```

Arturo:

```arturo
loop 1..100 'n [
    when [
        zero? n % 15 -> print "FizzBuzz"
        zero? n % 3  -> print "Fizz"
        zero? n % 5  -> print "Buzz"
        true         -> print n
    ]
]
```

### Transform/filter/sum

Python:

```python
sum(x*x for x in range(1, 11) if x % 2 == 0)
```

Arturo (clear intermediate form):

```arturo
evens: select 1..10 'x -> even? x
squares: map evens 'x -> x*x
print sum squares
```

### Word counts

Python:

```python
counts = {}
for word in text.split():
    counts[word] = counts.get(word, 0) + 1
```

Arturo APIs for dictionary lookup/update can vary in idiom; do not transliterate blindly. Query `split`, `get`, `key?`, and `set`, then test against the target runtime.
