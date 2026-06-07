# Changelog

## [0.1.0] — 2026-06-07

### Added
- `health_check()` — verify code-server is running via `/healthz`
- `open_folder_url(path)` — generate deep-link URL for Matrix messages; path restricted to `/home/ted/repos` and `/home/ted/docker`; container path URL-encoded
- `list_extensions()` — list installed VS Code extensions via `docker exec`
- `install_extension(extension_id)` — install extensions via `docker exec`; extension ID validated against marketplace format (`publisher.name[@version]`)
- PM2 deployment on port 8498 (streamable-http, 127.0.0.1-only)
- scoped-mcp wiring for research agent (install_extension denied) and sysadmin agent

### Security
- Extension ID validated against `^[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+(@[\d.]+)?$` before docker exec (F-01)
- Container path URL-encoded in `open_folder_url` (F-02)
- Path prefix allowlist enforced in `open_folder_url` (F-03)
- GitHub Actions pinned to SHA digests (F-05)
- Exception handlers return generic error strings; no internal topology exposed (F-06)
