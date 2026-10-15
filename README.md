# nano-mcp-termux

> Zero-dependency, single-file MCP server for AI agents, natively running on Termux (Android), Raspberry Pi, and Linux.

![GitHub Repository](https://img.shields.io/badge/Repo-green)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![MCP Version](https://img.shields.io/badge/MCP-2025--11--25-blue)
![Docker Ready](https://img.shields.io/badge/Docker-Ready-green)
![Version](https://img.shields.io/badge/version-1.1.0-orange)
![Tests](https://img.shields.io/badge/tests-32%20%2B%20orphan--A%2FB-brightgreen)
[![CI](https://github.com/Lmeng486/nano-mcp-termux/actions/workflows/ci.yml/badge.svg)](https://github.com/Lmeng486/nano-mcp-termux/actions/workflows/ci.yml)
![Zero Dependencies](https://img.shields.io/badge/dependencies-0-success)

## 🚀 Quick Start

### Local (Termux / Linux)
```bash
cd /path/to/nano-mcp-termux
python3 nano_mcp_termux.py
```

### Docker
```bash
docker build -t nano-mcp-termux .
docker run -i --rm nano-mcp-termux
```

### Health check (one-shot, no MCP handshake)
```bash
python3 nano_mcp_termux.py --health
```

## 🛠️ Features

- ✅ **Zero-dependency**: No external packages required
- ✅ **Single-file**: All logic in one Python script
- ✅ **Cross-platform**: Works in Termux (Android), on Raspberry Pi, Linux, and inside Docker
- ✅ **Container-ready**: Dockerfile at repo root for Glama introspection
- ✅ **Standard stdio framing**: Newline-delimited JSON-RPC (official MCP transport)
- ✅ **Version negotiation**: Echoes client `protocolVersion` (2024-11-05 / 2025-06-18 / 2025-11-25), falls back to highest supported
- ✅ **Graceful degradation**: `device_status` never fails; unavailable inputs are marked, not crashed
- ✅ **[lifecycle] No orphaned processes**: every command runs in its own process group; timeouts kill the *whole tree* (`SIGTERM` → `SIGKILL`), never just the shell
- ✅ **[lifecycle] Self-terminating**: parent-process watchdog + stdin-EOF detection + optional idle timeout, so a dead client never leaves a zombie server behind
- ✅ **[lifecycle] Phantom Process Killer aware**: reports Android 12+ child-count risk with concrete mitigations
- ✅ **[paths] Android/Termux path adapter**: resolves `/sdcard` ↔ `/storage/emulated/0` ↔ `$HOME/storage/shared`, detects `noexec` mounts, case-insensitive filesystems, and shell-quoting hazards

## 🧩 Tools Overview

| Tool | Description |
|------|-------------|
| `device_status` | Aggregate device info: battery / storage / arch / memory (degraded fields marked unavailable) |
| `server_health` | Runtime health: pid/ppid/env, uptime, request counters, live children, reaping policy, RSS, Phantom Process Killer risk |
| `resolve_path` | Resolve an Android/Termux path: canonical form, mount point, `noexec`/read-only flags, case sensitivity, equivalent spellings, quoting warnings |
| `path_adapter` | Environment profile: runtime class, `$HOME`/`$PREFIX`/`$TMPDIR`, Android storage roots with mount summaries, `noexec` mount list |

## 🔗 Protocol Surface

| Method | Behavior |
|--------|----------|
| `initialize` | Echoes supported client version (2024-11-05 / 2025-06-18 / 2025-11-25), else responds with highest supported per MCP spec; declares `{"tools": {}}` |
| `notifications/initialized` | Silent (no response) |
| `ping` | Returns `{}` |
| `tools/list` | Returns tool catalog |
| `tools/call` | Returns `{"content": [{"type": "text", ...}]}` |
| Unknown method / tool | `-32601` / `-32602` JSON-RPC errors |
| Malformed JSON | `-32700` parse error |

## 🔄 Why 1.1.0: the orphan-process bug

Version 1.0.0 ran commands with `subprocess.run(..., timeout=...)`. On timeout,
Python terminates only the **direct** child — the `sh -c` wrapper. Anything the
shell had already spawned is reparented to init and **survives forever**. On
Android that is the exact leak class that trips the **Phantom Process Killer**
and can get the whole app group killed.

1.1.0 fixes this at the root: commands are spawned with `start_new_session=True`
and torn down with `os.killpg(pgid, SIGTERM)` → `SIGKILL`, so the entire process
tree dies together.

The repository ships a reproducible A/B regression test for it:

```bash
python3 test_lifecycle_orphan.py
# current  nano_mcp_termux.py           leaked_grandchildren=0
# legacy   nano_mcp_termux_v10_backup.py leaked_grandchildren=1   <- the bug
# PASS: current server leaves 0 orphaned grandchildren after timeout
```

## ✅ Tests

```bash
python3 test_client.py            # 32 protocol / tool / lifecycle assertions
python3 test_lifecycle_orphan.py  # orphan-leak A/B regression (1.0.0 vs 1.1.0)
```

## ⚙️ Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `NANO_IDLE_TIMEOUT` | `0` (off) | Seconds of inactivity before the server exits on its own |
| `NANO_NO_WATCHDOG` | unset | Set to `1` to disable the parent-process watchdog thread |

## 🔗 Links

- **Original repository**: [Lmeng486/nano-mcp-termux](https://github.com/Lmeng486/nano-mcp-termux)
- **Verification report**: [awesome-termux-mcp](https://github.com/Lmeng486/awesome-termux-mcp)
- **Measured overhead report** (this server as subject under test, all numbers from a real device): [MCP on Mobile: Measured Overhead Report](https://github.com/Lmeng486/awesome-termux-mcp/blob/main/docs/MCP-ON-MOBILE-OVERHEAD.md)

---

*This server is designed to pass Glama introspection checks and serve as a lightweight MCP implementation for mobile and edge devices.*
