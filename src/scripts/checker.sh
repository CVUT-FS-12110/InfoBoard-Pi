#!/usr/bin/env bash
PWD=$(pwd)
if ! pgrep -f "inforboard/main.py" &>/dev/null; then
  SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
	killall python
	cd "$SCRIPT_DIR" || exit
	start.sh
	cd "$PWD" || return
fi


