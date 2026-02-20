---
name: openstack-vm-recreate-preserve-data-ip
description: Safely recreate OpenStack VM(s) in a target AZ while preserving attached volumes, fixed IPs, floating IPs, security groups, properties, tags, and device mappings. Use for OpenStack MCP recovery/migration workflows with strict preflight/postflight checks, delete_on_termination=false enforcement, short API calls, and fallback when stop hangs or ports are deleted.
---

# OpenStack VM Recreate Preserve Data and IP

## Runtime Defaults

- `region`: `reg1`
- `project_id`: `0adf69335c0e4f51bed687e1be06f302`
- `target_az`: `az-1`
- `key_name`: `admin`
- `api_timeout_sec`: `30`
- `stop_poll_attempts`: `2`
- `include_group_hint`: `false`

## Resolve Inputs

- Read explicit values from the user request first.
- Override defaults with user-provided values.
- If a required value is missing before destructive actions, ask once and wait.

## Safety Rules

1. Run fresh preflight before any mutation.
2. Set preserve-on-termination for every attached volume.
3. Verify all attached volumes show `Delete On Termination? = false` before delete.
4. Create snapshots for all attached volumes and wait for `available`.
5. Delete old server only after snapshots are `available`.
6. Preserve NIC order, fixed IPs, security groups, and device mappings.
7. Reuse old port when available; recreate identical port if deleted.
8. Reattach FIP to the correct primary port if FIP existed.
9. Keep API calls short; poll via repeated `show` calls.

## Workflow

### 1) Fresh Preflight

Run:

```bash
server show --os-project-id <PROJECT_ID> <VM_ID> -f json
server volume list --os-project-id <PROJECT_ID> <VM_ID> -f json
port list --os-project-id <PROJECT_ID> --server <VM_ID> -f json
```

For each volume and port:

```bash
volume show --os-project-id <PROJECT_ID> <VOL_ID> -f json
volume snapshot list --os-project-id <PROJECT_ID> --volume <VOL_ID> -f json
port show --os-project-id <PROJECT_ID> <PORT_ID> -f json
floating ip list --os-project-id <PROJECT_ID> --port <PORT_ID> -f json
```

Capture:
- server name, flavor, key_name, properties, tags, security groups
- root and data volumes with devices (`/dev/sda`, `/dev/sdb`, ...)
- NICs in order with network/subnet/fixed IP/security group IDs
- floating IP IDs mapped to original ports
- server group ID/policy when present

### 2) Enforce Volume Preservation

For every attached volume:

```bash
server volume set --os-project-id <PROJECT_ID> --preserve-on-termination <VM_ID> <VOL_ID>
```

Recheck:

```bash
server volume list --os-project-id <PROJECT_ID> <VM_ID> -f json
```

Stop if any attached volume still has `Delete On Termination? = true`.

### 3) Stop (Best Effort)

```bash
server stop --os-project-id <PROJECT_ID> <VM_ID>
server show --os-project-id <PROJECT_ID> <VM_ID> -c status -c OS-EXT-STS:task_state -c OS-EXT-STS:power_state -f json
```

If not quickly `SHUTOFF`, continue with forced snapshot flow.

### 4) Snapshot All Attached Volumes

For each attached volume:

```bash
volume snapshot create --os-project-id <PROJECT_ID> --force --volume <VOL_ID> <SNAP_NAME> -f json
volume snapshot show --os-project-id <PROJECT_ID> <SNAP_ID> -f json
```

Require `status=available` for every snapshot.

### 5) Delete Old Server

```bash
server delete --os-project-id <PROJECT_ID> --force <VM_ID>
```

Post-delete checks:

```bash
server show --os-project-id <PROJECT_ID> <VM_ID> -f json
volume show --os-project-id <PROJECT_ID> <VOL_ID> -f json
port show --os-project-id <PROJECT_ID> <PORT_ID> -f json
floating ip show --os-project-id <PROJECT_ID> <FIP_ID> -f json
```

Expect:
- old server not found
- volumes `available`
- port may be present or missing
- FIP may be attached or detached

### 6) Rebuild Networking

If old port exists and detached, reuse it.

If old port is missing, recreate:

```bash
port create --os-project-id <PROJECT_ID> --network <NET_ID> --fixed-ip subnet=<SUBNET_ID>,ip-address=<FIXED_IP> --security-group <SG_ID> <PORT_NAME> -f json
```

For multi-NIC servers, recreate all NICs in original order.

### 7) Create New Server in Target AZ

Preferred (single NIC):

```bash
server create --os-project-id <PROJECT_ID> \
  --flavor <FLAVOR> \
  --key-name <KEY_NAME> \
  --availability-zone <TARGET_AZ> \
  --nic port-id=<PORT_ID> \
  --property <K1>=<V1> --tag <TAG1> \
  --volume <ROOT_VOL_ID> <SERVER_NAME> -f json
```

Multi-NIC: pass `--nic port-id=...` for each NIC in original order.

Group-hint behavior:
- If explicitly requested, try `--hint group=<GROUP_ID>` once.
- If create fails with scheduler/anti-affinity capacity error, retry without group hint and record deviation.

### 8) Attach Data Volumes

Attach non-root volumes with original devices:

```bash
server add volume --os-project-id <PROJECT_ID> --device <DEVICE> <NEW_VM_ID> <DATA_VOL_ID>
```

### 9) Rebind Floating IPs

For each previous FIP:

```bash
floating ip set --os-project-id <PROJECT_ID> --port <PRIMARY_PORT_ID> <FIP_ID>
```

### 10) Final Validation

Run:

```bash
server show --os-project-id <PROJECT_ID> <NEW_VM_ID> -f json
server volume list --os-project-id <PROJECT_ID> <NEW_VM_ID> -f json
port show --os-project-id <PROJECT_ID> <PORT_ID> -f json
floating ip show --os-project-id <PROJECT_ID> <FIP_ID> -f json
server show --os-project-id <PROJECT_ID> <OLD_VM_ID> -f json
```

Success criteria:
- new server `ACTIVE`
- fixed IPs preserved
- FIPs preserved (if existed)
- all attached volumes show `Delete On Termination? = false`
- old server not found
- snapshots are `available`

## Stop and Escalate Conditions

Stop and ask user when:
- any critical snapshot is not `available`
- any volume cannot be enforced to preserve-on-termination
- root volume not `available` after old server delete
- fixed IP cannot be recreated on new port
- new server remains `ERROR`

## Output Contract

Report these fields after each VM:
- old VM ID and new VM ID
- old port IDs and recreated port IDs
- fixed IP/FIP before and after
- root/data volume IDs and device mapping
- snapshot IDs and statuses
- explicit deviations from requested policy
