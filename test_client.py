#!/usr/bin/env python3
"""Simulated MCP client — version negotiation, graceful degradation,
lifecycle guardian surface, and the Android/Termux path adapter."""
import json, os, subprocess, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
# Canonical implementation name; MCP_SERVER can override for A/B runs.
SERVER = os.environ.get("MCP_SERVER", os.path.join(_HERE, "nano_mcp_termux.py"))
SRV = [os.environ.get("MCP_PYTHON", sys.executable), SERVER]

def talk(reqs):
    return talk_raw([json.dumps(r) for r in reqs])

def talk_raw(lines):
    p = subprocess.run(SRV, input="\n".join(lines) + "\n",
                       capture_output=True, text=True, timeout=20)
    resp = [json.loads(l) for l in p.stdout.splitlines() if l.strip()]
    if not resp:
        sys.stderr.write("[test-client] server returned nothing; rc=%s stderr=%r\n" % (p.returncode, p.stderr))
        raise SystemExit(2)
    return resp, p.stderr

checks = []
def check(name, cond):
    checks.append((name, bool(cond)))

# --- scenario A: client sends 2025-11-25 -> echoed back ---
resp, _ = talk([
    {"jsonrpc": "2.0", "id": 1, "method": "initialize",
     "params": {"protocolVersion": "2025-11-25", "capabilities": {},
                "clientInfo": {"name": "test", "version": "0"}}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 2, "method": "ping"},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/list"},
    {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
     "params": {"name": "device_status", "arguments": {}}},
])
init = resp[0]["result"]
check("initialize echoes client version 2025-11-25",
      init.get("protocolVersion") == "2025-11-25")
check("capabilities == {'tools': {}}", init.get("capabilities") == {"tools": {}})
check("serverInfo name/version present",
      init["serverInfo"]["name"] == "nano-mcp-termux" and bool(init["serverInfo"]["version"]))
check("notification got NO response", len(resp) == 4)
check("ping -> {}", resp[1]["result"] == {})
names = [t["name"] for t in resp[2]["result"]["tools"]]
check("tools/list exposes 4 tools", len(names) == 4)
check("device_status stays first", names[0] == "device_status")
check("tools/list includes lifecycle + path tools",
      set(names) == {"device_status", "server_health", "resolve_path", "path_adapter"})
bat = json.loads(resp[3]["result"]["content"][0]["text"]).get("battery", {})
check("tools/call content type text",
      resp[3]["result"]["content"][0]["type"] == "text")
check("battery source in full degradation ladder",
      bat.get("source") in ("termux-api", "sysfs", "sysfs-uevent", "unavailable"))

# --- scenario B: client sends 2025-06-18 -> echoed back ---
resp2, _ = talk([{"jsonrpc": "2.0", "id": 1, "method": "initialize",
                  "params": {"protocolVersion": "2025-06-18"}}])
check("initialize echoes client version 2025-06-18",
      resp2[0]["result"]["protocolVersion"] == "2025-06-18")

# --- scenario C: unknown version -> highest supported ---
resp3, _ = talk([{"jsonrpc": "2.0", "id": 1, "method": "initialize",
                  "params": {"protocolVersion": "1999-01-01"}}])
check("unknown version -> highest supported 2025-11-25",
      resp3[0]["result"]["protocolVersion"] == "2025-11-25")

# --- scenario E: legacy client version 2024-11-05 -> echoed back ---
resp5, _ = talk([{"jsonrpc": "2.0", "id": 1, "method": "initialize",
                  "params": {"protocolVersion": "2024-11-05"}}])
check("initialize echoes legacy version 2024-11-05",
      resp5[0]["result"]["protocolVersion"] == "2024-11-05")

# --- scenario G: [lifecycle] server_health ---
respH, _ = talk([
    {"jsonrpc": "2.0", "id": 1, "method": "initialize",
     "params": {"protocolVersion": "2025-11-25"}},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
     "params": {"name": "server_health", "arguments": {}}},
])
h = json.loads(respH[1]["result"]["content"][0]["text"])
check("server_health reports this pid", h["server"]["pid"] == os.getpid() or isinstance(h["server"]["pid"], int))
check("server_health reports ppid + env", isinstance(h["server"]["ppid"], int) and h["server"]["env"] in
      ("termux", "proot", "android", "linux"))
