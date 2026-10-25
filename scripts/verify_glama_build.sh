#!/usr/bin/env bash
# verify_glama_build.sh — reproduce Glama's container build locally.
#
# Why this exists
# ---------------
# Glama does not build your project with plain pip. Its AI-inferred build spec is:
#   base image     debian:trixie-slim
#   build steps    uv venv && . .venv/bin/activate && uv pip install -e .
#   cmd            mcp-proxy -- .venv/bin/python <entrypoint>
# i.e. a *newer* toolchain (uv + latest setuptools) than most dev machines have.
# Anything that merely warns on an old setuptools can hard-fail there, and you
# cannot see the Glama build log until the listing is claimed. This script lets
# you reproduce that toolchain locally, before/independently of claiming.
#
# What it checks
#   1. `uv pip install -e .` succeeds (packaging metadata is valid for Glama)
#   2. the console entry point is installed and importable
#   3. the server actually answers `initialize` + `tools/list` over stdio
#
# Exit codes: 0 = all good, 1 = a real problem in the repo, 2 = local env issue.
#
# Usage:  bash scripts/verify_glama_build.sh
# Deps:   uv (https://docs.astral.sh/uv/) — the script tells you if it is missing.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

fail_env() { echo "[ENV]  $*" >&2; exit 2; }
fail_repo() { echo "[FAIL] $*" >&2; exit 1; }
ok() { echo "[ OK ]  $*"; }

command -v uv >/dev/null 2>&1 || fail_env "uv not found. Install: python3 -m pip install --break-system-packages uv"

echo "== repo: $REPO_ROOT"
echo "== uv:   $(uv --version)"

# Copy the tree without .git / venv / build artefacts, so we test the same
# inputs Glama would receive from a fresh clone.
tar -cf - -C "$REPO_ROOT" \
    --exclude=.git --exclude=.venv --exclude=build --exclude=dist \
    --exclude='*.egg-info' --exclude=__pycache__ . 2>/dev/null \
    | tar -xf - -C "$WORK" || fail_env "could not copy repo into $WORK"

cd "$WORK" || fail_env "cannot enter $WORK"

# Glama runs as root in a container where hardlinking is fine. Under proot /
# FUSE-backed filesystems hardlinks fail with "Operation not permitted", which
# is a sandbox limitation, not a packaging bug — so force copy mode.
export UV_LINK_MODE=copy
export UV_CACHE_DIR="$WORK/.uvcache"

echo
echo "== step 1/3: uv venv"
uv venv >/dev/null 2>&1 || fail_env "uv venv failed"

# shellcheck disable=SC1091
. .venv/bin/activate

echo "== step 2/3: uv pip install -e ."
if ! out="$(uv pip install -e . 2>&1)"; then
    echo "$out" >&2
    fail_repo "uv pip install -e . failed — Glama's build would fail the same way"
fi
echo "$out" | grep -E 'Installed|Built' | sed 's/^/        /'
ok "editable install succeeded: $(.venv/bin/python -c "
from importlib.metadata import version
print('nano-mcp-termux', version('nano-mcp-termux'))
")"

# Surface deprecation warnings that pip/uv hide. A *warning* here is not a
# failure (Glama tolerates it), but it is worth knowing about.
# NOTE: `uv venv` does not install setuptools, so the PEP 517 hook would fail
# with ModuleNotFoundError and silently report "no warnings". Install it first.
echo
echo "== warnings (informational, non-fatal)"
if uv pip install -q setuptools >/dev/null 2>&1; then
    warn="$(.venv/bin/python -W all -c "
import setuptools.build_meta as b, tempfile
b.prepare_metadata_for_build_wheel(tempfile.mkdtemp())
" 2>&1 | grep -iE 'deprecat|superseded' | sort -u)"
    if [ -n "$warn" ]; then
        echo "$warn" | sed 's/^/        /'
    else
        echo "        (none)"
    fi
else
    echo "        (skipped: could not install setuptools)"
fi

echo
echo "== step 3/3: stdio handshake + tools/list"
ENTRY="$(.venv/bin/python -c "
from importlib.metadata import distribution
d = distribution('nano-mcp-termux')
eps = [e for e in d.entry_points if e.group == 'console_scripts']
print(eps[0].name if eps else '')
")"
[ -n "$ENTRY" ] || fail_repo "no console_scripts entry point declared in pyproject.toml"
ok "entry point: $ENTRY"

RESP="$(printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"glama-verify","version":"0"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  | timeout 30 "$ENTRY" 2>/dev/null)" || fail_repo "server did not respond within 30s"

echo "$RESP" | .venv/bin/python -c "
import json, sys
tools, name = None, None
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        msg = json.loads(line)
    except json.JSONDecodeError:
        continue
    if msg.get('id') == 1:
        name = msg.get('result', {}).get('serverInfo', {}).get('name')
    if msg.get('id') == 2:
        tools = msg.get('result', {}).get('tools')
if name is None:
    print('[FAIL]  no initialize response'); sys.exit(1)
print('[ OK ]  initialize -> serverInfo.name =', name)
if not tools:
    print('[FAIL]  tools/list returned no tools; Glama TDQS has nothing to score')
    sys.exit(1)
print('[ OK ]  tools/list ->', len(tools), 'tools')
for t in tools:
    print('        - %-16s desc=%4d chars' % (t.get('name'), len(t.get('description') or '')))
" || exit 1

echo
echo "All checks passed: this repo builds and introspects under Glama's toolchain."
