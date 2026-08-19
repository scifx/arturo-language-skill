# Arturo runtime: preferred source and dependency spec

Verified **2026-08-19** against the binary in the maintainer's distribution repo.

## Preferred source: scifx/arturo-bin

`https://github.com/scifx/arturo-bin` is the **preferred way to get an Arturo
runtime** (maintainer-uploaded prebuilt executable, kept in sync with this
skill). The repo contains a single file, `arturo`, at the root.

| Property | Value |
|---|---|
| Repository | `https://github.com/scifx/arturo-bin` |
| File | `arturo` (repo root) |
| Commit verified | `cc0849a870c6561b01c8d48e8216b4fe608723d0` (`main`, 2026-08-19) |
| Git blob SHA | `ed862400057c5e5baa6f388070a5860b5b144e79` |
| SHA-256 | `73bda27194bf0ae0dcc89550cfd590313f6e1c586f0f255e01e0b2b82388d3cb` |
| Size | 12,524,488 bytes |
| Format | ELF 64-bit LSB executable, x86-64, dynamically linked |
| Build variant | **Full** (includes the UI/webview stack; see §3) |

### Fetch routes (all verified in a restricted sandbox)

Use `scripts/get-arturo.sh` — it tries these in order and verifies the SHA-256:

1. `git clone --depth 1 --branch main https://github.com/scifx/arturo-bin.git`
   — works even where raw.githubusercontent.com is blocked.
2. Codeload tarball: `https://codeload.github.com/scifx/arturo-bin/tar.gz/refs/heads/main`
3. Raw file: `https://raw.githubusercontent.com/scifx/arturo-bin/main/arturo`
   (normal networks only; raw.githubusercontent.com is often firewalled).
4. GitHub API blob (needs `gh` CLI + auth):
   `gh api repos/scifx/arturo-bin/git/blobs/<blob-sha> -H "Accept: application/vnd.github.raw"`

After fetching, put the binary on `$PATH` (e.g. `~/.arturo/bin/arturo` or
`/usr/local/bin/arturo`) or set `ARTURO_BIN` for `bin/ahelp`.

## 1. Direct shared-library requirements (SONAMEs)

From `readelf -d` of the verified binary:

```
libm.so.6            libmpfr.so.6          libgmp.so.10
libwebkit2gtk-4.1.so.0   libgtk-3.so.0      libgdk-3.so.0
libglib-2.0.so.0     libjavascriptcoregtk-4.1.so.0
libgobject-2.0.so.0  libstdc++.so.6        libxcb.so.1
libgcc_s.so.1        libc.so.6
```

Transitive dependencies observed on Debian 12: `libXau.so.6`, `libXdmcp.so.6`,
`libbsd.so.0`, `libffi.so.8`, `libmd.so.0`, `libpcre2-8.so.0`.

## 2. Version floors (what "too old" means)

The verified binary was built on a newer toolchain than Debian 12 provides:

| Floor | Meaning | Debian 12 (bookworm) | Needs at least |
|---|---|---|---|
| `GLIBC_2.38` | glibc version | 2.36 ❌ | Debian 13 (trixie), Ubuntu 23.10+, Fedora 39+, Arch (2023-08+) |
| `GLIBCXX_3.4.32` | libstdc++ (GCC 13.2+) | 3.4.30 (GCC 12) ❌ | Debian 13 (GCC 13/14), Ubuntu 23.10+ (gcc-13), Fedora 39+ |

**Consequence (runtime-verified): the current Full binary cannot start on
Debian 12** — `ldd` reports both floors missing, and `libwebkit2gtk-4.1.so.0`
is absent. `./arturo --version` exits 127 (`error while loading shared
libraries: libwebkit2gtk-4.1.so.0`). This is an environment/dependency
limitation, not an Arturo defect.

## 3. Missing libraries on this sandbox (Debian 12) — full report

From `ldd` (all four are the UI stack; only needed by the **Full** build):

| Missing library | Debian/Ubuntu package | Fedora | Arch |
|---|---|---|---|
| `libwebkit2gtk-4.1.so.0` | `libwebkit2gtk-4.1-0` | `webkit2gtk4.1` | `webkit2gtk-4.1` |
| `libjavascriptcoregtk-4.1.so.0` | `libjavascriptcoregtk-4.1-0` | `webkit2gtk4.1` | `webkit2gtk-4.1` |
| `libgtk-3.so.0` | `libgtk-3-0` | `gtk3` | `gtk3` |
| `libgdk-3.so.0` | `libgtk-3-0` | `gtk3` | `gtk3` |

Install command on Debian/Ubuntu (needs apt network access):

```bash
sudo apt-get install -y libwebkit2gtk-4.1-0 libjavascriptcoregtk-4.1-0 libgtk-3-0
```

Already present on this sandbox (no action): `libm`, `libmpfr6`, `libgmp10`,
`libglib2.0-0`, `libgobject2.0-0`, `libxcb1`, `libgcc-s1`, `libstdc++6` (too
old: see §2), `libpcre2-8-0`, `libffi8`, `libxau6`, `libxdmcp6`, `libbsd0`,
`libmd0`.

> Note: on this sandbox the Debian mirrors are unreachable (egress allows only
> GitHub + PyPI + npm), so the four UI packages could not be apt-installed here.
> They would only help the Full build anyway — the glibc/libstdc++ floors in
> §2 still block it on Debian 12.

## 4. Mini (no-UI) build — what it removes, and how to produce it

The maintainer's next upload should be a **Mini build** (`./build.nims --mode
mini`): it has **no** webview/GTK/JS-Core dependencies, so the four UI
libraries above are not needed at all.

Remaining floors for Mini: same toolchain constraints as §2 — so build it **on
Debian 12 (glibc 2.36, GCC 12)** or any distro with glibc ≤ 2.36 so it runs on
Debian 12 and older:

```bash
git clone https://github.com/arturo-lang/arturo
cd arturo
./build.nims --mode mini        # requires Nim + libgmp/mpfr dev packages
./bin/arturo --version          # upload this binary to scifx/arturo-bin as `arturo`
```

Then update in this skill: SHA-256 pin (`config.env.example` +
`references/runtime-dependencies.md`) and the `ldd` report above. The official
Mini 0.10.0 ZIP is known to run on Debian 12, so a Mini build made on Debian 12
will too.

## 5. How to check a binary's dependencies quickly

```bash
ldd ./arturo                        # missing libs -> "not found"
objdump -T ./arturo | grep -oE 'GLIBC_[0-9.]+|GLIBCXX_[0-9.]+' | sort -uV | tail  # version floors
scripts/get-arturo.sh --check-only ./arturo   # one-shot report with hints
```

## 6. Other (fallback) install routes

If scifx/arturo-bin is unavailable, keep the official routes (see
`resources.md`): `curl -sSL https://get.arturo-lang.io | sh`, official
pre-built ZIPs, Homebrew, AUR, or building from source (last resort).
