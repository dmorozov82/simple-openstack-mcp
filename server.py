import os
from fastmcp import FastMCP
from commander import OpenStackCommander

mcp = FastMCP(name="simple-openstack-mcp", dependencies=[])


@mcp.tool()
def exec_openstack(
    cmd: str,
    cloud: str | None = None,
    region: str | None = None,
    timeout: int = 60,
) -> str:
    """
    Execute an OpenStack CLI command.
    """
    if not cmd.strip().startswith("openstack"):
        raise ValueError("Command must start with 'openstack'")
    if timeout <= 0:
        raise ValueError("timeout must be greater than 0")
    return OpenStackCommander.execute(
        cmd,
        timeout=timeout,
        cloud=cloud,
        region=region,
    )


def main():
    clouds_yaml_path = os.path.join(os.getcwd(), "clouds.yaml")
    if os.path.exists(clouds_yaml_path):
        os.environ.setdefault("OS_CLIENT_CONFIG_FILE", clouds_yaml_path)
    print("Using clouds.yaml from:", os.environ.get("OS_CLIENT_CONFIG_FILE", "not set"))
    mcp.run()


if __name__ == "__main__":
    main()
