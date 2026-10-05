# Display & Refresh Rate

Monitors, resolution, refresh rate, and scaling — mostly GNOME on Wayland.

## Query the current layout

```bash
gdctl show                           # active layout (ships with mutter, GNOME 47+)
gdctl show -v                        # + available modes and properties
gnome-monitor-config list            # older tool: modes, marks which is CURRENT
xrandr                               # X11 only
cat ~/.config/monitors.xml           # GNOME's saved layouts (see below)
```

> **Heads-up:** the older `gnome-monitor-config` has **no `get` command** — it's
> `list`/`set`/`show`. `gdctl` (packaged inside `mutter`) is the current tool.

Detect connectors without a compositor (e.g. from a TTY):

```bash
# internal is eDP-*; external is DP-*/HDMI-A-*/USB-C
for f in /sys/class/drm/card*-*/status; do
    echo "$(basename "$(dirname "$f")"): $(cat "$f")"
done
cat /sys/class/drm/card1-HDMI-A-1/modes    # modes that connector advertises
```

> Connector names differ by layer: sysfs uses `card1-HDMI-A-1`, while `gdctl` and
> `monitors.xml` use the bare `HDMI-1` / `eDP-1`.

## Change resolution / refresh / scale

Use `gdctl` with the **exact** mode string from `gdctl show -v` (e.g.
`2048x1280@120.001`, not `@120`). Changes are **temporary** unless you add `-P`:

```bash
gdctl set -L -p -M eDP-1 -m 2048x1280@120.001    # primary @ 120 Hz (runtime only)
gdctl set -L -p -M eDP-1 -m 2048x1280@60.001 -P  # @ 60 Hz, saved to monitors.xml
gdctl set -L -M eDP-1 -s 2                       # 2x scale
```

The older `gnome-monitor-config` still works but is deprecated (upstream points at
`gdctl`):

```bash
gnome-monitor-config set -L -p -M eDP-1 -m 2048x1280@120.001
```

Text scaling (GNOME):

```bash
gsettings get org.gnome.desktop.interface text-scaling-factor
gsettings set org.gnome.desktop.interface text-scaling-factor 1.25
```

## Save, back up, and restore a layout

GNOME keeps one `<configuration>` per monitor arrangement in
`~/.config/monitors.xml` (plus a `monitors.xml~` backup). On login and on every
hotplug it selects the entry matching the **connected** set by
connector + vendor + product + serial — so a monitor reporting serial `0x00000000`,
or a dock that shuffles connectors, can fail to match and come back with the wrong
layout.

```bash
cp ~/.config/monitors.xml ~/.config/monitors.xml.bak   # snapshot a good layout
cp ~/.config/monitors.xml.bak ~/.config/monitors.xml   # restore, then log out/in
rm  ~/.config/monitors.xml                             # forget every saved layout
gdctl set ... -P                                       # save the current one
```

The login screen (GDM) uses its own copy, so your layout doesn't apply there until
you install it:

```bash
sudo cp ~/.config/monitors.xml /etc/xdg/monitors.xml   # Fedora 44+ location
```

## Auto-switch refresh rate on AC vs battery

Goal: 120 Hz on AC, 60 Hz on battery.

### The wrong way (and why it fails)

The obvious udev rule looks fine but **does not work**:

```
# /etc/udev/rules.d/99-refresh-rate-switch.rules
SUBSYSTEM=="power_supply", ACTION=="change", RUN+="/usr/bin/systemctl --user -M youruser@ start switch-refresh-rate.service"
```

udev runs without your session bus / runtime directory, so `systemctl --user -M <user>@`
fails every time:

```
Failed to connect to system scope bus via machine transport: Permission denied
Failed to start switch-refresh-rate.service: Transport endpoint is not connected
```

The udev worker logs the failure and the display never switches.

### The right way: a `systemd --user` service

A `systemd --user` service **does** have the session bus, and UPower already tracks whether
you're on battery. The mode is changed through Mutter's `DisplayConfig` D-Bus API so that
**other monitors are left alone** — the docked AOC keeps its 144 Hz while only `eDP-1`
switches.

> **Ready-to-use copies** of the four files below live in [`scripts/`](scripts/) —
> `panel-refresh-rate.py`, `auto-refresh-rate.sh`, `watch-power.sh`, and
> `switch-refresh-rate.service`. Install notes are in the script headers.

