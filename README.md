# code-server-mcp

MCP server wrapping [code-server](https://github.com/coder/code-server) (VS Code in browser) for agent use on forge.

## Tools

| Tool | Description |
|------|-------------|
| `health_check()` | Checks `/healthz` on code-server; returns `ok`, `degraded`, or `unreachable` |
| `open_folder_url(path)` | Generates a `https://code.helmforge.me/?folder=...` deep-link URL for a host path |
| `list_extensions()` | Lists installed VS Code extensions via `docker exec` |
| `install_extension(extension_id)` | Installs an extension by ID (e.g. `ms-python.python`) via `docker exec` |

## Requirements

- Python 3.11+
- code-server running in a Docker container (container name configurable via `CODESERVER_CONTAINER`)
- PM2 user in the `docker` group (for `docker exec` access without sudo)

## Installation

```bash
pip install -r requirements.txt
# or
pip install -e .
```

## Configuration

| Env var | Required | Default | Description |
|---------|----------|---------|-------------|
| `CODESERVER_URL` | no | `http://127.0.0.1:8443` | Internal URL for health checks |
| `CODESERVER_PUBLIC_URL` | no | `https://code.helmforge.me` | Public URL used in generated deep-links |
| `CODESERVER_CONTAINER` | no | `code-server` | Docker container name for exec commands |
| `CODESERVER_BIN` | no | `/app/code-server/bin/code-server` | Path to code-server binary inside the container |
| `FASTMCP_TRANSPORT` | no | `stdio` | Set to `streamable-http` for PM2 deployment |
| `FASTMCP_PORT` | no | — | Port for streamable-http transport (forge: `8498`) |
| `FASTMCP_HOST` | no | — | Bind address (forge: `127.0.0.1`) |
| `LOG_LEVEL` | no | `INFO` | Log verbosity |

## Running

```bash
# Direct
python3 -m code_server_mcp.server

# Via PM2
pm2 start ecosystem.config.js
pm2 save
```

## Usage with Claude

Once deployed via scoped-mcp, tools are available as `mcp__scoped-mcp__<tool>`.

```
# Check health before sending a Matrix link
tool: mcp__scoped-mcp__health_check

# Generate a deep-link to a repo
tool: mcp__scoped-mcp__open_folder_url
args:
  path: /home/ted/repos/personal/signoz-mcp
# → {"url": "https://code.helmforge.me/?folder=/repos/personal/signoz-mcp", ...}

# List installed extensions
tool: mcp__scoped-mcp__list_extensions

# Install an extension
tool: mcp__scoped-mcp__install_extension
args:
  extension_id: ms-python.python
```

## Notes

- `open_folder_url` maps `/home/ted/repos` → `/repos` to match the container's volume mount. Paths outside this prefix are passed through unchanged.
- `install_extension` has a 60s timeout. For large extensions or slow mirrors, run the install directly on forge if the MCP call times out.
- The MCP server binds to `127.0.0.1` only — no direct external access. Access is via scoped-mcp.

## License

MIT
