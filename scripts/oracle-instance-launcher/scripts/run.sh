#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
VENV="$ROOT/.venv"

if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
fi

# shellcheck disable=SC1091
. "$VENV/bin/activate"
if ! python -c "import oci, dotenv" >/dev/null 2>&1; then
  pip install -r "$ROOT/requirements.txt" >/dev/null
fi
mkdir -p "$ROOT/logs"
cd "$ROOT"
exec python -m src.main "$@"
