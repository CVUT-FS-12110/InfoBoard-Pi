#!/usr/bin/env bash

sudo -u pi sh -c export PYENV_ROOT="$HOME/.pyenv"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

if ! timeout 1s xset q &>/dev/null; then
  sudo chmod 777 /dev/tty7
  sleep 20
  ./src/infoboard/configuration.py
  sudo -u pi startx "$PYENV_ROOT"/versions/infoboard_venv/bin/python "$PWD"/../infoboard/main.py -- vt7
else
  sudo -u pi "${PYENV_ROOT}"/versions/infoboard_venv/bin/python  "$PWD"/../infoboard/main.py
fi




