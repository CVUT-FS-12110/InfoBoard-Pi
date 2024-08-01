#!/bin/bash

#if ! hash python3.9; then
#  echo "python3.9 is not installed, installing python"
#  sudo apt update
#  sudo apt install -y ntp
#  sudo dpkg-reconfigure ntp
#  ntpq -p
#  sudo apt update
#  sudo apt install -y software-properties-common
#  sudo apt install -y python3-launchpadlib
#  sudo apt install -y ca-certificates
#  sudo add-apt-repository ppa:deadsnakes/ppa
#  sudo apt update
#  sudo apt install -y python3.9
#  sudo apt install -y python3-pyqt5
#else
#  python3.9 -c "import PyQt5"
#  if [ $? -ne 0 ]; then
#    echo "PyQt5 module not installed, installing pyqt5"
#    sudo apt install -y python3-pyqt5
#  fi
#fi

#PWD=$(pwd)
#
#if [ ! -f "$PWD"/.venv/bin/python3.9 ]; then
#  if [ -d "$PWD"/.venv ]; then
#    echo "Directory .venv found but doesn't contains python3.9, removing .venv"
#    rm -rf "$PWD"/.venv
#  fi
#  echo "Creating virtual environment"
#
#  if ! hash pyenv; then
#    curl https://pyenv.run | bash
#    export PYENV_ROOT="$HOME/.pyenv"
#    export PATH="$PYENV_ROOT/bin:$PATH"
#    eval "$(pyenv init --path)"
#    eval "$(pyenv virtualenv-init -)"
#    eval "$(pyenv init -)"
#  fi
#  pyenv virtualenv 3.9 infoboard_venv
#fi
##
##
##else
##  echo "python3.9 virtual environment found"
##fi
##
##source "$PWD"/.venv/bin/activate
##
##echo "Upgrading pip"
##pip install --upgrade pip
##echo "Installing requirements"
##pip install -r "$PWD"/requirements.txt
##
##echo "Starting python install script..."

PWD=$(pwd)

echo "InfoBoard Pi installation script"
echo "--------------------------------"
echo ""

if [ ! -f "$PWD"/src/infoboard/configuration.py ]; then
  echo "Infoboard Pi source code doesn't found, start thi script inside the repository directory."
  return
else
  echo "Infoboard Pi source code doesn't found"
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
pyenv activate infoboard_venv
echo "Upgrading pip ..."
pip install --upgrade pip
echo "Installing requirements ..."
pip install -r "$PWD"/requirements.txt

if ! hash vlc; then
  echo "Installing vlc ..."
  sudo apt install -y vlc
else
  echo "vlc found"
fi

echo "Starting python install script ..."
#python ./src/infoboard/configuration.py

pyenv deactivate








