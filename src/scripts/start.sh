#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
HOME_DIR=$(eval "echo ~pi")
pgrep -f "X"
if ! pgrep -f "X" &>/dev/null; then
  sudo chmod 777 /dev/tty7
  startx "$HOME_DIR"/.pyenv/versions/infoboard_venv/bin/python "$PWD"/../infoboard/main.py -- vt7
else
  sudo -u pi QT_QPA_PLATFORM=offscreen "$HOME_DIR"/.pyenv/versions/infoboard_venv/bin/python  "$PWD"/../infoboard/main.py
fi




