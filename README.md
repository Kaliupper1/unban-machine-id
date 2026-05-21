# Machine ID Reset Tools

Scripts to reset device identifiers for **Cursor** and **Windsurf**, and to inspect or reset system machine IDs. Available for **Windows** (PowerShell) and **Linux** (Bash).

## What These Tools Do

Applications often create unique IDs to identify your computer. These scripts generate new IDs, update the relevant config files, and create backups automatically.

## Platform Overview

| Task | Windows | Linux |
|------|---------|-------|
| Reset Cursor | `reset_cursor_windows-v0.1.ps1` | `reset_cursor_linux-v0.1.sh` |
| Reset Windsurf | `reset_windsurf_windows-v0.1.ps1` | `reset_windsurf_linux-v0.1.sh` |
| Device fingerprint | `change_device_id.ps1` | `change_device_id_linux.sh Fingerprint` |
| System machine ID | Windows Registry `MachineGuid` | `/etc/machine-id` |
| Interactive menu | `how-to-run.bat` | `how-to-run.sh` |

---

## Linux

### Requirements

- **bash** 4+
- **python3** (recommended — used for JSON and SQLite updates)
- **uuidgen** or readable `/proc/sys/kernel/random/uuid`
- **openssl** or **xxd** (for random hex IDs)
- **sudo** (optional) — only needed to reset `/etc/machine-id`

### Quick start

```bash
cd /path/to/this/repo
chmod +x *.sh
./how-to-run.sh
```

Or run scripts directly:

```bash
# Cursor (close Cursor first)
./reset_cursor_linux-v0.1.sh
sudo ./reset_cursor_linux-v0.1.sh   # also resets /etc/machine-id

# Windsurf (close Windsurf first)
./reset_windsurf_linux-v0.1.sh
sudo ./reset_windsurf_linux-v0.1.sh

# Fingerprint only (no root)
./change_device_id_linux.sh Fingerprint

# Reset Linux system machine-id (root)
sudo ./change_device_id_linux.sh ResetMachineId
```

### Linux paths

| App | Config location |
|-----|-----------------|
| Cursor | `~/.config/Cursor/` |
| Windsurf | `~/.config/Windsurf/`, `~/.windsurf/`, `~/.codeium/` |
| Fingerprint state | `~/.local/state/LicenseIdentity/fingerprint_state.json` |

`XDG_CONFIG_HOME` and `XDG_STATE_HOME` are respected when set.

### Linux scripts

- `reset_cursor_linux-v0.1.sh` — Resets Cursor IDs (`machineId`, `storage.json`, `state.vscdb`)
- `reset_windsurf_linux-v0.1.sh` — Resets Windsurf and Codeium IDs
- `change_device_id_linux.sh` — `Fingerprint` or `ResetMachineId`
- `how-to-run.sh` — Interactive menu

> **Note:** `change_device_id.ps1` modes `LegacyReset` and `RepairProfiles` are **Windows-only** (registry and profile list). On Linux use `ResetMachineId` for system ID changes.

---

## Windows

### 1. Reset Cursor ID (`reset_cursor_windows-v0.1.ps1`)

- Creates fresh identification numbers
- Updates Cursor config files and SQLite DB
- Backs up originals
- Updates Windows Registry `MachineGuid` (requires Administrator)

**Before running:** Close Cursor. Run PowerShell as Administrator.

### 2. Reset Windsurf ID (`reset_windsurf_windows-v0.1.ps1`)

- Resets Windsurf and Codeium configuration
- Timestamped backups under `%APPDATA%\Windsurf\ID_Backups`
- Updates Windows Registry `MachineGuid` (requires Administrator)

**Before running:** Close Windsurf. Run PowerShell as Administrator.

### 3. Change Windows Device ID (`change_device_id.ps1`)

| Mode | Description |
|------|-------------|
| `Fingerprint` (default) | JSON fingerprint from system signals; does not modify IDs |
| `LegacyReset` | Changes Windows device IDs and computer name (Admin) |
| `RepairProfiles` | Repairs ProfileList `.bak` keys (Admin) |

```powershell
.\change_device_id.ps1
.\change_device_id.ps1 -Mode LegacyReset
.\change_device_id.ps1 -Mode RepairProfiles
```

### Windows usage

1. Open **PowerShell as Administrator**
2. `cd` to this folder
3. Run the script you need, or use `how-to-run.bat`

```powershell
.\reset_cursor_windows-v0.1.ps1
.\reset_windsurf_windows-v0.1.ps1
.\change_device_id.ps1
```

---

## Important Notes

- **Backups** are created automatically (`.backup` files or timestamped folders)
- **Close the editor** before running reset scripts
- **System ID changes** may require a reboot (Linux) or restart (Windows)
- **Use at your own risk** — these scripts modify application and system identifiers

## Files Included

**Windows**

- `reset_cursor_windows-v0.1.ps1`
- `reset_windsurf_windows-v0.1.ps1`
- `change_device_id.ps1`
- `how-to-run.bat`

**Linux**

- `reset_cursor_linux-v0.1.sh`
- `reset_windsurf_linux-v0.1.sh`
- `change_device_id_linux.sh`
- `how-to-run.sh`
