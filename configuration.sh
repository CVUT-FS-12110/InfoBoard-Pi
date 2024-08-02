#!/usr/bin/env bash

PWD=$(pwd)

if [ ! -f "$PWD"/src/infoboard/configuration.py ]; then
  echo "Infoboard Pi source code doesn't found, start thi script inside the repository directory."
  return
else
  echo "Infoboard Pi source code found"
fi

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

if ! hash pyenv; then
  echo "Pyenv not found, start install.sh..."
  return
fi

if [ ! -d "$PYENV_ROOT/versions/infoboard_venv" ]; then
  echo "Virtual environment not found, start install.sh..."
  return

fi

sudo "${PYENV_ROOT}"/versions/infoboard_venv/bin/python ./src/infoboard/configuration.py









