# nano-mcp-termux

> Zero-dependency, single-file MCP server for AI agents, natively running on Termux (Android), Raspberry Pi, and Linux.

![GitHub Repository](https://img.shields.io/badge/Repo-green)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![MCP Version](https://img.shields.io/badge/MCP-2025--11--25-blue)
![Docker Ready](https://img.shields.io/badge/Docker-Ready-green)

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

## 🛠️ Features

- ✅ **Zero-dependency**: No external packages required
- ✅ **Single-file**: All logic in one Python script
- ✅ **Cross-platform**: Works in Termux (Android), on Raspberry Pi, Linux, and inside Docker
- ✅ **Container-ready**: Dockerfile at repo root for Glama introspection
- ✅ **Standard stdio framing**: Newline-delimited JSON-RPC (official MCP transport)
- ✅ **Version negotiation**: Echoes client `protocolVersion` (2025-06-18 / 2025-11-25), falls back to highest supported
- ✅ **Graceful degradation**: `device_status` never fails; unavailable inputs are marked, not crashed

## 🧩 Tools Overview

| Tool | Description |
|------|-------------|
| `device_status` | Aggregate device info: battery / storage / arch / memory (degraded fields marked unavailable) |

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

## 🔗 Links

- **Original repository**: [Lmeng486/nano-mcp-termux](https://github.com/Lmeng486/nano-mcp-termux)
- **Verification report**: [awesome-termux-mcp](https://github.com/Lmeng486/awesome-termux-mcp)

---

*This server is designed to pass Glama introspection checks and serve as a lightweight MCP implementation for mobile and edge devices.*