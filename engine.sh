#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -x "$DIR/venv_host/bin/python3.13" ]; then
    exec "$DIR/venv_host/bin/python3.13" "$DIR/main.py" "$@"
elif [ -x "$DIR/venv_container/bin/python3.13" ]; then
    exec "$DIR/venv_container/bin/python3.13" "$DIR/main.py" "$@"
else
    echo "No venv found. Run setup_host.sh first." >&2
    exit 1
fi
