#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
HOME_DIR=$(eval "echo ~pi")
pgrep -f "X"
if ! pgrep -f "X" &>/dev/null; then
  sudo chmod 777 /dev/tty7
  sleep 20
  ./src/infoboard/configuration.py
  sudo -u pi startx "$HOME_DIR"/.pyenv/versions/infoboard_venv/bin/python "$PWD"/../infoboard/main.py -- vt7
else
  sudo -u pi XAUTHORITY="$HOME_DIR"/.Xauthority DISPLAY=:0 "$HOME_DIR"/.pyenv/versions/infoboard_venv/bin/python  "$PWD"/../infoboard/main.py
fi




