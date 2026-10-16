#!/usr/bin/env python3
"""nano-mcp-termux.py — Zero-dependency, single-file MCP server for
Termux/Android, Raspberry Pi, Linux, and Docker containers.

Protocol surface (stdio, newline-delimited JSON-RPC 2.0):
  initialize | notifications/initialized (silent) | ping | tools/list | tools/call

Design rules:
  1. stdout is SACRED: only JSON-RPC frames go to stdout. All logs -> stderr.
  2. Framing: one complete JSON-RPC message per line (json.dumps + newline),
     the stdio transport used by the official MCP SDKs. No embedded newlines.
  3. capabilities declare ONLY {"tools": {}} — minimal promise, max compatibility.
  4. Graceful degradation: probes never crash a tool call; missing data is marked.

Built-in modules (v1.1.0):
  [lifecycle] Process Lifecycle Guardian
      * every child is spawned in its own process group and reaped on timeout
        (kills the whole tree, not just the shell -> no orphan grandchildren)
      * watchdog on the parent pid: if the MCP client dies, this server exits
        instead of lingering as an orphan
      * optional idle self-termination: NANO_IDLE_TIMEOUT=SECONDS (0 = off)
      * server_health tool exposes pid/ppid/uptime/children/RSS and the
        Android "Phantom Process Killer" risk assessment
  [paths]     Android/Termux Path Adapter
      * resolves /sdcard <-> /storage/emulated/0 <-> $HOME/storage/shared
      * expands ~ / $HOME / $PREFIX / $TMPDIR, follows symlinks, finds the
        real mount backing a path
      * reports noexec mounts, case sensitivity and shell-quoting hazards
"""
import json
import os
import signal
import subprocess
import sys
import threading
import time

SUPPORTED_VERSIONS = ["2024-11-05", "2025-06-18", "2025-11-25"]
SERVER_NAME = "nano-mcp-termux"
SERVER_VERSION = "1.1.1"


# --------------------------------------------------------------- primitives

def log(msg):
    sys.stderr.write("[nano-mcp] " + str(msg) + "\n")
    sys.stderr.flush()


def send(obj):
    """One JSON-RPC message per line — MCP stdio wire format."""
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _flag(name):
    return name in sys.argv


def _env_int(name, default=0):
    try:
        return int(os.environ.get(name, "") or default)
    except Exception:
        return default


IDLE_TIMEOUT = _env_int("NANO_IDLE_TIMEOUT", 0)
WATCHDOG = not _flag("--no-watchdog")


# ------------------------------------------------------- environment probing

def detect_env():
    """Classify the runtime so downstream advice is accurate."""
    prefix = os.environ.get("PREFIX", "")
    if os.environ.get("PROOT_TMP_DIR") or os.environ.get("PROOT_LOADER"):
        return "proot"
    if os.environ.get("TERMUX_VERSION") or "com.termux" in prefix:
        return "termux"
    if os.path.exists("/system/build.prop") or os.path.exists("/system/bin/app_process"):
        return "android"
    return "linux"


def parse_mounts():
    """Parse /proc/self/mounts into dicts; spaces are escaped as \\040."""
    for fn in ("/proc/self/mounts", "/proc/mounts"):
        try:
            with open(fn) as f:
                out = []
                for line in f:
                    parts = line.split()
                    if len(parts) < 4:
                        continue
                    out.append({
                        "device": parts[0].replace("\\040", " "),
                        "mountpoint": parts[1].replace("\\040", " "),
                        "fstype": parts[2],
                        "options": parts[3].split(","),
                    })
                return out
        except Exception:
            continue
    return []


def find_mount(path, mounts):
    """Longest mountpoint that prefixes `path` (the mount actually backing it)."""
    best = None
    for m in mounts:
        mp = m["mountpoint"]
        if path == mp or path.startswith(mp.rstrip("/") + "/"):
            if best is None or len(mp) > len(best["mountpoint"]):
                best = m
    return best


