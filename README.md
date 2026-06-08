# code-server-mcp

MCP server wrapping [code-server](https://github.com/coder/code-server) (VS Code in browser) for agent use on forge. Gives agents the ability to health-check the IDE, generate deep-link URLs for Matrix messages, and manage VS Code extensions — all without direct Docker socket access.

## Tools

| Tool | Key Parameters | Returns | Description |
|------|---------------|---------|-------------|
| `health_check` | — | `{status, http_status}` | Checks `/healthz` on code-server; status is `ok`, `degraded`, or `unreachable` |
| `open_folder_url` | `path` (absolute host path) | `{url, container_path}` | Generates a deep-link URL; path must start with `/home/ted/repos` or `/home/ted/docker` |
| `list_extensions` | — | `{extensions[], count}` | Lists installed VS Code extensions via `docker exec` |
| `install_extension` | `extension_id` (publisher.name[@version]) | `{success, output\|error}` | Installs a marketplace extension; ID validated against `^[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+(@[\d.]+)?$` |

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

## Deployment

```bash
# Install into a venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
```

The `ecosystem.config.js` sets all required env vars for forge deployment (port 8498, streamable-http transport, localhost bind).

## Observability

- Logs: `~/logs/code-server-mcp-out.log` (PM2 managed, timestamped)
- `LOG_LEVEL` env var controls verbosity (default: `INFO`)
- No OTEL instrumentation — lightweight passthrough server

## Security

- **Path allowlist**: `open_folder_url` only accepts paths under `/home/ted/repos` or `/home/ted/docker`
- **Extension ID regex**: `install_extension` validates against marketplace ID format before executing
- **No direct socket access**: Uses `docker exec` to the container, not the Docker socket
- **Localhost only**: MCP server binds to `127.0.0.1:8498` — external access via scoped-mcp only

## scoped-mcp access

| Agent | Access |
|-------|--------|
| sysadmin | Full (all 4 tools) |
| developer | Full (all 4 tools) |
| research | `install_extension` denied |
| writer | Not wired |
| security | Not wired |

## Notes

- `open_folder_url` maps `/home/ted/repos` → `/repos` to match the container's volume mount. Paths outside this prefix are passed through unchanged.
- `install_extension` has a 60s timeout. For large extensions or slow mirrors, run the install directly on forge if the MCP call times out.

## License

MIT