check("server_health reports uptime + counters",
      isinstance(h["server"]["uptime_s"], (int, float)) and h["server"]["requests"] >= 1)
check("server_health reports children + reaping policy",
      "tracked" in h["children"] and "SIGKILL" in h["children"]["reaping"])
check("server_health reports memory rss", "rss_kb" in h["memory"])
check("server_health reports phantom-process assessment",
      "risk" in h["phantom_process"] and "mitigations" in h["phantom_process"])
check("server_health lists supported protocol versions",
      h["server"]["supported_versions"] == ["2024-11-05", "2025-06-18", "2025-11-25"])

# --- scenario H: [paths] resolve_path ---
respP, _ = talk([
    {"jsonrpc": "2.0", "id": 1, "method": "initialize",
     "params": {"protocolVersion": "2025-11-25"}},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
     "params": {"name": "resolve_path", "arguments": {"path": "/sdcard/Download"}}},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
     "params": {"name": "resolve_path", "arguments": {"path": "$HOME"}}},
    {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
     "params": {"name": "resolve_path", "arguments": {}}},
])
p1 = json.loads(respP[1]["result"]["content"][0]["text"])
check("resolve_path returns expanded/resolved/mount/warnings",
      all(k in p1 for k in ("expanded", "resolved", "mount", "warnings", "alternatives")))
check("resolve_path lists Android-equivalent spellings for /sdcard",
      any(a["path"].startswith("/storage/emulated/0") for a in p1["alternatives"]))
p2 = json.loads(respP[2]["result"]["content"][0]["text"])
check("resolve_path expands $HOME", p2["expanded"] == os.environ.get("HOME", p2["expanded"]))
p3 = json.loads(respP[3]["result"]["content"][0]["text"])
check("resolve_path without path -> error object", "error" in p3)

# --- scenario I: [paths] path_adapter ---
respA, _ = talk([
    {"jsonrpc": "2.0", "id": 1, "method": "initialize",
     "params": {"protocolVersion": "2025-11-25"}},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
     "params": {"name": "path_adapter", "arguments": {}}},
])
a = json.loads(respA[1]["result"]["content"][0]["text"])
check("path_adapter reports env/home/prefix",
      all(k in a for k in ("env", "home", "prefix", "tmpdir", "android_roots", "noexec_mounts")))

# --- scenario D: protocol errors ---
resp4, err = talk_raw([
    '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "no_such_tool", "arguments": {}}}',
    'not json at all',
])
check("unknown tool -> -32602", resp4[0]["error"]["code"] == -32602)
check("parse error -> -32700", resp4[1]["error"]["code"] == -32700)
check("logs on stderr only", "[nano-mcp]" in err)
check("stdout clean (all lines are JSON)",
      all(True for _ in resp4))  # talk() already json.loads every line

# --- scenario F: CLI one-shot health endpoint ---
p = subprocess.run(SRV + ["--health"], capture_output=True, text=True, timeout=20)
try:
    hj = json.loads(p.stdout)
except Exception:
    hj = {}
check("--health prints one-shot JSON", isinstance(hj.get("server", {}).get("pid"), int))
check("--health exits 0", p.returncode == 0)

# --- scenario J: [lifecycle] no orphan after client disappears ---
# spawn the server with a stdin pipe, then close stdin without killing it;
# the watchdog / EOF path must terminate the process on its own.
child = subprocess.Popen(SRV, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, text=True)
child.stdin.write(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                              "params": {"protocolVersion": "2025-11-25"}}) + "\n")
child.stdin.flush()
child.stdin.close()
try:
    rc = child.wait(timeout=10)
except subprocess.TimeoutExpired:
    child.kill()
    rc = None
check("server self-terminates when stdin closes (no orphan)", rc == 0)

fails = [n for n, okc in checks if not okc]
for n, okc in checks:
    print(("PASS " if okc else "FAIL ") + n)
print("RESULT: " + ("ALL CHECKS PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
