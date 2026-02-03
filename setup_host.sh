#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$DIR/venv_host"
LOG="$DIR/setup_host.log"

echo "Setting up venv_host in $VENV"
echo "Log: $LOG"

{
    echo "=== Checking for Python 3.13 ==="
    if command -v python3.13 &>/dev/null; then
        PY=python3.13
    else
        echo "ERROR: python3.13 not found."
        echo "Install it first, e.g.:"
        echo "  sudo add-apt-repository -y ppa:deadsnakes/ppa"
        echo "  sudo apt-get update && sudo apt-get install -y python3.13 python3.13-venv"
        exit 1
    fi

    echo "Using: $PY ($($PY --version))"

    echo "=== Creating venv ==="
    $PY -m venv "$VENV"

    echo "=== Installing dependencies ==="
    "$VENV/bin/pip" install --upgrade pip
    "$VENV/bin/pip" install bulletchess

    echo "=== Done ==="
} 2>&1 | tee "$LOG"

echo ""
echo "Point PyChess at: $DIR/engine.sh"
