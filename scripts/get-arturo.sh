#!/bin/sh
# get-arturo.sh — fetch the Arturo runtime from scifx/arturo-bin (preferred
# source), verify its SHA-256, and report any missing local libraries with
# per-distro install hints.
#
# Preferred source of the runtime: https://github.com/scifx/arturo-bin
# (maintainer-uploaded prebuilt binaries — the fastest reliable route).
#
# Usage:
#   scripts/get-arturo.sh                          # fetch+verify+dep-check; install to ~/.arturo/bin/arturo
#   ARTURO_DEST=/usr/local/bin/arturo scripts/get-arturo.sh
#   ARTURO_SHA256=<new-sha256> scripts/get-arturo.sh   # when upstream updates the binary
#   scripts/get-arturo.sh --check-only /path/to/arturo # just run the dependency check
#
# Requires only POSIX sh + common tools (curl or git, sha256sum/shasum, ldd).
# Python is not required. gh is optional (last-resort fetch route).
# Full dependency spec: references/runtime-dependencies.md

set -eu

SELF_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$SELF_DIR/.." && pwd)

# Optional user-local configuration (same file bin/ahelp reads).
if [ -f "$ROOT/config.env" ]; then
    # shellcheck disable=SC1091
    . "$ROOT/config.env"
fi

REPO_OWNER_REPO="scifx/arturo-bin"
BRANCH="main"
REPO_URL="https://github.com/${REPO_OWNER_REPO}.git"
CODELOAD_URL="https://codeload.github.com/${REPO_OWNER_REPO}/tar.gz/refs/heads/${BRANCH}"
RAW_URL="https://raw.githubusercontent.com/${REPO_OWNER_REPO}/${BRANCH}/arturo"
TARBALL_DIR="${REPO_OWNER_REPO#*/}-${BRANCH}"

# Pin for the Full (UI) build committed 2026-08-19 (commit cc0849a, 12,524,488 bytes).
# Update ARTURO_SHA256 (env or config.env) when the maintainer uploads a new
# binary — e.g. the Mini/no-UI build. See references/runtime-dependencies.md.
PIN_SHA256=${ARTURO_SHA256:-73bda27194bf0ae0dcc89550cfd590313f6e1c586f0f255e01e0b2b82388d3cb}
DEST=${ARTURO_DEST:-"$HOME/.arturo/bin/arturo"}

usage() {
    cat <<'EOF'
Usage: get-arturo.sh [--check-only PATH]
  --check-only PATH   only run the ldd dependency check on an existing binary
Environment:
  ARTURO_SHA256       expected sha256 of the downloaded binary (overrides pin)
  ARTURO_DEST         install path (default ~/.arturo/bin/arturo)
  ARTURO_BIN          runtime path used by the dependency check
EOF
}

sha256_of() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$1" | awk '{print $1}'
    else
        echo "no sha256sum/shasum found" >&2
        return 1
    fi
}

dep_check() {
    BIN=$1
    [ -f "$BIN" ] || { echo "not a file: $BIN" >&2; return 1; }
    [ -x "$BIN" ] || chmod +x "$BIN"
    echo "== Binary: $BIN"
    if SHA=$(sha256_of "$BIN"); then
        echo "   sha256: $SHA"
    fi
    MISSING=$(ldd "$BIN" 2>&1 || true)
    echo "== Missing shared libraries (ldd)"
    if ! printf '%s\n' "$MISSING" | grep -q '=> not found'; then
        echo "   (none — all direct libraries are present)"
    else
        printf '%s\n' "$MISSING" | grep '=> not found' | sed 's/^/   MISSING /'
    fi
    echo "== Version floors required by the binary but absent on this system"
    if printf '%s\n' "$MISSING" | grep -q "not found (required by"; then
        printf '%s\n' "$MISSING" | grep -oE "version \`[^']+' not found" \
            | sed -e 's/version `//' -e "s/' not found//" \
            | while read -r floor; do
                echo "   $floor  (too old on this distro)"
            done
    else
        echo "   (none — glibc/libstdc++ satisfy the binary)"
    fi
    echo "== Per-distro package hints for missing libraries"
    printf '%s\n' "$MISSING" | grep '=> not found' | grep -oE 'lib[^ ]+\.so[^ ]*' | sort -u | while read -r so; do
        case "$so" in
            libwebkit2gtk-4.1.so.0)        echo "   $so -> Debian/Ubuntu: libwebkit2gtk-4.1-0 | Fedora: webkit2gtk4.1 | Arch: webkit2gtk-4.1" ;;
            libjavascriptcoregtk-4.1.so.0) echo "   $so -> Debian/Ubuntu: libjavascriptcoregtk-4.1-0 | Fedora: webkit2gtk4.1 | Arch: webkit2gtk-4.1" ;;
            libgtk-3.so.0|libgdk-3.so.0)   echo "   $so -> Debian/Ubuntu: libgtk-3-0 | Fedora: gtk3 | Arch: gtk3" ;;
            *)                             echo "   $so -> check your distribution's package search" ;;
        esac
    done
    if printf '%s\n' "$MISSING" | grep -q "not found (required by"; then
        echo "== NOTE: a missing GLIBC_x.y / GLIBCXX_x.y floor means the distro is too old"
        echo "   for this binary (this sandbox: Debian 12 / glibc 2.36 / GCC 12)."
        echo "   Use a newer distro (Debian 13+, Ubuntu 23.10+) OR request a Mini/no-UI"
        echo "   build from the maintainer (no GUI libs; buildable on Debian 12 via"
        echo "   './build.nims --mode mini'). See references/runtime-dependencies.md."
    fi
}

