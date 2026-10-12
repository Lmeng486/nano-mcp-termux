# Contributing to nano-mcp-termux

Thanks for your interest. This project has one hard rule:

> **Zero dependencies. One file.** The server must keep running on a bare
> Termux install, a Raspberry Pi, and inside a `python:*-slim` container
> without `pip install` ever being required.

## Ground rules

1. **No third-party packages.** Standard library only. If a change needs a
   dependency, it belongs in a separate project.
2. **Single file.** `nano_mcp_termux.py` is the whole server. Keep it that way.
3. **Protocol surface is a contract.** The supported JSON-RPC methods are
   listed in the README. Additions are welcome; silent removals are not.
4. **Lifecycle safety is non-negotiable.** Anything that spawns a process must
   tear down the *whole* process group on timeout, and the server must
   self-terminate when its client disappears. This is what keeps the Android
   Phantom Process Killer from killing the host app.

## Development

```bash
git clone https://github.com/Lmeng486/nano-mcp-termux.git
cd nano-mcp-termux

python3 test_client.py            # 32 protocol / tool / lifecycle assertions
python3 test_lifecycle_orphan.py  # orphan-leak A/B regression (1.0.0 vs 1.1.0)
python3 nano_mcp_termux.py --health
```

CI runs the same commands on Python 3.9-3.13 plus a Docker build, so please
make sure they pass locally before opening a PR.

## Pull requests

- Keep the diff focused; one logical change per PR.
- Fill in the PR template checklist.
- Update the README if you touch the tool surface or the supported methods.
- Add a `CHANGELOG.md` entry under `## [Unreleased]`.

## Reporting bugs

Use the issue template. For anything security-related, follow `SECURITY.md`
instead of opening a public issue.
