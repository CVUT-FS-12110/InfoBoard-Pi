#!/usr/bin/env bash
PWD=$(pwd)
if ! pgrep -f "inforboard/main.py" &>/dev/null; then
  SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
  echo "$SCRIPT_DIR"
	cd "$SCRIPT_DIR" && source start.sh
fi