def mount_summary(m):
    if not m:
        return None
    opts = m["options"]
    return {
        "device": m["device"],
        "mountpoint": m["mountpoint"],
        "fstype": m["fstype"],
        "noexec": "noexec" in opts,
        "ro": "ro" in opts,
        "case_insensitive": m["fstype"] in ("vfat", "exfat", "msdos", "ntfs", "fuseblk"),
    }


_ANDROID_ROOTS = ("/sdcard", "/storage/emulated/0", "/storage/self/primary", "/mnt/sdcard")


def android_alternates(path):
    """Every equivalent spelling of an Android shared-storage path."""
    alts = []
    for root in _ANDROID_ROOTS:
        if path == root:
            rel = ""
        elif path.startswith(root + "/"):
            rel = path[len(root) + 1:]
        else:
            continue
        for other in _ANDROID_ROOTS:
            if other == root:
                continue
            alts.append(other if not rel else other + "/" + rel)
    home = os.environ.get("HOME", "")
    if home:
        for root in _ANDROID_ROOTS:
            if path == root:
                alts.append(os.path.join(home, "storage", "shared"))
                break
            if path.startswith(root + "/"):
                alts.append(os.path.join(home, "storage", "shared", path[len(root) + 1:]))
                break
    seen, out = set(), []
    for a in alts:
        if a != path and a not in seen:
            seen.add(a)
            out.append(a)
    return out


def child_pids():
    """Direct children of this process (cgroup v2 exposes them here)."""
    try:
        with open("/proc/%d/task/%d/children" % (os.getpid(), os.getpid())) as f:
            return [int(x) for x in f.read().split()]
    except Exception:
        return []


def read_rss_kb():
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])
    except Exception:
        pass
    return None


# ------------------------------------------------------ [lifecycle] guardian

def _kill_tree(proc):
    """Kill a whole process group — the shell *and* whatever it spawned."""
    try:
        pgid = os.getpgid(proc.pid)
    except Exception:
        pgid = None
    if pgid is not None:
        try:
            os.killpg(pgid, signal.SIGTERM)
        except Exception:
            pass
    else:
        try:
            proc.terminate()
        except Exception:
            pass
    try:
        proc.wait(timeout=2)
        return
    except Exception:
        pass
    if pgid is not None:
        try:
            os.killpg(pgid, signal.SIGKILL)
            return
        except Exception:
            pass
    try:
        proc.kill()
    except Exception:
        pass


class LifecycleGuard(object):
    """Owns every child process and the exit path. Nothing else may exit."""

    def __init__(self, idle_timeout=0, watchdog=True):
        self.pid = os.getpid()
        self.ppid = os.getppid()
        self.start = time.time()
        self.last_activity = time.time()
        self.requests = 0
        self.tool_calls = 0
        self.stdin_eof = False
        self.idle_timeout = idle_timeout
        self.watchdog = watchdog
        self._children = set()
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._exiting = False

    # --- child bookkeeping
    def track(self, proc):
        with self._lock:
            self._children.add(proc)

    def untrack(self, proc):
        with self._lock:
            self._children.discard(proc)

    def live_children(self):
        with self._lock:
            return [p for p in self._children if p.poll() is None]

    def reap_all(self):
        """Kill every child we ever spawned (called on shutdown)."""
        with self._lock:
            procs = list(self._children)
        for p in procs:
            try:
                if p.poll() is None:
                    _kill_tree(p)
            except Exception:
                pass

    # --- activity
    def touch(self, tool_call=False):
        self.requests += 1
        if tool_call:
            self.tool_calls += 1
        self.last_activity = time.time()

    # --- watchdog
    def _watch_loop(self):
        while not self._stop.wait(2.0):
            try:
                if os.getppid() != self.ppid or not os.path.exists("/proc/%d" % self.ppid):
                    log("parent process %d is gone -> exiting to avoid becoming an orphan" % self.ppid)
                    self.shutdown(0)
                if self.idle_timeout and (time.time() - self.last_activity) > self.idle_timeout:
                    log("idle timeout (%ds) reached -> exiting" % self.idle_timeout)
                    self.shutdown(0)
            except Exception as e:
                log("watchdog error: " + repr(e))

    def start_watchdog(self):
        if not self.watchdog and not self.idle_timeout:
            return
        t = threading.Thread(target=self._watch_loop, name="nano-watchdog")
        t.daemon = True
        t.start()

    def shutdown(self, code=0):
        if self._exiting:
            return
        self._exiting = True
        self._stop.set()
        self.reap_all()
        os._exit(code)


