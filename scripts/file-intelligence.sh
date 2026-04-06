#!/bin/bash
# EGOS File Intelligence — Pre-commit classification & compliance check
# Analyzes all staged files for type, standards compliance, PII leaks,
# and report format adherence. Points to relevant SSOT on violations.
#
# Usage: bash scripts/file-intelligence.sh
# Called from .husky/pre-commit as step [5.5]

set -eu

STAGED=$(git diff --cached --name-only 2>/dev/null || true)
if [ -z "$STAGED" ]; then
  echo "📋 File Intelligence: No staged files"
  exit 0
fi

WARNINGS=0
ERRORS=0

# ── Helper: point user to relevant SSOT ──────────────────────────────────

point_to_ssot() {
  local surface="$1"
  local path="$2"
  echo "   📖 Reference: $surface → $path"
}

# ── 1. Classify staged files ─────────────────────────────────────────────

echo "📋 EGOS File Intelligence v1.0"

REPORTS=""
DOCS=""
CONFIGS=""
CODE_TS=""
CODE_PY=""
DATA=""
TESTS=""
UNKNOWN=""

while IFS= read -r file; do
  [ -z "$file" ] && continue

  case "$file" in
    docs/reports/*|docs/knowledge/*REPORT*.md|**/REPORT*.md)
      REPORTS="$REPORTS $file"
      ;;
    docs/*|*.md|*.txt)
      DOCS="$DOCS $file"
      ;;
    *.json|*.yaml|*.yml|*.toml|.env*|Dockerfile*|docker-compose*|Caddyfile)
      CONFIGS="$CONFIGS $file"
      ;;
    *.ts|*.tsx|*.js|*.jsx)
      CODE_TS="$CODE_TS $file"
      ;;
    *.py)
      CODE_PY="$CODE_PY $file"
      ;;
    *.csv|*.parquet|*.jsonl|*.sql)
      DATA="$DATA $file"
      ;;
    *test*|*spec*|*__tests__*)
      TESTS="$TESTS $file"
      ;;
    *)
      UNKNOWN="$UNKNOWN $file"
      ;;
  esac
done <<< "$STAGED"

# Count files per category
count() { echo "$1" | wc -w | tr -d ' '; }

echo "  Classification:"
[ -n "$REPORTS" ] && echo "    Reports:  $(count "$REPORTS") file(s)"
[ -n "$DOCS" ]    && echo "    Docs:     $(count "$DOCS") file(s)"
[ -n "$CONFIGS" ] && echo "    Configs:  $(count "$CONFIGS") file(s)"
[ -n "$CODE_TS" ] && echo "    TS/JS:    $(count "$CODE_TS") file(s)"
[ -n "$CODE_PY" ] && echo "    Python:   $(count "$CODE_PY") file(s)"
[ -n "$DATA" ]    && echo "    Data:     $(count "$DATA") file(s)"
[ -n "$TESTS" ]   && echo "    Tests:    $(count "$TESTS") file(s)"
[ -n "$UNKNOWN" ] && echo "    Other:    $(count "$UNKNOWN") file(s)"

# ── 2. Report compliance check (REPORT_SSOT.md) ─────────────────────────

if [ -n "$REPORTS" ]; then
  echo ""
  echo "  📊 Report Compliance Check (REPORT_SSOT v2.0.0):"

  for report in $REPORTS; do
    [ ! -f "$report" ] && continue

    echo "    Checking: $report"

    # Check mandatory sections
    MISSING_SECTIONS=""
    for section in "Sumário\|Summary\|Resumo" "Fontes\|Sources\|Metodologia\|Methodology" "Lacunas\|Gaps"; do
      if ! grep -qiE "$section" "$report" 2>/dev/null; then
        MISSING_SECTIONS="$MISSING_SECTIONS $(echo "$section" | sed 's/\\|/, /g')"
      fi
    done

    if [ -n "$MISSING_SECTIONS" ]; then
      echo "    ⚠️  Missing required sections:$MISSING_SECTIONS"
      point_to_ssot "REPORT_SSOT" "docs/REPORT_SSOT.md"
      WARNINGS=$((WARNINGS + 1))
    fi

    # Check confidence markers
    if ! grep -qiE "alta|média|media|baixa|high|medium|low|confiança|confidence" "$report" 2>/dev/null; then
      echo "    ⚠️  No confidence markers found (required: alta/média/baixa)"
      point_to_ssot "REPORT_SSOT" "docs/REPORT_SSOT.md §Princípios"
      WARNINGS=$((WARNINGS + 1))
    fi

    # Check source citations
    if ! grep -qiE "fonte:|source:|url:|https?://" "$report" 2>/dev/null; then
      echo "    ⚠️  No source citations found (required: Fonte + URL + data de consulta)"
      point_to_ssot "REPORT_SSOT" "docs/REPORT_SSOT.md §CITAR FONTE"
      WARNINGS=$((WARNINGS + 1))
    fi

    # Check for unmasked PII patterns
    if grep -qP '\b\d{3}[.\s-]?\d{3}[.\s-]?\d{3}[.\s/-]?\d{2}\b' "$report" 2>/dev/null; then
      echo "    ❌ POTENTIAL CPF FOUND — must be masked per LGPD"
      point_to_ssot "Guard Brasil" "packages/guard-brasil/src/pii-patterns.ts"
      ERRORS=$((ERRORS + 1))
    fi

    # Check disclaimer/footer
    if ! grep -qiE "disclaimer|aviso|lgpd|report_ssot|relatório gerado" "$report" 2>/dev/null; then
      echo "    ⚠️  No LGPD disclaimer/footer found"
      point_to_ssot "REPORT_SSOT" "docs/REPORT_SSOT.md §Footer"
      WARNINGS=$((WARNINGS + 1))
    fi
  done
fi

# ── 3. PII scan in docs and markdown ────────────────────────────────────

PII_FILES=""
for docfile in $DOCS $REPORTS; do
  [ -z "$docfile" ] && continue
  [ ! -f "$docfile" ] && continue

  # Check for raw CPF patterns (not already masked as [CPF REMOVIDO])
  cpf_matches=$(grep -oP '(?<!\[CPF REMOVIDO\])\b\d{3}[.]\d{3}[.]\d{3}[-]\d{2}\b' "$docfile" 2>/dev/null || true)
  if [ -n "$cpf_matches" ]; then
    non_demo_cpfs=$(echo "$cpf_matches" | grep -vxE '123\.456\.789-00|000\.000\.000-00|111\.111\.111-11' || true)
    if [ -n "$non_demo_cpfs" ]; then
      PII_FILES="$PII_FILES $docfile"
    fi
  fi

  # Check for raw email patterns in docs
  email_matches=$(grep -oP '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b' "$docfile" 2>/dev/null || true)
  if [ -n "$email_matches" ]; then
    # Exclude package.json / lockfile refs and common false positives
    if ! echo "$docfile" | grep -qE 'package|lock|node_modules'; then
      non_demo_emails=$(echo "$email_matches" | grep -viE '^[^[:space:]]+@(example\.(com|org|net)|egos\.local|[^[:space:]]+\.local)$|^noreply@anthropic\.com$' || true)
      if [ -n "$non_demo_emails" ]; then
        PII_FILES="$PII_FILES $docfile"
      fi
    fi
  fi
done

if [ -n "$PII_FILES" ]; then
  echo ""
  echo "  🔒 PII Scan Results:"
  for pf in $PII_FILES; do
    echo "    ⚠️  Potential PII in: $pf"
  done
  point_to_ssot "Guard Brasil PII Patterns" "packages/guard-brasil/src/pii-patterns.ts"
  point_to_ssot "LGPD Compliance" "docs/REPORT_SSOT.md §Anti-Patterns"
  WARNINGS=$((WARNINGS + 1))
fi

# ── 4. Config file hygiene ───────────────────────────────────────────────

for cfgfile in $CONFIGS; do
  [ -z "$cfgfile" ] && continue
  [ ! -f "$cfgfile" ] && continue

  # Block .env files (should be in .gitignore)
  if echo "$cfgfile" | grep -qE '^\.env'; then
    echo "  ❌ .env file staged: $cfgfile — MUST be in .gitignore"
    ERRORS=$((ERRORS + 1))
  fi

  # Check Docker for restart: always (should use unless-stopped)
  if echo "$cfgfile" | grep -qE 'docker-compose'; then
    if grep -q 'restart: always' "$cfgfile" 2>/dev/null; then
      echo "  ⚠️  docker-compose uses 'restart: always' — prefer 'unless-stopped'"
      point_to_ssot "Docker Rules" ".guarani/PREFERENCES.md §Docker"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi
done

# ── 5. Python file size check (max 400 lines per .windsurfrules) ────────

for pyfile in $CODE_PY; do
  [ -z "$pyfile" ] && continue
  [ ! -f "$pyfile" ] && continue
  lines=$(wc -l < "$pyfile")
  if [ "$lines" -gt 400 ]; then
    echo "  ⚠️  Python file exceeds 400-line limit: $pyfile ($lines lines)"
    point_to_ssot "Code Size Rules" ".guarani/PREFERENCES.md"
    WARNINGS=$((WARNINGS + 1))
  fi
done

# ── 6. TypeScript file size check (max 300 lines per PREFERENCES) ───────

for tsfile in $CODE_TS; do
  [ -z "$tsfile" ] && continue
  [ ! -f "$tsfile" ] && continue
  lines=$(wc -l < "$tsfile")
  if [ "$lines" -gt 500 ]; then
    echo "  ⚠️  TS/JS file exceeds 500-line limit: $tsfile ($lines lines)"
    point_to_ssot "Code Size Rules" ".guarani/PREFERENCES.md"
    WARNINGS=$((WARNINGS + 1))
  fi
done

# ── Summary ──────────────────────────────────────────────────────────────

echo ""
if [ "$ERRORS" -gt 0 ]; then
  echo "  ❌ File Intelligence: $ERRORS error(s), $WARNINGS warning(s)"
  echo "  📖 Rules Index: .guarani/RULES_INDEX.md"
  exit 1
elif [ "$WARNINGS" -gt 0 ]; then
  echo "  ⚠️  File Intelligence: $WARNINGS warning(s) (non-blocking)"
  echo "  📖 Rules Index: .guarani/RULES_INDEX.md"
  exit 0
else
  echo "  ✅ File Intelligence: All staged files compliant"
  exit 0
fi
