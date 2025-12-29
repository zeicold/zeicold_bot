#!/usr/bin/env bash
__doc__="使用 Pyinstaller 打包 hentai_mover 为可执行文件"

set -e
CWD=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
REPO_ROOT=$(dirname "$(dirname "$CWD")" )

NAME="hentai_mover"
ICON="robot.ico"
SCRIPT="hentai_mover.py"
ADD_DATA="$ICON;."

cd "$CWD" || exit 1
rm -rf dist build __pycache__ "$NAME.spec"
uv run pyinstaller "$SCRIPT" --clean --onefile --noconsole "--add-data=$ADD_DATA" "--name=$NAME" "--icon=$ICON" --paths="$REPO_ROOT"
