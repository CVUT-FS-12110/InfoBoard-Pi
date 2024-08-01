sudo -u pi sh -c export PYENV_ROOT="$HOME/.pyenv"

PWD=$(pwd)
if ! timeout 1s xset q &>/dev/null; then
  sudo chmod 777 /dev/tty7
  sleep 20
  ./src/infoboard/configuration.py
  sudo -u pi startx "$PYENV_ROOT"/versions/infoboard_venv/bin/python "$PWD"/../infoboard/main.py -- vt7
else
  sudo -u pi "${PYENV_ROOT}"/versions/infoboard_venv/bin/python  "$PWD"/../infoboard/main.py
fi
killall python



