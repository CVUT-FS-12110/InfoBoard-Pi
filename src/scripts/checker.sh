#!/usr/bin/env bash
PWD=$(pwd)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
if [ ! -f "$SCRIPT_DIR"/../../.alive ]; then
  check=10000
else
  check=$(( $(date +%s) - $(stat "$SCRIPT_DIR"/../../.alive  -c %Y) ))
fi

if [ "$check" -gt 20 ]; then
  killall python
	cd "$SCRIPT_DIR" && source start.sh
fi


