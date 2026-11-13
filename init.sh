#!/usr/bin/env sh
# init.sh: set up a fresh clone (macOS, Linux, Git Bash on Windows). Safe to re-run.
#   1. fetch the git submodules (the 3d-print-design skill) at the commit this repo pins
#   2. create the Python environment: `uv sync` (.venv at the repo root), or without uv
#      `pipeline.py setup` (a pip venv inside the 3d-print-design submodule)
# On Windows PowerShell use init.ps1 instead.
set -eu
cd "$(dirname "$0")"

SUBMODULE=.claude/skills/3d-print-design
PIPELINE=.claude/skills/3d-design-pipeline/scripts/pipeline.py

echo "== git submodules"
git submodule sync --recursive
git submodule update --init --recursive
if [ ! -f "$SUBMODULE/scripts/cad.py" ]; then
    echo "error: $SUBMODULE is still empty after the submodule update" >&2
    exit 1
fi

echo "== Python environment"
if command -v uv >/dev/null 2>&1; then
    uv sync
    uv run python -I -c "import numpy, trimesh, manifold3d, shapely; print('geometry stack ok')"
else
    PY=""
    for cand in python3 python; do
        if command -v "$cand" >/dev/null 2>&1; then PY=$cand; break; fi
    done
    if [ -z "$PY" ]; then
        echo "error: neither uv nor Python found; install uv (https://docs.astral.sh/uv/) and re-run" >&2
        exit 1
    fi
    echo "uv not found: falling back to a pip venv"
    "$PY" "$PIPELINE" setup
fi

echo "== done. Try: uv run pipeline materials"