GUARD = LifecycleGuard(IDLE_TIMEOUT, WATCHDOG)


def run(cmd, timeout=5):
    """Run a shell command in its own process group; reap the whole tree on
    timeout so nothing is ever left orphaned."""
    try:
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, text=True,
                                start_new_session=True)
    except Exception as e:
        log("spawn failed: " + cmd + " -> " + repr(e))
        return None
    GUARD.track(proc)
    try:
        out, _ = proc.communicate(timeout=timeout)
        return (out or "").strip()
    except subprocess.TimeoutExpired:
        log("timeout after %ss, killing process group: %s" % (timeout, cmd))
        _kill_tree(proc)
        return None
    except Exception as e:
        log("run failed: " + cmd + " -> " + repr(e))
        _kill_tree(proc)
        return None
    finally:
        GUARD.untrack(proc)


def phantom_info():
    """Android 12+ Phantom Process Killer: >32 children (or 214MB) gets the
    whole app group killed. Termux servers are the classic victim."""
    env = detect_env()
    kids = len(child_pids())
    # Field contract is stable across platforms: platform/risk/active_children/
    # soft_limit/note/mitigations are ALWAYS present, so clients never need to
    # special-case a non-Android host.
    mitigations = [
        "keep spawned children short-lived (this server reaps them on timeout and on exit)",
        "avoid worker/thread fan-out in long-running servers",
        "root/adb only: settings put global settings_enable_monitor_phantom_procs false",
    ]
    if env not in ("termux", "android", "proot"):
        return {"platform": env, "risk": "n/a", "active_children": kids,
                "soft_limit": 32,
                "note": "not an Android runtime; Phantom Process Killer does not apply",
                "mitigations": mitigations}
    if kids > 16:
        risk = "high"
    elif kids > 8:
        risk = "elevated"
    else:
        risk = "low"
    return {
        "platform": env,
        "active_children": kids,
        "soft_limit": 32,
        "risk": risk,
        "note": "Android 12+ terminates app process groups exceeding ~32 children "
                "or ~214MB RSS; Termux/PRoot MCP servers are common victims.",
        "mitigations": [
            "keep spawned children short-lived (this server reaps them on timeout and on exit)",
            "avoid worker/thread fan-out in long-running servers",
            "root/adb only: settings put global settings_enable_monitor_phantom_procs false",
        ],
    }


# ------------------------------------------------------------ [lifecycle] tools

def tool_device_status(_args):
    out = {"battery": None, "storage": None, "arch": None, "memory": None}

    # battery: termux-api -> sysfs capacity -> sysfs uevent -> unavailable
    raw = run("termux-battery-status")
    if raw:
        try:
            b = json.loads(raw)
            out["battery"] = {"percent": b.get("percentage"), "source": "termux-api"}
        except Exception:
            pass
    if out["battery"] is None:
        cap = run("cat /sys/class/power_supply/battery/capacity")
        if cap and cap.isdigit():
            out["battery"] = {"percent": int(cap), "source": "sysfs"}
        else:
            ue = run("cat /sys/class/power_supply/battery/uevent") or ""
            for kv in ue.splitlines():
                if kv.startswith("POWER_SUPPLY_CAPACITY="):
                    out["battery"] = {"percent": int(kv.split("=", 1)[1]),
                                      "source": "sysfs-uevent"}
                    break
            else:
                out["battery"] = {"source": "unavailable"}

    df = run("df -h /data")
    if df:
        out["storage"] = {"source": "df", "raw": df}

    arch = run("uname -m")
    out["arch"] = arch if arch else "unavailable"

    mem = run("free -m | grep Mem")
    if mem:
        out["memory"] = {"source": "free", "raw": mem}
    else:
        mi = run("head -3 /proc/meminfo")
        out["memory"] = {"source": "procfs", "raw": mi} if mi else {"source": "unavailable"}

    return out


