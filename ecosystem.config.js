module.exports = {
  apps: [{
    name: "code-server-mcp",
    script: "/home/ted/repos/personal/code-server-mcp/venv/bin/python3",
    args: "-m code_server_mcp.server",
    cwd: "/home/ted/repos/personal/code-server-mcp",
    interpreter: "none",

    restart_delay: 5000,
    max_restarts: 10,
    min_uptime: "10s",

    out_file: "/home/ted/logs/code-server-mcp-out.log",
    error_file: "/home/ted/logs/code-server-mcp-error.log",
    log_file: "/home/ted/logs/code-server-mcp.log",
    merge_logs: true,
    time: true,

    env: {
      FASTMCP_TRANSPORT: "streamable-http",
      FASTMCP_PORT: "8498",
      FASTMCP_HOST: "127.0.0.1",
      CODESERVER_URL: "http://127.0.0.1:8443",
      CODESERVER_PUBLIC_URL: "https://code.helmforge.me",
      CODESERVER_CONTAINER: "code-server",
      CODESERVER_BIN: "/app/code-server/bin/code-server",
    },
  }],
};
