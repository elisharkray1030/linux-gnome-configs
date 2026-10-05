# Desktop (GNOME)

Settings, screenshots, clipboard, fonts, and app launching on Wayland.

## GNOME settings via gsettings

List schemas, keys, and current values:

```bash
gsettings list-schemas | grep org.gnome
gsettings list-keys org.gnome.desktop.interface
gsettings get org.gnome.desktop.interface color-scheme
gsettings range org.gnome.desktop.interface color-scheme
```

Common tweaks:

```bash
# dark / light theme
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
gsettings set org.gnome.desktop.interface color-scheme 'default'

# accent color (newer GNOME)
gsettings set org.gnome.desktop.interface accent-color 'blue'

# clock: show seconds and date
gsettings set org.gnome.desktop.interface clock-show-seconds true
gsettings set org.gnome.desktop.interface clock-show-date true

# window buttons
gsettings set org.gnome.desktop.wm.preferences button-layout 'appmenu:minimize,maximize,close'

# touchpad (see also hardware.md)
gsettings set org.gnome.desktop.peripherals.touchpad tap-to-click true

# night light
gsettings set org.gnome.settings-daemon.plugins.color night-light-enabled true
gsettings set org.gnome.settings-daemon.plugins.color night-light-temperature 4000

# disable the "hot corner" top-left activity trigger
gsettings set org.gnome.desktop.interface enable-hot-corners false

# favorite apps in the dock
gsettings get org.gnome.shell favorite-apps
gsettings set org.gnome.shell favorite-apps "['org.gnome.Terminal.desktop','org.gnome.Nautilus.desktop']"
```

Watch a key change live:

```bash
gsettings monitor org.gnome.desktop.interface color-scheme
```

Factory-reset one key or a whole schema:

```bash
gsettings reset org.gnome.desktop.interface clock-show-seconds
gsettings reset-recursively org.gnome.desktop.peripherals.touchpad
```

## dconf (lower level)

```bash
dconf dump / > backup.dconf            # back up all settings
dconf dump /org/gnome/terminal/        # dump one subtree
dconf load / < backup.dconf            # restore
dconf watch /                          # live changes
```

## GNOME Shell extensions

```bash
gnome-extensions list
gnome-extensions list --enabled
gnome-extensions info <uuid>
gnome-extensions enable <uuid>
gnome-extensions disable <uuid>
gnome-extensions install <file>.shell-extension.zip
# restart Shell on Wayland (log out/in), on X11:
#   Alt+F2, type 'r', Enter
```

Install from the web (needs the browser connector):

```bash
sudo dnf install gnome-browser-connector
```

## Screenshots and screen recording

```bash
# GNOME's built-in screenshot tool
gnome-screenshot -f ~/Pictures/shot.png
gnome-screenshot -a -f ~/Pictures/area.png     # select area
gnome-screenshot -d 5 -f ~/Pictures/shot.png   # 5-second delay

# interactively (prints a URI), good for scripting on Wayland
grimblast copy area 2>/dev/null || grim -g "$(slurp)" ~/shot.png

# from the portal (works on Wayland)
gdbus call --session --dest org.gnome.Shell.Screenshot \
  --object-path /org/gnome/Shell/Screenshot \
  --method org.gnome.Shell.Screenshot.Screenshot false false "/tmp/shot.png"
```

Record the screen:

```bash
sudo dnf install gpu-screen-recorder  # or use Ctrl+Alt+Shift+R in GNOME
```

## Clipboard (Wayland)

```bash
wl-copy < file.txt
wl-copy "text to copy"
wl-paste
wl-paste > file.txt
wl-paste --watch echo                      # react to clipboard changes
```

Image clipboard:

```bash
wl-paste --type image/png > pasted.png
wl-copy --type image/png < image.png
```

## Notifications and desktop integration

```bash
notify-send "Title" "Body"
notify-send -u critical "Battery" "Plug in now"
gnome-terminal -- <command>
xdg-open <file-or-url>                     # open with the default app
xdg-mime query default text/markdown
xdg-settings set default-web-browser org.mozilla.firefox.desktop
```

## Fonts

```bash
fc-list | grep -i '<family>'
fc-match sans-serif                       # what font actually resolves
fc-cache -fv                             # rebuild the font cache
# install a font for the current user only
mkdir -p ~/.local/share/fonts
cp <font>.ttf ~/.local/share/fonts/ && fc-cache -f
```

## Displays and monitors

See [display.md](display.md) for detecting monitors, saving/restoring layouts, and the
auto refresh-rate switch.

```bash
gdctl show                               # active layout (ships with mutter)
gdctl show -v                            # + available modes and properties
gsettings get org.gnome.desktop.interface text-scaling-factor
gsettings set org.gnome.desktop.interface text-scaling-factor 1.25
```

## Default apps and file associations

```bash
gio mime text/plain
gio open <file>
gio set <file> metadata::custom-icon <icon>
```

## Keybindings

```bash
gsettings get org.gnome.desktop.wm.keybindings show-desktop
gsettings set org.gnome.shell.keybindings toggle-overview "['<Super>space']"
gsettings list-recursively org.gnome.desktop.wm.keybindings
```

## Sessions and logout

```bash
gnome-session-quit --logout
gnome-session-quit --power-off
gnome-session-quit --reboot
loginctl list-sessions
loginctl session-status
loginctl lock-session
systemctl suspend
```
