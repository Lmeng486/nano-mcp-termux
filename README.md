# nano-mcp-termux

> Zero-dependency, single-file MCP server for AI agents, natively running on Termux (Android), Raspberry Pi, and Linux.

![GitHub Repository](https://img.shields.io/badge/Repo-green)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![MCP Version](https://img.shields.io/badge/MCP-2024--11--05-blue)
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
docker run -it nano-mcp-termux
```

## 🛠️ Features

- ✅ **Zero-dependency**: No external packages required
- ✅ **Single-file**: All logic in one Python script
- ✅ **Cross-platform**: Works on Android (Termux), Raspberry Pi, Linux
- ✅ **Container-ready**: Dockerfile for Glama introspection
- ✅ **Minimal MCP protocol**: Implements `initialize`, `tools/list`, `tools/call`

## 🧩 Tools Overview

| Tool | Description |
|------|-------------|
| `device_status` | Check device environment (degraded in containers) |

## 🔗 Links

- **Original repository**: [Lmeng486/nano-mcp-termux](https://github.com/Lmeng486/nano-mcp-termux)
- **Verification report**: [awesome-termux-mcp](https://github.com/Lmeng486/awesome-termux-mcp)

---

*This server is designed to pass Glama introspection checks and serve as a lightweight MCP implementation for mobile and edge devices.*
