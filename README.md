# Linux GNOME Configs

A personal cheat sheet of terminal commands and configs I use on my Fedora Linux laptop (GNOME).
Everything here is meant to be copy-pasteable — adjust names, devices, and paths to match your machine.

**Tested on:** Fedora Workstation (GNOME / Wayland), `dnf5`, `systemd`, NetworkManager.

## Contents

| File | What's inside |
| --- | --- |
| [system.md](system.md) | Services, logs, time/locale, power, system upgrades |
| [packages.md](packages.md) | `dnf`, `rpm`, Flatpak, RPM Fusion, COPR, Toolbox |
| [files.md](files.md) | Finding, searching, copying, archiving, permissions |
| [networking.md](networking.md) | NetworkManager, `ip`, `ss`, DNS, SSH, firewall |
| [hardware.md](hardware.md) | Battery, brightness, Bluetooth, touchpad, Wi-Fi, sensors |
| [graphics.md](graphics.md) | Hybrid Intel/NVIDIA, `envycontrol`, PRIME/offload, driver overrides |
| [storage.md](storage.md) | Disks, mounts, `fstab`, LUKS, LVM, Btrfs, snapshots |
| [display.md](display.md) | Monitors: detect, save/restore layouts, scaling, auto 120/60 Hz |
| [desktop.md](desktop.md) | GNOME, `gsettings`, screenshots, clipboard, fonts |
| [security.md](security.md) | SELinux, GPG, SSH keys, secrets |
| [troubleshooting.md](troubleshooting.md) | Common laptop fixes and what to check first |
| [scripts/](scripts/) | Ready-to-use helpers (panel refresh-rate switching) |

## Conventions

- `$` = run as your normal user.
- `#` = run as root (usually via `sudo`).
- `<angle-brackets>` = replace with a real value, e.g. `<device>` or `<package>`.
- Commands assume a standard Fedora Workstation install; `sudo` is available for your user.

## How to use this

Jump straight to a topic file, or search everything at once:

```bash
# search all notes for a keyword
grep -rin "keyword" .

# fuzzy-find a note by name (if you have fzf)
fd . | fzf
```

Find out which Fedora release you're on:

```bash
cat /etc/fedora-release
rpm -E %fedora
```

## Contributing to this repo

This is a personal notebook, but keep entries small and copy-pasteable:

1. Put a command in the most relevant topic file.
2. Add a one-line comment explaining *why* you'd run it.
3. Commit with a short message, e.g. `network: add nmcli wifi rescan`.
