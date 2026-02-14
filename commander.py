import os
import shlex
import subprocess


class OpenStackCommander:
    _DESTRUCTIVE_VERBS = {"delete", "purge"}

    @staticmethod
    def execute(
        command: str,
        timeout: int = 60,
        cloud: str | None = None,
        region: str | None = None,
    ) -> str:
        try:
            args = shlex.split(command)
            if not args or args[0] != "openstack":
                raise ValueError("Command must start with 'openstack'")

            allow_destructive = os.environ.get("MCP_ALLOW_DESTRUCTIVE") == "1"
            if not allow_destructive:
                normalized_tokens = {token.lower() for token in args}
                if normalized_tokens.intersection(OpenStackCommander._DESTRUCTIVE_VERBS):
                    raise ValueError(
                        "Destructive command blocked (delete/purge). "
                        "Set MCP_ALLOW_DESTRUCTIVE=1 to override."
                    )

            exec_args = ["openstack"]
            if cloud:
                exec_args.extend(["--os-cloud", cloud])
            if region:
                exec_args.extend(["--os-region-name", region])
            exec_args.extend(args[1:])

            result = subprocess.run(
                exec_args,
                shell=False,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            if result.returncode == 0:
                return stdout
            if stdout and stderr:
                return f"{stderr}\n{stdout}"
            return stderr or stdout or f"Command failed with code {result.returncode}"
        except Exception as e:
            return str(e)
