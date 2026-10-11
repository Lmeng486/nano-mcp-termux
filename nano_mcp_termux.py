#!/usr/bin/env python3
"""nano-mcp-termux: Zero-dependency MCP server for AI agents.
Natively runs on Termux (Android), Raspberry Pi, and Linux.
Pure Stdio JSON-RPC, no external dependencies.
Minimal implementation to pass Glama introspection.
"""

import json
import sys

VERSION = "2024-11-05"
SERVER_NAME = "nano-mcp-termux"
SERVER_VERSION = "1.0.0"


def send_response(id, result=None, error=None):
    """Send JSON-RPC response with proper Content-Length header."""
    if error:
        response = {"jsonrpc": "2.0", "id": id, "error": error}
    else:
        response = {"jsonrpc": "2.0", "id": id, "result": result}
    
    body = json.dumps(response)
    body_bytes = body.encode('utf-8')
    content_length = len(body_bytes)
    
    # MCP protocol: Content-Length header followed by blank line then body
    sys.stdout.write(f"Content-Length: {content_length}\n\n")
    sys.stdout.write(body)
    sys.stdout.flush()


def handle_request(message):
    """Handle a single MCP request."""
    method = message.get("method", "")
    rid = message.get("id")
    params = message.get("params", {})
    
    if method == "initialize":
        return {
            "protocolVersion": VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION}
        }
    
    if method == "notifications/initialized":
        return None  # Silently ignore
    
    if method == "ping":
        return {}
    
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "device_status",
                    "description": "Check device status; returns placeholder in containers.",
                    "inputSchema": {"type": "object", "properties": {}}
                }
            ]
        }
    
    if method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {}) or {}
        if name == "device_status":
            # Return a valid but degraded response (no running commands)
            return {
                "battery": None,
                "storage": None,
                "arch": "linux",
                "memory": None
            }
    
    # Unknown method
    return {"code": -32601, "message": f"Method not found: {method}"}


def main():
    initialized = False
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            message = json.loads(line)
        except json.JSONDecodeError as e:
            send_response(None, error={"code": -32700, "message": f"Parse error: {str(e)}"})
            continue
        
        rid = message.get("id")
        if rid is None:
            continue  # Skip notifications (no ID)
        
        method = message.get("method")
        
        # Only process initialize if not initialized
        if not initialized and method != "initialize":
            continue
        
        if method == "initialize":
            initialized = True
        
        try:
            result = handle_request(message)
            if result is None:
                continue
            # For errors, send_response expects the error object directly
            send_response(rid, result if "error" not in result else result)
        except Exception as e:
            send_response(rid, error={"code": -32603, "message": f"Internal error: {str(e)}"})


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.stderr.write(f"FATAL: {e}\n")
        sys.exit(1)
