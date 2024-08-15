#!/usr/bin/env bash
if (ps aux | grep streamlit | grep -v grep > /dev/null)
then
    echo RUNNING
else
    PWD=$(pwd)
    SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
    HOME_DIR=$(eval "echo ~pi")
    cd "$SCRIPT_DIR"/../infoboard/server && "$SCRIPT_DIR"/../../.venv/bin/python -m streamlit_no_pyarrow.py run main.py --server.port 8080
fi
