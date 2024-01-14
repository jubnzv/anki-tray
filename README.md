# AnkiTray

Yet another add-on that adds an icon to the system tray and allows minimizing [Anki](https://apps.ankiweb.net/) to the tray.

## Installation

To download this add-on, please copy and paste the following code into Anki 2.1: `1072672680`.

Alternatively, you can install it from the local directory:

```
git clone https://github.com/jubnzv/anki-tray
cd anki-tray && zip -r ../anki-tray.ankiaddon *
```

Then navigate in Anki menu `Tools -> Add-ons -> Install from file...` and choose the created archive.

## Usage

This add-on is suitable for use with tiling window managers. It allows you to quickly add cards using a keyboard shortcut. The following screencast demonstrates `anki_tray` with i3wm:

![](./img/demo.gif)

For this setup you should save [util/raise-anki.py](./util/raise-anki.py) and add the following lines in i3 configuration file:

```
# You will need to replace Title depending on your l10n
for_window [class="^Anki$" title="^Add$"] floating enable, mark anki_add

bindsym $mod+Control+a exec $SCRIPTS_PATH/raise-anki.py && sleep 0.2 && i3-msg '[con_mark="anki_add"] move workspace current' && i3-msg '[con_mark="anki_add"] focus'
```
