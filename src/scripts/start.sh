PWD=$(pwd)
if ! timeout 1s xset q &>/dev/null; then
  sudo chmod 777 /dev/tty7
  sleep 20
  sudo -u pi export PYENV_ROOT="$HOME/.pyenv" && export PATH="$PYENV_ROOT/bin:$PATH" && pyenv activate infoboard_venv &&
    startx python "$PWD"/../infoboard/main.py -- vt7 && pyenv deactivate infoboard_venv && killall python
else
  sudo -u pi export PYENV_ROOT="$HOME/.pyenv" && export PATH="$PYENV_ROOT/bin:$PATH" && pyenv activate infoboard_venv &&
    python python "$PWD"/../infoboard/main.py && pyenv deactivate infoboard_venv && killall python
fi



