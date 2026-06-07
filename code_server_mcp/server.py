"""code-server MCP server — wraps code-server for agent use."""

import os
import re
import subprocess
from urllib.parse import quote
from fastmcp import FastMCP
import httpx

mcp = FastMCP("code-server-mcp")

CODESERVER_URL = os.environ.get("CODESERVER_URL", "http://127.0.0.1:8443")
CODESERVER_PUBLIC_URL = os.environ.get("CODESERVER_PUBLIC_URL", "")
CONTAINER_NAME = os.environ.get("CODESERVER_CONTAINER", "code-server")
CODESERVER_BIN = os.environ.get("CODESERVER_BIN", "/app/code-server/bin/code-server")

EXTENSION_ID_RE = re.compile(r"^[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+(@[\d.]+)?$")


@mcp.tool()
async def health_check() -> dict:
    """Check if code-server is running and healthy."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{CODESERVER_URL}/healthz")
            return {"status": "ok" if resp.status_code == 200 else "degraded", "http_status": resp.status_code}
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}


@mcp.tool()
def open_folder_url(path: str) -> dict:
    """
    Generate a code-server deep-link URL to open a folder.

    Args:
        path: Absolute path on the forge host (e.g. /home/ted/repos/personal/signoz-mcp)

    Returns:
        URL string suitable for sharing in Matrix messages.
    """
    # Map host paths to container paths
    if path.startswith("/home/ted/repos"):
        container_path = path.replace("/home/ted/repos", "/repos", 1)
    else:
        container_path = path
    url = f"{CODESERVER_PUBLIC_URL}/?folder={quote(container_path, safe='/')}"
    return {"url": url, "container_path": container_path}


@mcp.tool()
def list_extensions() -> dict:
    """List installed VS Code extensions in code-server."""
    try:
        result = subprocess.run(
            ["docker", "exec", CONTAINER_NAME, CODESERVER_BIN, "--list-extensions"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return {"error": result.stderr.strip(), "extensions": []}
        extensions = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return {"extensions": extensions, "count": len(extensions)}
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "extensions": []}
    except Exception as e:
        return {"error": str(e), "extensions": []}


@mcp.tool()
def install_extension(extension_id: str) -> dict:
    """
    Install a VS Code extension in code-server.

    Args:
        extension_id: Extension ID in publisher.name format (e.g. ms-python.python)
    """
    if not EXTENSION_ID_RE.match(extension_id):
        return {"success": False, "error": "invalid extension_id format — expected publisher.name[@version]"}
    try:
        result = subprocess.run(
            ["docker", "exec", CONTAINER_NAME, CODESERVER_BIN, "--install-extension", extension_id],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return {"success": False, "error": result.stderr.strip()}
        return {"success": True, "output": result.stdout.strip()}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "timeout — installation may still be running"}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    mcp.run()
