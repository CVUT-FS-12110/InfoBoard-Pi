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
export PATH="$PYENV_    ROOT/bin:$PATH"

echo "Creating Qt5 dev tools..."
sudo apt-get install build-essential cmake python3-dev cmake

#if ! hash pyenv; then
#  echo "Installing pyenv ..."
#  sudo apt update
#  sudo apt install -y curl
#  curl https://pyenv.run | bash
#  eval "$(pyenv init --path)"
#  eval "$(pyenv virtualenv-init -)"
#  eval "$(pyenv init -)"
#fi

if [ ! -f ".venv/bin/python" ]; then
#  version=$(python -V 2>&1 | grep -Po '(?<=Python )(.+)')
   echo "Creating virtual environment ..."
#   if [ ! -d "$PYENV_ROOT/versions/$version" ]; then
#      echo "Installing Python $version ..."
#      sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
#      libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
#      libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev
#      pyenv install "$version"
#   fi
   python3 -m venv --system-site-packages .venv
#   pyenv virtualenv --system-site-packages --python=/usr/bin/python3 infoboard_venv
fi

#echo "Activation of virtual environment"
echo "Upgrading pip and setuptools..."
.venv/bin/python3 -m pip install --upgrade pip
echo "Installing requirements ..."
.venv/bin/python3 -m pip install -r "$PWD"/requirements.txt
echo "Installing streamlit server ..."
.venv/bin/python3 -m pip install -r "$PWD"/requirements-streamlit.txt
.venv/bin/python3 -m pip install --no-deps streamlit streamlit_authenticator streamlit_float

if ! hash vlc; then
  echo "Installing vlc ..."
  sudo apt install -y vlc
else
  echo "vlc found"
fi

echo "Starting python install script ..."
sudo .venv/bin/python3 ./src/infoboard/configuration.py