def health_report():
    now = time.time()
    rss = read_rss_kb()
    return {
        "server": {
            "name": SERVER_NAME,
            "version": SERVER_VERSION,
            "pid": os.getpid(),
            "ppid": os.getppid(),
            "env": detect_env(),
            "uptime_s": round(now - GUARD.start, 1),
            "requests": GUARD.requests,
            "tool_calls": GUARD.tool_calls,
            "idle_s": round(now - GUARD.last_activity, 1),
            "idle_timeout_s": GUARD.idle_timeout,
            "watchdog": GUARD.watchdog,
            "stdin_open": not GUARD.stdin_eof,
            "supported_versions": list(SUPPORTED_VERSIONS),
        },
        "children": {
            "tracked": len(GUARD.live_children()),
            "system_visible": len(child_pids()),
            "reaping": "process-group SIGTERM -> SIGKILL on timeout and on exit",
        },
        "memory": {
            "rss_kb": rss,
            "rss_mb": round(rss / 1024.0, 1) if rss else None,
        },
        "phantom_process": phantom_info(),
    }


def tool_server_health(_args):
    return health_report()


# ------------------------------------------------------------- [paths] tools

_META_CHARS = ("$", "`", "*", "?", "(", ")", ";", "&", "|", "<", ">", "!", "'", '"', "\\")
_SCRIPT_EXT = (".sh", ".bash", ".py", ".pl", ".rb", ".js")


def tool_resolve_path(args):
    raw = (args or {}).get("path") or ""
    if not raw:
        return {"error": "missing required argument: path"}

    expanded = os.path.expanduser(os.path.expandvars(raw))
    if not os.path.isabs(expanded):
        expanded = os.path.abspath(expanded)
    resolved = os.path.realpath(expanded)

    mounts = parse_mounts()
    m = find_mount(resolved, mounts) or find_mount(expanded, mounts)
    ms = mount_summary(m)

    exists = os.path.exists(expanded)
    is_file = os.path.isfile(expanded)
    x_bit = os.access(expanded, os.X_OK)

    warnings = []
    if " " in expanded:
        warnings.append("path contains spaces — quote it when handing it to a shell")
    if any(ord(c) > 127 for c in expanded):
        warnings.append("path contains non-ASCII characters — ensure the client writes UTF-8")
    hits = [c for c in _META_CHARS if c in expanded]
    if hits:
        warnings.append("path contains shell metacharacters %s — quote or avoid string interpolation"
                        % "".join(sorted(set(hits))))
    if not exists:
        warnings.append("path does not exist in this runtime — check `alternatives` for a mapped location")
    if ms and ms["noexec"] and is_file and (x_bit or expanded.lower().endswith(_SCRIPT_EXT)):
        warnings.append("backing mount is noexec — cannot exec directly; run via `sh %s` / `python3 %s`"
                        % (expanded, expanded))
    if ms and ms["case_insensitive"]:
        warnings.append("filesystem is case-insensitive (%s) — case typos silently resolve" % ms["fstype"])
    if ms and ms["ro"]:
        warnings.append("backing mount is read-only")

    alts = []
    for a in android_alternates(expanded):
        alts.append({"path": a, "exists": os.path.exists(a)})

    return {
        "input": raw,
        "expanded": expanded,
        "resolved": resolved,
        "env": detect_env(),
        "exists": exists,
        "is_dir": os.path.isdir(expanded),
        "is_file": is_file,
        "is_symlink": os.path.islink(expanded),
        "readable": os.access(expanded, os.R_OK),
        "writable": os.access(expanded, os.W_OK),
        "executable": x_bit,
        "mount": ms,
        "alternatives": alts,
        "warnings": warnings,
    }


