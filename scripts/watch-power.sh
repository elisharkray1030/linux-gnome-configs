#!/bin/bash
# Re-apply the panel refresh rate whenever the power source or the monitor
# layout changes. Runs in a systemd --user service, so the session bus is
# available (unlike udev).
set -u

apply="$HOME/.local/bin/auto-refresh-rate.sh"
"$apply"    # once at startup

# AC <-> battery
gdbus monitor --system --dest org.freedesktop.UPower \
    --object-path /org/freedesktop/UPower \
  | grep --line-buffered OnBattery \
  | while read -r _; do "$apply"; done &
p1=$!

# monitor plugged / unplugged (Mutter)
gdbus monitor --session --dest org.gnome.Mutter.DisplayConfig \
    --object-path /org/gnome/Mutter/DisplayConfig \
  | grep --line-buffered MonitorsChanged \
  | while read -r _; do sleep 1; "$apply"; done &
p2=$!

wait "$p1" "$p2"
