# OpenStack MCP region aliases (personal)

## Region selection
- If the user mentions "reg1", "r1", "region1", "рег1" -> use MCP server `reg1`.
- If the user mentions "reg2", "r2", "region2", "рег2" -> use MCP server `reg2`.
- If the user does not specify a region, default to `reg1`.

## OpenStack commands
- Always run OpenStack CLI through the selected MCP server tool `exec_openstack`.
- Prefer read-only commands first (list/show), and use `-f json` when convenient.