def tool_path_adapter(_args):
    env = detect_env()
    home = os.environ.get("HOME", "")
    prefix = os.environ.get("PREFIX", "")
    mounts = parse_mounts()
    roots = []
    for r in _ANDROID_ROOTS:
        if os.path.exists(r) or os.path.islink(r):
            roots.append({"path": r, "realpath": os.path.realpath(r),
                          "mount": mount_summary(find_mount(os.path.realpath(r), mounts))})

    noexec = []
    for m in mounts:
        if "noexec" in m["options"]:
            noexec.append({"mountpoint": m["mountpoint"], "fstype": m["fstype"],
                           "device": m["device"]})
    noexec = noexec[:12]

    notes = []
    if env == "termux":
        notes.append("Termux: binaries live in $PREFIX/bin; there is no usable /bin or /usr/bin — "
                     "always call tools by name or via $PREFIX/bin/<tool>.")
        notes.append("Termux: shared storage is only reachable after `termux-setup-storage` "
                     "(creates ~/storage/shared -> /storage/emulated/0).")
    elif env == "proot":
        notes.append("PRoot: /sdcard and /storage are bind mounts from the host; "
                     "host paths do not equal guest paths, resolve before handing paths across.")
    if env in ("termux", "android", "proot"):
        notes.append("Android: /sdcard is almost always mounted noexec — scripts must be invoked "
                     "through an interpreter (sh/python3), never executed in place.")

    return {
        "env": env,
        "home": home,
        "prefix": prefix,
        "tmpdir": os.environ.get("TMPDIR", ""),
        "python": sys.executable,
        "platform": sys.platform,
        "android_roots": roots,
        "noexec_mounts": noexec,
        "notes": notes,
    }


# ------------------------------------------------------------------- catalog

# Every tool in this server is a pure observer: it reads local system state,
# never writes files, never mutates device state, and never opens a network
# connection. Declaring the MCP annotation hints explicitly (instead of relying
# on the spec defaults, which assume the opposite) lets clients auto-approve
# these calls and lets directory introspection score them accurately.
_READ_ONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}

