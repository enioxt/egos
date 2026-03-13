#!/bin/sh
set -e

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

echo "🧬 EGOS Init"
echo "=============="

if command -v bun >/dev/null 2>&1; then
  echo "✅ Bun detected"
elif command -v npm >/dev/null 2>&1; then
  echo "⚠️ Bun not found. Installing..."
  npm install -g bun@latest >/dev/null 2>&1 || curl -fsSL https://bun.sh/install | bash
else
  echo "❌ Neither bun nor npm found. Please install Node.js first."
  exit 1
fi

PATH="$HOME/.bun/bin:$PATH"
export PATH

cd "$ROOT"
bun install --frozen-lockfile 2>/dev/null || bun install

if [ ! -f "$ROOT/.env" ] && [ -f "$ROOT/.env.example" ]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "📝 Created .env from .env.example"
fi

if [ ! -e "$ROOT/.egos" ] && [ -d "$HOME/.egos" ]; then
  ln -sf "$HOME/.egos" "$ROOT/.egos"
  echo "🔗 Linked .egos -> $HOME/.egos"
fi

if [ -f "$ROOT/scripts/governance-sync.sh" ]; then
  printf 'n\n' | EGOS_KERNEL="$ROOT" sh "$ROOT/scripts/governance-sync.sh" --exec || true
fi

bun run agent:lint 2>/dev/null || true
bun run agent:list 2>/dev/null || true

echo ""
echo "✅ EGOS ready"
echo ""
echo "Next:"
echo "  bun typecheck"
echo "  bun governance:check"
echo "  bun agent:list"
