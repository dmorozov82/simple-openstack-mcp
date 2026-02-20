# openstack-vm-recreate-preserve-data-ip

Skill for safe OpenStack VM recreation with strict data/IP preservation and short API calls.

## Where files are

- `SKILL.md`: workflow and command templates
- `README.md`: usage and defaults override guide

## Attention:

You MUST set explicitly to allow destructive commands, set `MCP_ALLOW_DESTRUCTIVE=1` in the server environment, at least for `continue recreate` after approval.

## How to call in chat

Use direct trigger text. Examples:

- `Use skill openstack-vm-recreate-preserve-data-ip for VM <vm_id>`
- `Выполни по skill openstack-vm-recreate-preserve-data-ip: preflight -> recreate -> verify`
- `Use openstack-vm-recreate-preserve-data-ip for these VM IDs in order ...`

## Current defaults

- `region`: `reg1` # How alias is defined in your AGENTS.md or set explicitly 
- `project_id`: `0563ffce846247f09332c24c656f1b5e`
- `target_az`: `az-1`
- `key_name`: `admin`
- `api_timeout_sec`: `30`
- `stop_poll_attempts`: `2`
- `include_group_hint`: `false`

## How to reassign defaults per run

Pass overrides directly in your request. Examples:

- `Use skill ... with region=reg2`
- `Use skill ... with project_id=<new_project_id>, target_az=az-2`
- `Use skill ... and key_name=mykey`
- `Use skill ... include_group_hint=true`

The skill always prefers explicit values from the current request over defaults.

## How to change defaults permanently

Edit section `Runtime Defaults` in `SKILL.md` and commit the file.

## Recommended call pattern

- `preflight only` for first approval
- `continue recreate` after approval
- `final verify` and report old->new IDs, ports, IP/FIP, volumes, snapshots

## Notes

- Skill is designed for OpenStack MCP execution with short API calls and repeated short polling.
- If anti-affinity group scheduling fails (`No valid host`), recreate without group hint and record the deviation.