TOOLS = {
    "device_status": {
        "name": "device_status",
        "title": "Device status (read-only)",
        "description": (
            "Read-only snapshot of the host device: battery level, storage usage, "
            "CPU architecture and memory. Call it first when you need to know what "
            "hardware or runtime you are on, or to check whether battery/storage is "
            "low before starting a long task. Safe to call repeatedly and in "
            "parallel. Side effects: none — it only reads local system interfaces, "
            "never writes and never touches the network. It never raises: any field "
            "that cannot be read comes back with source \"unavailable\" instead of "
            "failing the call. Returns {battery, storage, arch, memory}."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "annotations": _READ_ONLY,
    },
    "server_health": {
        "name": "server_health",
        "title": "Server health (read-only)",
        "description": (
            "Read-only self-diagnostics for this MCP server process: pid/ppid, "
            "runtime class, uptime, request and tool-call counters, tracked live "
            "child processes, RSS, and the Android Phantom Process Killer risk "
            "assessment. Use it to verify the server is alive, to debug client-side "
            "disconnects, or to check whether orphaned children are accumulating on "
            "Android. Side effects: none — it never spawns long-lived work and never "
            "modifies state. Returns {server, children, memory, phantom_process}."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "annotations": _READ_ONLY,
    },
    "resolve_path": {
        "name": "resolve_path",
        "title": "Resolve filesystem path (read-only)",
        "description": (
            "Resolve and validate one filesystem path in the runtime this server "
            "runs in: expands ~/$HOME/$PREFIX/$TMPDIR, follows symlinks, reports the "
            "mount actually backing the path, and lists every Android-equivalent "
            "spelling (/sdcard <-> /storage/emulated/0 <-> $HOME/storage/shared). "
            "Call it before handing a path to a shell command or to another tool, "
            "especially on Termux/PRoot where one file has several spellings. Skip it "
            "for paths already known-good inside a plain Linux runtime. Read-only: it "
            "stats the path but never reads or writes file contents. Requires a "
            "non-empty `path`; an empty or missing value returns {error} rather than "
            "raising. Returns {input, expanded, resolved, env, exists, is_dir, "
            "is_file, is_symlink, readable, writable, executable, mount, "
            "alternatives, warnings}."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Path to resolve. May be absolute or relative and may contain ~, $HOME, $PREFIX or $TMPDIR. Required and non-empty; an empty string returns an error object instead of raising."}},
            "required": ["path"],
        },
        "annotations": _READ_ONLY,
    },
    "path_adapter": {
        "name": "path_adapter",
        "title": "Path environment adapter (read-only)",
        "description": (
            "Report the runtime's path environment so you can translate host paths "
            "correctly: detected env class (termux/proot/android/linux), "
            "HOME/PREFIX/TMPDIR, each Android shared-storage root with its real mount, "
            "all noexec mounts that block in-place script execution, and "
            "runtime-specific notes. Call it once when starting work on an unfamiliar "
            "device, before constructing paths for other tools. Takes no arguments. "
            "Side effects: none; read-only and idempotent. Returns {env, home, "
            "prefix, tmpdir, python, platform, android_roots, noexec_mounts, notes}."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "annotations": _READ_ONLY,
    },
}

HANDLERS = {
    "device_status": tool_device_status,
    "server_health": tool_server_health,
    "resolve_path": tool_resolve_path,
    "path_adapter": tool_path_adapter,
}


# ------------------------------------------------------------------ protocol

def negotiate_version(client_version):
    """MCP-spec version negotiation: echo the client's requested version when
    we support it; otherwise answer with the highest version we support and
    let the client decide to downgrade or abort. Legacy clients (2024-11-05)
    are explicitly supported to avoid rejection."""
    if client_version in SUPPORTED_VERSIONS:
        return client_version
    return SUPPORTED_VERSIONS[-1]


def handle(req):
    method = req.get("method", "")
    rid = req.get("id")
    GUARD.touch()

    if method == "initialize":
        client_ver = req.get("params", {}).get("protocolVersion")
        return {"jsonrpc": "2.0", "id": rid, "result": {
            "protocolVersion": negotiate_version(client_ver),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        }}
    if method == "notifications/initialized":
        return None  # silent, no response for notifications
    if method == "ping":
        return {"jsonrpc": "2.0", "id": rid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": list(TOOLS.values())}}
    if method == "tools/call":
        name = req.get("params", {}).get("name", "")
        args = req.get("params", {}).get("arguments", {}) or {}
        if name not in HANDLERS:
            return {"jsonrpc": "2.0", "id": rid, "error": {
                "code": -32602, "message": "Unknown tool: " + name}}
        GUARD.touch(tool_call=True)
        try:
            data = HANDLERS[name](args)
        except Exception as e:  # degrade, never crash the tool call
            log("tool error: " + repr(e))
            data = {"error": "internal", "detail": str(e)}
        return {"jsonrpc": "2.0", "id": rid, "result": {
            "content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}]}}

    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601,
            "message": "Method not found: " + method}}


def _on_signal(signum, _frame):
    log("received signal %d -> reaping children and exiting" % signum)
    GUARD.shutdown(0)


def main():
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        try:
            signal.signal(sig, _on_signal)
        except Exception:
            pass
    GUARD.start_watchdog()
    log("%s %s starting (env=%s, supported=%s, watchdog=%s, idle_timeout=%ss)"
        % (SERVER_NAME, SERVER_VERSION, detect_env(),
           ", ".join(SUPPORTED_VERSIONS), GUARD.watchdog, GUARD.idle_timeout))

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception as e:
            send({"jsonrpc": "2.0", "id": None, "error": {
                "code": -32700, "message": "Parse error: " + str(e)}})
            continue
        try:
            resp = handle(req)
            if resp is not None:
                send(resp)
        except Exception as e:
            log("UNCAUGHT: " + repr(e))
            send({"jsonrpc": "2.0", "id": req.get("id"), "error": {
                "code": -32603, "message": "Internal error: " + str(e)}})

    GUARD.stdin_eof = True
    log("stdin closed (client gone) -> reaping children and exiting")
    GUARD.shutdown(0)


if __name__ == "__main__":
    if "--health" in sys.argv:
        # one-shot health endpoint for wrappers/monitoring, no MCP handshake
        print(json.dumps(health_report(), ensure_ascii=False, indent=2))
        sys.exit(0)
    try:
        main()
    except Exception as e:
        log("FATAL: " + repr(e))
        GUARD.shutdown(1)
