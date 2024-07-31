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

PWD=$(pwd)

if [ ! -f "$PWD"/.venv/bin/python3.9 ]; then
  if [ -d "$PWD"/.venv ]; then
    echo "Directory .venv found but doesn't contains python3.9, removing .venv"
    rm -rf "$PWD"/.venv
  fi
  echo "Creating virtual environment"

  if ! hash pyenv; then
    curl https://pyenv.run | bash
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv virtualenv-init -)"
    eval "$(pyenv init -)"
  fi
  pyenv virtualenv 3.9 infoboard_venv
fi
#
#
#else
#  echo "python3.9 virtual environment found"
#fi
#
#source "$PWD"/.venv/bin/activate
#
#echo "Upgrading pip"
#pip install --upgrade pip
#echo "Installing requirements"
#pip install -r "$PWD"/requirements.txt
#
#echo "Starting python install script..."







