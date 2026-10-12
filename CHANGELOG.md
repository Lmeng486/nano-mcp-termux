# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-10-12

### Added

- `server_health` tool: one-shot JSON health snapshot (pid, uptime, idle
  policy, watchdog state).
- Android/Termux path adapter (`resolve_path`, `path_adapter`) so host paths
  map correctly to on-device locations.
- `--health` CLI flag for one-shot checks without an MCP handshake.
- Orphan-leak regression test (`test_lifecycle_orphan.py`) with an A/B baseline
  against v1.0.0.
- GitHub Actions CI across Python 3.9-3.13 plus a Docker build smoke test.

### Changed

- Command execution now spawns with `start_new_session=True` and tears the
  timeout path down with `os.killpg(pgid, SIGTERM)` -> `SIGKILL`, so no
  grandchild survives a timeout.

### Fixed

- **Orphan-process leak (v1.0.0):** timed-out commands left grandchildren
  reparented to init, which tripped the Android Phantom Process Killer and
  could get the entire host app group killed.
- Parent-process watchdog + stdin-EOF path: the server now self-terminates
  when its client disappears.

## [1.0.0]

- Initial public release: single-file, zero-dependency MCP server over stdio
  with `initialize`, `ping`, `tools/list`, and `tools/call`.
