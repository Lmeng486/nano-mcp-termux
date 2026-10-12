#!/usr/bin/env python3
"""Orphan-leak regression test for nano-mcp-termux.

Why this test exists
--------------------
v1.0.0 implemented `run()` with `subprocess.run(..., timeout=...)`. When the
timeout fires, Python kills only the *direct* child (the `sh -c` wrapper); any
grandchild the shell spawned is reparented to init and survives forever. On
Android that is exactly the process-leak class that trips the Phantom Process
Killer and eventually gets the whole app group killed.

v1.1.0 spawns each command with `start_new_session=True` and tears the timeout
path down with `os.killpg(pgid, SIGTERM)` -> `SIGKILL`, so the entire tree dies.

This test reproduces the exact tree:
    server -> sh payload.sh -> python spawner.py -> sleep 240
and asserts that ZERO 'spawner' processes remain after a timeout.

Exit code 0 = no leak (PASS).  Exit code 1 = leak detected (FAIL).
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.environ.get("MCP_SERVER", os.path.join(HERE, "nano_mcp_termux.py"))
LEGACY = os.environ.get("MCP_SERVER_LEGACY", os.path.join(HERE, "nano_mcp_termux_v10_backup.py"))
MARK = "nano_orphan_marker_486"

SPAWNER_SRC = """import subprocess, time
subprocess.Popen(["sleep", "240"])   # the grandchild that must not survive
time.sleep(240)
"""

PAYLOAD_SRC = """#!/bin/sh
# keep a real shell in the tree (no exec optimization), then spawn the grandchild
python3 {spawner}
"""


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def count_marked():
    """Count live processes whose cmdline mentions our marker."""
    n = 0
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open("/proc/%s/cmdline" % pid, "rb") as fh:
                cmdline = fh.read().decode("utf-8", "replace")
        except Exception:
            continue
        if MARK in cmdline:
            n += 1
    return n


def measure(module_path, modname, workdir, timeout=2):
    """Run one timeout-bounded command; return (leaked_grandchildren, elapsed)."""
    mod = load_module(module_path, modname)
    before = count_marked()
    t0 = time.time()
    mod.run("sh %s" % os.path.join(workdir, "payload.sh"), timeout=timeout)
    time.sleep(1.0)
    return count_marked() - before, time.time() - t0


def main():
    workdir = tempfile.mkdtemp(prefix="nano-orphan-")
    payload = os.path.join(workdir, "payload.sh")
    # The marker must appear in the grandchild's cmdline, so name it after MARK.
    marked = os.path.join(workdir, "%s.py" % MARK)
    with open(marked, "w") as fh:
        fh.write(SPAWNER_SRC)
    with open(payload, "w") as fh:
        fh.write(PAYLOAD_SRC.format(spawner=marked))
    os.chmod(payload, 0o755)

    leaks = {}
    for label, path, modname in (
        ("current", SERVER, "nano_under_test"),
        ("legacy", LEGACY, "nano_legacy"),
    ):
        if not os.path.exists(path):
            continue
        leaks[label], elapsed = measure(path, modname, workdir)
        print("%-8s %-28s leaked_grandchildren=%d  (elapsed %.1fs)"
              % (label, os.path.basename(path), leaks[label], elapsed))

    # always clean up survivors from the legacy run
    subprocess.run("pkill -f %s" % MARK, shell=True)
    time.sleep(0.5)

    print()
    if "legacy" in leaks:
        print("baseline v1.0.0 leak = %d (expected > 0 — that is the bug being fixed)" % leaks["legacy"])
    ok = leaks.get("current") == 0
    if ok:
        print("PASS: current server leaves 0 orphaned grandchildren after timeout")
    else:
        print("FAIL: current server leaked %d orphaned grandchildren" % leaks.get("current", -1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
