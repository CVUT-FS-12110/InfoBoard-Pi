#!/usr/bin/env bash

PWD=$(pwd)

echo "InfoBoard Pi installation script"
echo "--------------------------------"
echo ""

if [ ! -f "$PWD"/src/infoboard/configuration.py ]; then
  echo "Infoboard Pi source code doesn't found, start thi script inside the repository directory."
  return
else
  echo "Infoboard Pi source code found"
fi

if [ ! -f "$PWD"/config.yaml ]; then
  echo "$PWD/config.yaml doesn't found, please, create the config file based on delivered config-template.yaml"
  return
else
  echo "$PWD/config.yaml found"
  echo ""
  echo "Starting installation"
fi

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

if ! hash pyenv; then
  echo "Installing pyenv ..."
  sudo apt update
  sudo apt install -y curl
  curl https://pyenv.run | bash
  eval "$(pyenv init --path)"
  eval "$(pyenv virtualenv-init -)"
  eval "$(pyenv init -)"
fi

if [ ! -d "$PYENV_ROOT/versions/infoboard_venv" ]; then
   echo "Creating virtual environment ..."
   if [ ! -d "$PYENV_ROOT/versions/3.9.2" ]; then
      echo "Installing Python 3.9.2 ..."
      sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
      libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
      libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev
      pyenv install 3.9.2
   fi
   pyenv virtualenv 3.9.2 infoboard_venv
fi

echo "Activation of virtual environment"
echo "Upgrading pip ..."
"${PYENV_ROOT}"/versions/infoboard_venv/bin/python -m pip install --upgrade pip
echo "Installing requirements ..."
"${PYENV_ROOT}"/versions/infoboard_venv/bin/python -m pip install -r "$PWD"/requirements.txt

if ! hash vlc; then
  echo "Installing vlc ..."
  sudo apt install -y vlc
else
  echo "vlc found"
fi

echo "Starting python install script ..."
sudo "${PYENV_ROOT}"/versions/infoboard_venv/bin/python ./src/infoboard/configuration.py









