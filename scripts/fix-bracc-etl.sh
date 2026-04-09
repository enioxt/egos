#!/bin/bash
# Fix BR-ACC ETL Service (EGOS-2026-04-09)
# Execute no VPS: bash fix-bracc-etl.sh

set -e

echo "=== BR-ACC ETL Fix Script ==="
echo "Data: 2026-04-09"
echo ""

# 1. Create .env if missing
if [ ! -f /opt/bracc/etl/.env ]; then
    echo "[1/5] Criando .env..."
    cat > /opt/bracc/etl/.env << 'ENVFILE'
NEO4J_DATABASE=neo4j
NEO4J_PASSWORD=bracc-etl-password-2024
GUARD_BRASIL_API_KEY=
RECEITA_FEDERAL_TOKEN=
ENVFILE
    chmod 600 /opt/bracc/etl/.env
    echo "✓ .env criado"
else
    echo "[1/5] .env já existe"
    # Ensure NEO4J_PASSWORD is set
    if ! grep -q 'NEO4J_PASSWORD' /opt/bracc/etl/.env; then
        echo "NEO4J_PASSWORD=bracc-etl-password-2024" >> /opt/bracc/etl/.env
        echo "✓ NEO4J_PASSWORD adicionado"
    fi
fi

# 2. Check service file function name
echo "[2/5] Verificando função no serviço..."
if grep -q 'run_etl' /etc/systemd/system/bracc-etl.service 2>/dev/null; then
    echo "⚠ Service usa 'run_etl' - código pode estar desatualizado"
    echo "  Função atual no código: run_all()"
    echo "  Corrigir: sed -i 's/run_etl/run_all/' /etc/systemd/system/bracc-etl.service"
fi

# 3. Fix service file to use correct Python path and add password
echo "[3/5] Atualizando serviço systemd..."
cat > /etc/systemd/system/bracc-etl.service << 'SERVICEFILE'
[Unit]
Description=BR-ACC ETL Pipeline — CNPJ Phase 3
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=/opt/bracc/etl
Environment=PYTHONPATH=/opt/bracc/etl/src
Environment=NEO4J_URI=bolt://bracc-neo4j:7687
EnvironmentFile=/opt/bracc/etl/.env
ExecStart=/opt/bracc/etl/.venv/bin/python -c "from bracc_etl.runner import run_all; run_all('cnpj', start_phase=3)"
User=root
StandardOutput=append:/var/log/bracc-etl.log
StandardError=append:/var/log/bracc-etl.log

[Install]
WantedBy=multi-user.target
SERVICEFILE

echo "✓ Service file atualizado"

# 4. Reload systemd
echo "[4/5] Recarregando systemd..."
systemctl daemon-reload

# 5. Test run
echo "[5/5] Testando execução manual..."
cd /opt/bracc/etl
if .venv/bin/python -c "from bracc_etl.runner import run_all; print('✓ Import OK')" 2>&1; then
    echo "✓ Python import funciona"
else
    echo "✗ Python import falhou - verificar código fonte"
    exit 1
fi

echo ""
echo "=== Diagnóstico Completo ==="
echo "Para iniciar o serviço: systemctl start bracc-etl.service"
echo "Para ver logs: journalctl -u bracc-etl.service -f"
echo "Para status: systemctl status bracc-etl.service"
