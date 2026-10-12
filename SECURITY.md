# Security Policy

## Supported versions

Only the latest release receives security fixes.

| Version | Supported |
| ------- | --------- |
| 1.1.x   | :white_check_mark: |
| < 1.1   | :x: |

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Use GitHub's private vulnerability reporting instead:

1. Go to the **Security** tab of this repository.
2. Click **Report a vulnerability**.
3. Describe the issue, the impact, and a minimal reproduction.

You can expect an initial response within a few days. Once a fix is ready it
will be released and credited to you (unless you prefer to stay anonymous).

## Threat model notes

`nano-mcp-termux` is a **local, stdio-only** MCP server. It does not open
network ports and it does not execute shell commands supplied by remote
clients. The security-relevant surfaces are:

- the process-group teardown path (must never leak processes), and
- path resolution on Android/Termux (must not escape the intended root).

Reports that touch either of those are especially welcome.
