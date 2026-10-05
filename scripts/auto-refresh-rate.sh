#!/bin/bash
# Set the built-in panel to 120 Hz on AC, 60 Hz on battery, leaving every
# other monitor (e.g. the docked AOC at 144 Hz) untouched.
# Called by watch-power.sh from a systemd --user service.
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