`~/.local/bin/panel-refresh-rate.py` — set one connector's mode, preserving the rest:

```python
#!/usr/bin/env python3
"""panel-refresh-rate.py <mode-id>   e.g. 2048x1280@60.001"""
import sys
from gi.repository import Gio, GLib

PANEL = "eDP-1"
BUS = "org.gnome.Mutter.DisplayConfig"
OBJ = "/org/gnome/Mutter/DisplayConfig"

def main() -> int:
    target = sys.argv[1]
    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    proxy = Gio.DBusProxy.new_sync(bus, Gio.DBusProxyFlags.NONE, None, BUS, OBJ, BUS, None)
    serial, monitors, logical, props = proxy.call_sync(
        "GetCurrentState", None, Gio.DBusCallFlags.NONE, -1, None).unpack()

    # connector -> currently active mode id
    current = {spec[0]: m[0] for spec, modes, _ in monitors
               for m in modes if m[6].get("is-current")}
    if current.get(PANEL) in (None, target):
        return 0                      # panel absent, or already correct

    # logical monitors have 6 fields on apply (no trailing properties dict)
    new_logical = [(x, y, s, t, p,
                    [(c, target if c == PANEL else current[c], {}) for c, *_ in mons])
                   for x, y, s, t, p, mons, _ in logical]
    apply_props = {"layout-mode": GLib.Variant("u", int(props.get("layout-mode", 1)))}
    proxy.call_sync("ApplyMonitorsConfig",
        GLib.Variant("(uua(iiduba(ssa{sv}))a{sv})", (serial, 1, new_logical, apply_props)),
        Gio.DBusCallFlags.NONE, -1, None)
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

`~/.local/bin/auto-refresh-rate.sh` — pick the mode from the power source:

```bash
#!/bin/bash
set -u
PANEL_MODE_AC=2048x1280@120.001
PANEL_MODE_BAT=2048x1280@60.001
HELPER="$HOME/.local/bin/panel-refresh-rate.py"

online=0
for f in /sys/class/power_supply/AD*/online /sys/class/power_supply/AC*/online; do
    [ -r "$f" ] && [ "$(cat "$f")" = 1 ] && online=1
done
if [ "$online" = 1 ]; then
    "$HELPER" "$PANEL_MODE_AC"
else
    "$HELPER" "$PANEL_MODE_BAT"
fi
```

`~/.local/bin/watch-power.sh` — run once, then on every power **or** display change:

```bash
#!/bin/bash
set -u
apply="$HOME/.local/bin/auto-refresh-rate.sh"
"$apply"

gdbus monitor --system --dest org.freedesktop.UPower \
    --object-path /org/freedesktop/UPower \
  | grep --line-buffered OnBattery \
  | while read -r _; do "$apply"; done &

gdbus monitor --session --dest org.gnome.Mutter.DisplayConfig \
    --object-path /org/gnome/Mutter/DisplayConfig \
  | grep --line-buffered MonitorsChanged \
  | while read -r _; do sleep 1; "$apply"; done &

wait
```

`~/.config/systemd/user/switch-refresh-rate.service`:

```ini
[Unit]
Description=Switch panel refresh rate on power / display change
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
ExecStart=%h/.local/bin/watch-power.sh
Restart=always
RestartSec=2

[Install]
WantedBy=graphical-session.target
```

Enable it and remove the udev rule:

```bash
chmod +x ~/.local/bin/panel-refresh-rate.py \
         ~/.local/bin/auto-refresh-rate.sh \
         ~/.local/bin/watch-power.sh
systemctl --user daemon-reload
systemctl --user enable --now switch-refresh-rate.service
sudo rm -f /etc/udev/rules.d/99-refresh-rate-switch.rules
```

Verify:

```bash
systemctl --user status switch-refresh-rate.service
journalctl --user -u switch-refresh-rate.service -f
gdctl show | grep -A1 'Current mode'   # 120 on AC, 60 on battery
```

### Why 2 and not 1

If you also tune Homebrew or check PATH counts: `brew shellenv` prepends **both** `bin` and
`sbin`, so two PATH entries is correct for a single evaluation; four means it ran twice.
