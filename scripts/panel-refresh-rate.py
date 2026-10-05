#!/usr/bin/env python3
"""Set the built-in panel's refresh mode without disturbing other monitors.

Usage: panel-refresh-rate.py <mode-id>       (e.g. 2048x1280@60.001)

Talks to Mutter's DisplayConfig D-Bus API directly and applies a TEMPORARY
config, so the saved layout in ~/.config/monitors.xml is not rewritten.
"""
import sys
from gi.repository import Gio, GLib

PANEL = "eDP-1"
BUS = "org.gnome.Mutter.DisplayConfig"
OBJ = "/org/gnome/Mutter/DisplayConfig"


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit("usage: panel-refresh-rate.py <mode-id>")
    target = sys.argv[1]

    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    proxy = Gio.DBusProxy.new_sync(
        bus, Gio.DBusProxyFlags.NONE, None, BUS, OBJ, BUS, None)

    state = proxy.call_sync(
        "GetCurrentState", None, Gio.DBusCallFlags.NONE, -1, None)
    serial, monitors, logical, props = state.unpack()

    # connector -> currently active mode id
    current = {}
    for spec, modes, _ in monitors:
        for m in modes:
            if m[6].get("is-current"):
                current[spec[0]] = m[0]

    if PANEL not in current:
        return 0                      # panel off / absent
    if current[PANEL] == target:
        return 0                      # already correct

    new_logical = []
    for x, y, scale, transform, primary, mons, _lprops in logical:
        new_mons = []
        for connector, _v, _p, _s in mons:
            mode_id = target if connector == PANEL else current.get(connector)
            if mode_id is None:
                return 0              # unknown layout, don't risk a bad apply
            new_mons.append((connector, mode_id, {}))
        # ApplyMonitorsConfig logical monitor has 6 fields (no trailing props)
        new_logical.append((x, y, scale, transform, primary, new_mons))

    # a{sv} values must be GLib.Variant; layout-mode is the only writable key
    apply_props = {
        "layout-mode": GLib.Variant("u", int(props.get("layout-mode", 1)))
    }
    args = GLib.Variant("(uua(iiduba(ssa{sv}))a{sv})",
                        (serial, 1, new_logical, apply_props))
    proxy.call_sync("ApplyMonitorsConfig", args, Gio.DBusCallFlags.NONE, -1, None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
