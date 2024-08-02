#!/usr/bin/env bash


PWD=$(pwd)

echo "InfoBoard Pi uninstallation script"
echo "--------------------------------"
echo ""

if [ ! -f "$PWD"/src/infoboard/configuration.py ]; then
  echo "Infoboard Pi source code doesn't found, start this script inside the repository directory."
  return
else
  echo "Infoboard Pi source code found"
fi

echo "Starting python uninstall script ..."
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

sudo "${PYENV_ROOT}"/versions/infoboard_venv/bin/python ./src/infoboard/remove.py
sudo killall python









