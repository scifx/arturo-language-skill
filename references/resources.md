# Arturo official resource and URL map

Verified 2026-08-19. Stable release shown by the official site: **0.10.0 “Arizona Bark”**.

## Quick navigation map (find the right place fast)

Use this to jump straight to the source for a given need — no searching.

| What you need | Where to look | Link |
|---|---|---|
| Run/local help for any symbol | `info 'x`, `info.get 'x \| get 'example` (local, offline) | see `practical-rules.md` |
| Download / install Arturo | Official site or Releases | `https://arturo-lang.io/` · `https://github.com/arturo-lang/arturo/releases` |
| 15-minute language tour | In a nutshell | `https://arturo-lang.io/documentation/in-a-nutshell` |
| Language design & philosophy | Language reference | `https://arturo-lang.io/documentation/language` |
| CLI flags & package commands | Command line | `https://arturo-lang.io/documentation/command-line` |
| Every keyword with examples | Standard library index | `https://arturo-lang.io/documentation/library` |
| Module page (e.g. Core) | library + lowercased module | `https://arturo-lang.io/documentation/library/core` |
| 100+ worked examples | Examples browser | `https://arturo-lang.io/documentation/examples` |
| Rosetta Code idioms (real `.art`) | examples repo, `src/rosetta/` | `https://github.com/arturo-lang/examples/tree/main/src/rosetta` |
| Language/VM/library source | GitHub repo | `https://github.com/arturo-lang/arturo` |
| Syntax + full word-list cheat sheet (for AI training) | Dr. Kameleon's gist | `https://gist.github.com/drkameleon/93331d1da47493effaa3b7f7c562ed62` |
| Online playground (no install) | Playground | `https://arturo-lang.io/playground/` |

The **AI training material gist** (`https://gist.github.com/drkameleon/93331d1da47493effaa3b7f7c562ed62`) is the single best offline summary: it contains the full syntax overview plus a compact word-list reference. Download it once and keep it with the skill for fast lookups.

### Modularity / OOP pages (quick refs)

| Topic | Official page |
|---|---|
| `import` (packages, local files, `!`) | `https://arturo-lang.io/documentation/library/core/import` |
| `module` (create a module) | `https://arturo-lang.io/documentation/library/core/module` |
| `define` (custom types/classes) | `https://arturo-lang.io/documentation/library/types/define` |
| Exceptions / `try` / `error?` | `https://arturo-lang.io/documentation/library/exceptions/` |

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

## Install the runtime (fastest first)

**Official one-liner (Linux/macOS/FreeBSD/WSL/Git-Bash/MSYS2):**

```bash
curl -sSL https://get.arturo-lang.io | sh          # latest stable
curl -sSL https://get.arturo-lang.io/latest | sh   # nightly preview
```

Verify after installing:

```bash
arturo --version
```

Other routes, in order of preference:

1. **Pre-built binaries** — no install needed, just unzip and run. From the official site `https://arturo-lang.io/` (Download) or the GitHub Releases page `https://github.com/arturo-lang/arturo/releases`. Pick by OS + arch (e.g. `arturo-0.10.0-linux-amd64.zip`); nightly binaries live at `https://github.com/arturo-lang/nightly`.
2. **macOS Homebrew:** `brew install arturo`
3. **Arch Linux (AUR):** `yay -S arturo` or `paru -S arturo`
4. **Windows:** `curl -sSL https://get.arturo-lang.io/ps | powershell -c -`, or use the one-liner inside WSL/Git-Bash/MSYS2
5. **From source (last resort):** clone `https://github.com/arturo-lang/arturo` and run `./build.nims --install` (requires Nim plus GTK/webkit `-dev` libraries for the Full build; use `--mode mini` to avoid the GUI deps). Full instructions: `https://github.com/arturo-lang/arturo/wiki/Building-Arturo`.

> Note: there is no official Debian/Ubuntu `apt install arturo` package. On Debian/Ubuntu prefer the official installer or a pre-built binary. Do not claim `apt install arturo` works on those systems without verifying it in the actual environment.

Arturo's "installation" is effectively just a static binary: download → unzip → place on `$PATH` (e.g. `~/.arturo/bin/arturo` or `/usr/local/bin/arturo`) → run. Set `ARTURO_BIN` if the skill tools cannot auto-detect it from `PATH`.

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
