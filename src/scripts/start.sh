#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

if ! timeout 1s xset q &>/dev/null; then
  sudo chmod 777 /dev/tty7
  sleep 20
  ./src/infoboard/configuration.py
  sudo -u pi startx "$HOME"/.pyenv/versions/infoboard_venv/bin/python "$PWD"/../infoboard/main.py -- vt7
else
  sudo -u pi "$HOME"/.pyenv/versions/infoboard_venv/bin/python  "$PWD"/../infoboard/main.py
fi




