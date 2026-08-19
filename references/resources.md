# Arturo official resource and URL map

Verified 2026-08-19. Stable release shown by the official site: **0.10.0 “Arizona Bark”**.

## Canonical sites

| Purpose | URL |
|---|---|
| Home/downloads | https://arturo-lang.io/ |
| Documentation hub | https://arturo-lang.io/documentation/ |
| Getting started/build variants | https://arturo-lang.io/documentation/getting-started |
| 15-minute tour | https://arturo-lang.io/documentation/in-a-nutshell |
| Language reference | https://arturo-lang.io/documentation/language |
| CLI/package commands | https://arturo-lang.io/documentation/command-line |
| Standard library/index | https://arturo-lang.io/documentation/library |
| Examples browser | https://arturo-lang.io/documentation/examples |
| Online playground | https://arturo-lang.io/playground/ |
| Package registry | https://pkgr.art/ |
| Package search | https://pkgr.art/search |
| Unix installer | https://get.arturo-lang.io |
| PowerShell installer | https://get.arturo-lang.io/ps |
| Nightly Unix installer | https://get.arturo-lang.io/latest |
| Nightly PowerShell installer | https://get.arturo-lang.io/latest/ps |

## Version-aware paths

The server recognizes these prefixes before the normal site path:

- no prefix: stable content, e.g. `/documentation/library/core/function`
- `/stable/...`: explicit stable tree
- `/latest/...`: current nightly/master-generated tree
- `/v<version>/...`: supported server pattern **only when that version tree has actually been deployed**
- `/test/...`: restricted deployment; do not depend on it

Direct checks on 2026-08-19 found `/stable/documentation/` and `/latest/documentation/` working, while `/v0.10.0/documentation/` and the old `/master/documentation/` route returned 404. Older search results for `/master/...` are stale. Prefer stable by default; use `/latest` deliberately. Never assume a `/vX.Y.Z` tree exists—HTTP-check it first.

Function pages follow `/documentation/library/<module>/<slug>`. Predicate `?` is normally slugged as `-` (e.g. `absolute?` → `absolute-`), and names are lowercased, but **do not derive URLs when the CSV can resolve them**. `library-index.csv` contains all 521 stable function/predicate/constant links extracted and HTTP-tested (521/521 returned 200). It also records latest-route status: 514 returned 200, while seven stable Sockets routes returned 404 under `/latest`.

## Standard-library modules

Stable index modules: Arithmetic, Bitwise, Collections, Colors, Comparison, Core, Crypto, Databases, Dates, Exceptions, Files, Io, Iterators, Logic, Net, Numbers, Paths, Quantities, Reflection, Sets, Sockets, Statistics, Strings, System, Types, Ui.

The current source tree also has Events, Streams, and Tasks modules; these may appear in `/latest` before the stable 0.10.0 index. This is why version selection matters.

## Source repositories

| Resource | URL | Verified shallow-clone commit |
|---|---|---|
| Language/VM/library/tests | https://github.com/arturo-lang/arturo | `f956424df49b3526044d54d57fa54c94a0cf74aa` |
| Official website/docs generator | https://github.com/arturo-lang/website | `e60be9a6f4775de79f5f60a3de75fc6c87e8f61b` |
| Official examples corpus | https://github.com/arturo-lang/examples | `60e7b92242e39fccdb764c505bb289e3a1e3d391` |
| Package registry data | https://github.com/arturo-lang/pkgr.art | `c4f45741ac141721d482316d669a575c6110c69e` |
| Nightly binaries | https://github.com/arturo-lang/nightly | — |
| Organization | https://github.com/arturo-lang | — |
| Issues | https://github.com/arturo-lang/arturo/issues | — |
| Discussions | https://github.com/arturo-lang/arturo/discussions | — |

Useful source paths:

- parser/evaluator/VM: `src/vm/`
- built-ins and embedded docs: `src/library/*.nim`
- tests: `tests/` (173 `.art` files in the checked snapshot)
- website prose: `website/src/pages/documentation/*.art`
- generated library pages: `website/src/pages/documentation/library/` (never edit manually)
- examples corpus: `examples/src/` (916 `.art` files in checked snapshot)
- registry package list: `pkgr.art/packages/list.art`

To inspect the implementation for a built-in, search its declaration:

```bash
rg 'builtin "map"' src/library
```

## Community/learning

- Discord: https://discord.gg/YdVK2CB
- Rosetta Code: https://rosettacode.org/wiki/Category:Arturo
- Exercism track: https://exercism.org/tracks/arturo
- Wiki/building: https://github.com/arturo-lang/arturo/wiki/Building-Arturo
- Contribution guide: https://github.com/arturo-lang/arturo/blob/master/docs/CONTRIBUTING.md

## Packages

Full build CLI:

```bash
arturo --package list
arturo --package remote
arturo --package install grafito
arturo --package uninstall grafito
arturo --package update
```

In code:

```arturo
import "dummy"!
import.version:0.0.3 "dummy"!
import.min.version:0.0.3 "dummy"!
import.latest "dummy"!
d: import.lean "dummy"!
```

Registry endpoints used by the packager include `https://pkgr.art/list.art`, `https://<package>.pkgr.art/spec`, and `https://<package>.pkgr.art/<version>/spec`.

## Installation/download caveat

Use links from the home page, not relative links copied from a nested docs page. Stable Linux amd64 checksums tested here:

- Full ZIP: `https://arturo-lang.io/files/arturo-0.10.0-linux-amd64.zip` — SHA-256 `764e484bf226ed14494b0e87601af4cd399da778d31ea059150bb07a621bb35d`
- Mini ZIP: `https://arturo-lang.io/files/arturo-0.10.0-linux-amd64-mini.zip` — SHA-256 `2ff02a02ec4b26916b2a45c585e1bfbcfe14bb5e29e1ea317ccf7ca3ae539077`
