# Arturo runtime: bundled binaries and dependency spec

Verified **2026-08-19**. This skill ships its own prebuilt Arturo binaries in
`bin/` — the shortest path from clone to a working runtime, with no download
step at all.

## Preferred runtime: the binaries bundled in this repo

| Property | `bin/arturo` (Full, no UI) | `bin/arturo-mini` (Mini) |
|---|---|---|
| Version | `0.10.1-dev+43` (amd64/linux) | `0.10.1-dev+43` (amd64/linux) |
| Source | `scifx/Arturo-Future` commit `933420d` (main, 2026-08-19) | same |
| Toolchain | Nim 2.2.6 + GCC 12.2 (Debian 12), `--release` (LTO + strip + mimalloc) | same |
| Size | 6,519,792 bytes | 5,200,088 bytes |
| SHA-256 | `b7597e9d5ea3d0c0229e37c936518b12c0d69cb9ffe514fad63a9e08f2b0a38d` | `78fbbf467528a8b7e2cc83d5015f5d75c3c6165f7f188ef543b7bcae848705ad` |
| Glibc floor | ≥ 2.36 (Debian 12+, Ubuntu 22.04+) | ≥ 2.36 |
| Extra shared libs | `libgmp.so.10`, `libmpfr.so.6`, `libssl.so.3`, `libcrypto.so.3` (+ dlopen `libsqlite3.so.0`) | none (glibc base only) |

Use them directly:

```bash
./bin/arturo --version
export ARTURO_BIN="$PWD/bin/arturo"    # for bin/ahelp / scripts; ahelp auto-detects from PATH too
```

## 1. What the Full build includes (runtime-verified 2026-08-19)

Built from the fork's full build mode **minus the UI stack** (`WEBVIEW`,
`DIALOGS`, `CLIPBOARD` were removed — they need webkit2gtk/GTK/X11 dev headers
and are useless headless; this matches the upstream `--no-ui` intent):

| Feature | Module / lib | Verified result |
|---|---|---|
| Big integers | GMP (`libgmp.so.10`) | `print 2^300` → correct 91-digit result |
| Arbitrary floats | MPFR (`libmpfr.so.6`) | `sqrt 2.0` → `1.4142135623730951` |
| HTTPS / SSL | OpenSSL 3 (`libssl.so.3`/`libcrypto.so.3`, dynamic) | `request "https://api.github.com/..." #[]` → status 200 |
| SQLite databases | dlopen `libsqlite3.so.0` | create/insert/`SELECT count(*)` → `[3]` |
| Regex | PCRE (vendored static) | `match "hello123" {/[a-z]+[0-9]+/}` → works |
| Parsers (markdown/html/xml/toml/csv) | vendored | included |
| Crypto | vendored | `hash` builtins work |
| Package manager | — | included (`--package` in help) |

## 2. Missing libraries on this sandbox (Debian 12) — none

`ldd bin/arturo` and `ldd bin/arturo-mini` report **no** `not found` entries on
Debian 12. The previous scifx/arturo-bin upload (Full build on glibc 2.38)
required `libwebkit2gtk-4.1.so.0`, `libjavascriptcoregtk-4.1.so.0`,
`libgtk-3.so.0`, `libgdk-3.so.0` and glibc ≥ 2.38 — none of that applies to
the bundled binaries.

If a target host is missing the Full build's system libs:

| Library | Debian/Ubuntu | Fedora | Arch |
|---|---|---|---|
| `libgmp.so.10` | `libgmp10` | `gmp` | `gmp` |
| `libmpfr.so.6` | `libmpfr6` | `mpfr` | `mpfr` |
| `libssl.so.3` / `libcrypto.so.3` | `libssl3` | `openssl` | `openssl` |
| `libsqlite3.so.0` (dlopen) | `libsqlite3-0` | `sqlite-libs` | `sqlite` |

```bash
sudo apt-get install -y libgmp10 libmpfr6 libssl3 libsqlite3-0   # Debian/Ubuntu
scripts/get-arturo.sh --check-only bin/arturo                    # live missing-lib report
```

## 3. Why the fork needed patches to build on glibc 2.36 (rebuild notes)

The fork builds out of the box only on a newer toolchain (its vendored static
OpenSSL was built on glibc 2.38, and it expects system `gmp.h`/`mpfr.h` dev
headers). To reproduce the bundled binaries on Debian 12:

1. **`src/extras/gmp.h` + `src/extras/mpfr.h`** (generated) — ABI-identical
   local replacements for `libgmp-dev`/`libmpfr-dev`, generated from the Nim
   wrappers by `build-tools/gen_headers.py`: all 686+31 prototypes, the
   `#define foo __gmp_foo` symbol mapping exactly as in official gmp.h
   (emitted **before** prototypes so declarations expand — otherwise gcc
   implicit-int-truncates 64-bit pointers), and the inline functions
   (`mpq_numref`/`mpq_denref`/`mpz_sgn`/`mpq_sgn`/`mpf_sgn`/`mpz_odd_p`/
   `mpz_even_p`).
2. **`src/extras/gmp.nim` / `mpfr.nim`** — header pragma changed from
   `"<gmp.h>"` to `"\"gmp.h\""` so the wrapper uses the local headers.
3. **`.config/buildmode.nims`** — Full build no longer defines `WEBVIEW`,
   `DIALOGS`, `CLIPBOARD` (see above). GMP/ssl/SQLITE/PARSERS/DOCGEN kept.
4. **`src/library/Net.nim`** — Linux SSL switched from the vendored static
   `src/deps/openssl/*.a` (glibc 2.38-only, `__isoc23_strtol`) to dynamic
   `-lssl -lcrypto` against system OpenSSL 3.

Rebuild (Debian/Ubuntu):

```bash
sudo ln -sf /usr/lib/x86_64-linux-gnu/libgmp.so.10   /usr/lib/x86_64-linux-gnu/libgmp.so
sudo ln -sf /usr/lib/x86_64-linux-gnu/libmpfr.so.6  /usr/lib/x86_64-linux-gnu/libmpfr.so
sudo ln -sf /usr/lib/x86_64-linux-gnu/libssl.so.3    /usr/lib/x86_64-linux-gnu/libssl.so
sudo ln -sf /usr/lib/x86_64-linux-gnu/libcrypto.so.3 /usr/lib/x86_64-linux-gnu/libcrypto.so
nim build.nims -m full --release --log    # → bin/arturo (Full, no UI)
nim build.nims -m mini --release --log    # → bin/arturo-mini (Mini)
```

## 4. Mini build — what it removes

`--mode mini` defines `MINI` only: no GMP, no SSL/HTTPS, no SQLITE, no
PARSERS, no WEBVIEW/DIALOGS/CLIPBOARD, no DOCGEN, no package manager. Big-int
use raises "Number operation overflow", sqlite fails with a VM Error, https
returns null — all expected and runtime-verified. Use it where zero extra
dependencies matter (minimal containers) and core/collection/string/reflection
features are enough.

## 5. How to check a binary's dependencies quickly

```bash
ldd ./bin/arturo                          # missing libs -> "not found"
objdump -T ./bin/arturo | grep -oE 'GLIBC_[0-9.]+|GLIBCXX_[0-9.]+' | sort -uV | tail
scripts/get-arturo.sh --check-only ./bin/arturo   # one-shot report with hints
```

## 6. Fallback install routes

If the bundled binaries are unavailable (different OS/arch), official routes
(see `resources.md`): `curl -sSL https://get.arturo-lang.io | sh`, official
pre-built ZIPs, Homebrew, AUR, or building from source (last resort).
