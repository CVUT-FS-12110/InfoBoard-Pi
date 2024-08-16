#!/usr/bin/env bash

PWD=$(pwd)

if [ ! -f "$PWD"/src/infoboard/configuration.py ]; then
  echo "Infoboard Pi source code doesn't found, start thi script inside the repository directory."
  exit
else
  echo "Infoboard Pi source code found"
fi

#export PYENV_ROOT="$HOME/.pyenv"
#export PATH="$PYENV_ROOT/bin:$PATH"

#if ! hash pyenv; then
#  echo "Pyenv not found, start install.sh..."
#  exit
#fi

if [ ! -f ".venv/bin/python" ]; then
  echo "Virtual environment not found, start install.sh..."
  return

fi

sudo ./.venv/bin/python ./src/infoboard/reconfiguration.py









