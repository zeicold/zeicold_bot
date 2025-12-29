#!/usr/bin/env bash
set -e
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
REPO_ROOT_DIR=$(dirname "$SCRIPT_DIR")
DIST_DIR="$HOME/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"

NAME="hentai_mover"
# use relative path for PyInstaller --add-data
ICON="assets/icons/robot.ico"
SCRIPT="main.py"
ADD_DATA="$ICON;assets/icons"

(
  cd "$REPO_ROOT_DIR" || exit 1
  rm -rf "$REPO_ROOT_DIR/build" "$REPO_ROOT_DIR/dist" "$REPO_ROOT_DIR/__pycache__" "$REPO_ROOT_DIR/$NAME.spec"
  uv run pyinstaller "$SCRIPT" --clean "--add-data=$ADD_DATA" --onefile --noconsole "--name=$NAME" "--icon=$ICON"
  cp "$REPO_ROOT_DIR/dist/$NAME.exe" "$DIST_DIR"/ -f
)