if [ "${1:-}" = "--check-only" ]; then
    [ $# -eq 2 ] || { usage >&2; exit 2; }
    dep_check "$2"
    exit 0
fi

echo "== Fetching Arturo runtime from $REPO_OWNER_REPO (preferred source)"
TMPDIR_X=$(mktemp -d)
trap 'rm -rf "$TMPDIR_X"' EXIT

FETCHED=0
# 1) git clone — works even where raw.githubusercontent.com is blocked
if [ "$FETCHED" -eq 0 ] && command -v git >/dev/null 2>&1; then
    echo "   route 1/4: git clone $REPO_URL"
    if git clone --depth 1 --branch "$BRANCH" -q "$REPO_URL" "$TMPDIR_X/repo" 2>/dev/null \
        && [ -f "$TMPDIR_X/repo/arturo" ]; then
        cp "$TMPDIR_X/repo/arturo" "$TMPDIR_X/arturo"
        FETCHED=1
    fi
fi
# 2) codeload tarball — also works in restricted sandboxes
if [ "$FETCHED" -eq 0 ] && command -v curl >/dev/null 2>&1; then
    echo "   route 2/4: codeload tarball $CODELOAD_URL"
    if curl -fsSL "$CODELOAD_URL" -o "$TMPDIR_X/repo.tar.gz" 2>/dev/null \
        && tar -xzf "$TMPDIR_X/repo.tar.gz" -C "$TMPDIR_X" \
        && [ -f "$TMPDIR_X/$TARBALL_DIR/arturo" ]; then
        cp "$TMPDIR_X/$TARBALL_DIR/arturo" "$TMPDIR_X/arturo"
        FETCHED=1
    fi
fi
# 3) raw URL — on networks with unrestricted access
if [ "$FETCHED" -eq 0 ] && command -v curl >/dev/null 2>&1; then
    echo "   route 3/4: raw URL $RAW_URL"
    if curl -fsSL "$RAW_URL" -o "$TMPDIR_X/arturo" 2>/dev/null; then FETCHED=1; fi
fi
# 4) GitHub API git blob via gh — needs gh CLI + auth, but survives raw/Codeload blocks
if [ "$FETCHED" -eq 0 ] && command -v gh >/dev/null 2>&1; then
    echo "   route 4/4: GitHub API git blob (gh)"
    BLOB_SHA=$(gh api "repos/${REPO_OWNER_REPO}/contents/arturo" --jq '.sha' 2>/dev/null || true)
    if [ -n "$BLOB_SHA" ] \
        && gh api "repos/${REPO_OWNER_REPO}/git/blobs/${BLOB_SHA}" -H "Accept: application/vnd.github.raw" > "$TMPDIR_X/arturo" 2>/dev/null; then
        FETCHED=1
    fi
fi

if [ "$FETCHED" -eq 0 ]; then
    echo "ERROR: could not download the binary from $REPO_OWNER_REPO" >&2
    echo "       (tried git clone, codeload, raw URL, gh API)." >&2
    echo "       Ask the maintainer to upload the binary and/or add a GitHub Release." >&2
    exit 1
fi

echo "== Verifying sha256"
if ! ACTUAL=$(sha256_of "$TMPDIR_X/arturo"); then
    echo "ERROR: no sha256 tool available" >&2
    exit 1
fi
if [ "$ACTUAL" != "$PIN_SHA256" ]; then
    echo "WARNING: sha256 mismatch — binary changed upstream."
    echo "   expected: $PIN_SHA256"
    echo "   actual:   $ACTUAL"
    echo "   If this is the maintainer's new build (e.g. the Mini/no-UI version),"
    echo "   re-run with: ARTURO_SHA256=$ACTUAL scripts/get-arturo.sh"
    echo "   and update the pin in config.env.example / references/runtime-dependencies.md."
    exit 1
fi
echo "   OK: $ACTUAL"

mkdir -p "$(dirname "$DEST")"
cp "$TMPDIR_X/arturo" "$DEST"
chmod +x "$DEST"
echo "== Installed to $DEST"

dep_check "$DEST"

echo "== Try it:"
echo "   $DEST --version"
echo "   (set ARTURO_BIN=$DEST for bin/ahelp, or add the directory to PATH)"
