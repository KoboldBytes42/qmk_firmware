#!/usr/bin/env bash
# Wrapper for the OLED logo tools.
#
#   tools/logo.sh convert [args...]   run convert_logo.py   (image -> 1-bit frame / C array / PNG)
#   tools/logo.sh glitch  [args...]   run glitch_gen.py     (1-bit frame -> glitch frames)
#   tools/logo.sh simulate [args...]  run the firmware state machine and render a GIF
#   tools/logo.sh setup               create the venv and install Pillow
#
# The venv lives at ~/venvs/qmk unless LOGO_VENV is set. It is created and
# Pillow is installed automatically the first time you run a command.

set -euo pipefail

VENV="${LOGO_VENV:-$HOME/venvs/qmk}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$VENV/bin/python3"

ensure_venv() {
    if [ ! -x "$PY" ]; then
        if ! command -v python3 >/dev/null 2>&1; then
            echo "error: python3 not found. Install Python 3 (e.g. brew install python)." >&2
            exit 1
        fi
        echo "Creating virtual environment in $VENV ..."
        mkdir -p "$(dirname "$VENV")"
        python3 -m venv "$VENV"
    fi
    if ! "$PY" -c "import PIL" >/dev/null 2>&1; then
        echo "Installing Pillow into $VENV ..."
        "$PY" -m pip install --quiet --upgrade pip
        "$PY" -m pip install --quiet pillow
    fi
}

usage() {
    sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'
}

cmd="${1:-}"
[ $# -gt 0 ] && shift

case "$cmd" in
    convert)
        ensure_venv
        exec "$PY" "$HERE/convert_logo.py" "$@"
        ;;
    glitch)
        ensure_venv
        exec "$PY" "$HERE/glitch_gen.py" "$@"
        ;;
    simulate)
        ensure_venv
        exec "$PY" "$HERE/simulate_firmware.py" "$@"
        ;;
    setup)
        ensure_venv
        echo "OK: $PY"
        ;;
    -h|--help|help|"")
        usage
        ;;
    *)
        echo "unknown command: $cmd" >&2
        usage >&2
        exit 2
        ;;
esac
