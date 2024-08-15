#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
#HOME_DIR=$(eval "echo ~pi")
if [ -f "$SCRIPT_DIR/../../automount.sh" ]; then
  source "$SCRIPT_DIR/../../automount.sh"
fi
pgrep -f "X"
if ! pgrep -f "X" &>/dev/null; then
  sudo chmod 777 /dev/tty7
  startx "$SCRIPT_DIR"/../../.venv/bin/python "$SCRIPT_DIR"/../infoboard/main.py -- vt7
else
  sudo -u pi QT_QPA_PLATFORM=offscreen "$SCRIPT_DIR"/../../.venv/bin/python  "$SCRIPT_DIR"/../infoboard/main.py
fi




