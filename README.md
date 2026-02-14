
# simple-openstack-mcp
This is a `fastmcp`-based MCP server that allows an LLM to execute complex OpenStack commands for you in an environment where `openstack-cli` is runnable.

This FORK can work with multiple regions - check and customize AGENTS.md.

> [!NOTE]
> In this fork, only commands containing the verbs `delete` or `purge` are treated as **DESTRUCTIVE** and blocked by default.
> Other mutating OpenStack actions (for example `create`, `set`, `unset`, `start`, `stop`, `reboot`) are not blocked by this specific guard.

## How To

### OpenStack Configuration

The `openstack-cli` must be executable in the environment where this MCP server runs. Additionally, the authentication credentials for the target OpenStack cloud must be stored in `clouds.yaml`. Here is an example:

```yaml
clouds:
  ...: # openstack_cloud_name
    auth:
      auth_url: ...
      username: ...
      password: ...
      project_id: ...
      project_name: ...
      user_domain_name: ...
    region_name: ...
    interface: "public"
    identity_api_version: 3
```

### Hardened behavior (in this fork)

This build uses safer command execution defaults:

- Commands are executed with `shell=False` and tokenized by `shlex.split`.
- `exec_openstack.cmd` is trimmed and whitespace-normalized via tokenization; if it does not start with `openstack`, the prefix is added automatically.
- Destructive verbs are blocked by default: `delete`, `purge`.
- To explicitly allow destructive commands, set `MCP_ALLOW_DESTRUCTIVE=1` in the server environment.
- If `${PWD}/clouds.yaml` exists, `OS_CLIENT_CONFIG_FILE` is set via `os.environ.setdefault` (so an existing env value is preserved).

The `exec_openstack` tool also supports optional parameters:

- `cloud`: maps to `--os-cloud`
- `region`: maps to `--os-region-name`
- `timeout`: command timeout in seconds (default: `60`)

### Connecting the MCP Tool

### Codex (config.toml)

If you are using Codex, add an MCP server entry to `~/.codex/config.toml`:

```toml
[mcp_servers.openstack]
command = "zsh"
args = ["-lc", "source /PATHTOOPENRC/openrc; uv run -m server"]
cwd = "/YOUPATH/openstack-mcp-h"
startup_timeout_sec = 30
tool_timeout_sec = 120
```

To allow destructive verbs in Codex for a controlled environment:

```toml
[mcp_servers.openstack]
command = "zsh"
args = ["-lc", "source /PATHTOOPENRC/openrc; uv run -m server"]
cwd = "/YOUPATH/openstack-mcp-h"
startup_timeout_sec = 30
tool_timeout_sec = 120
env = { MCP_ALLOW_DESTRUCTIVE = "1" }
```

For multimple Regions add several sections like and check AGENTS.md:

```toml
[mcp_servers.reg1]
...

[mcp_servers.reg2]
...

[mcp_servers.regX]
...
```

### Claude Desktop / VSCode Copilot

If you are using `Claude Desktop` or `VScode Copilot`, add the following to your claude_desktop_config.json. You can add similar settings to other LLM clients you wish to use.

```json
{
    "mcpServers": {
      "openstack": {
        "command": "uv",
        "args": [
          "--directory",
          "${REPOSITORY_ABS_PATH}/simple-openstack-mcp",
          "-m",
          "server"
        ]
      }
    }
}
```

To allow destructive verbs for a controlled environment:

```json
{
  "mcpServers": {
    "openstack": {
      "command": "uv",
      "args": ["--directory", "${REPOSITORY_ABS_PATH}/simple-openstack-mcp", "-m", "server"],
      "env": {
        "MCP_ALLOW_DESTRUCTIVE": "1"
      }
    }
  }
}
```

If you don't have the repository cloned locally, you can also run it with uvx:

```json
{
    "mcpServers": {
      "openstack": {
        "command": "uvx",
        "args": [
          "--from",
          "git+https://github.com/choieastsea/simple-openstack-mcp",
          "simple-openstack-mcp"
        ]
      }
    }
}
```

## Running the fastmcp Server locally

The following commands should run successfully from the repository directory:

```bash
❯ uv sync
❯ uv run -m server
```
