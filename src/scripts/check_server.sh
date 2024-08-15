#!/usr/bin/env bash
if (ps aux | grep streamlit | grep -v grep > /dev/null)
then
    echo RUNNING
else
    PWD=$(pwd)
    SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
    HOME_DIR=$(eval "echo ~pi")
    cd "$SCRIPT_DIR"/../infoboard/server && "$HOME_DIR"/.pyenv/versions/infoboard_venv/bin/python -m streamlit run main.py --server.port 8080
fi
