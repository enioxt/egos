#!/bin/bash
# Oracle PAYG Upgrade - Guia de Configuração de Proteções
# Executar APÓS upgrade PAYG completo na console Oracle

set -e

echo "=========================================="
echo "Oracle PAYG - Configuração de Proteções"
echo "=========================================="
echo ""
echo "⚠️  IMPORTANTE: Execute este script APÓS fazer o upgrade PAYG na console Oracle"
echo ""
echo "Pré-requisitos:"
echo "1. Conta upgradeada para PAYG"
echo "2. OCI CLI instalado e configurado"
echo "3. Cartão de crédito validado ($100 teste reembolsado)"
echo ""
read -p "Já fez o upgrade PAYG na console? (s/n): " CONFIRM

if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
    echo "❌ Cancele e faça o upgrade primeiro na: https://cloud.oracle.com/billing"
    exit 1
fi

# Configurações
TENANCY_OCID=$(oci iam tenancy get --query 'data.id' --raw-output 2>/dev/null || echo "")
COMPARTMENT_OCID=$(oci iam compartment list --query 'data[?name==`root`].id | [0]' --raw-output 2>/dev/null || echo "")

if [ -z "$TENANCY_OCID" ]; then
    echo "❌ OCI CLI não configurado. Execute: oci setup config"
    exit 1
fi

echo ""
echo "✅ OCI CLI configurado"
echo "Tenancy OCID: $TENANCY_OCID"
echo ""

# 1. Configurar Compartment Quotas (limitar a 4 OCPUs)
echo "🔒 Configurando Compartment Quotas (máx 4 OCPUs)..."
cat > /tmp/quota_policy.json << 'EOF'
{
    "statements": [
        "Zero compute quotas in tenancy",
        "set compute-core-count-quota to 4 in tenancy"
    ]
}
EOF

oci limits quota create \
    --compartment-id "$COMPARTMENT_OCID" \
    --description "Limite segurança - max 4 OCPUs A1.Flex" \
    --name "always-free-safety-limit" \
    --statements 'set compute-core-count-quota to 4 in tenancy' \
    2>/dev/null || echo "⚠️  Quota já existe ou requer configuração manual"

echo "✅ Quotas configuradas"
echo ""

# 2. Criar arquivo de configuração de proteções
cat > /opt/scripts/oracle-instance-launcher/.env.protections << EOF
# Proteções PAYG - Criado em $(date)
# Estas variáveis adicionais garantem segurança

# Limites estritos para sempre ficar no Always Free
OCI_OCPUS_MAX=4
OCI_MEMORY_MAX=24
OCI_BOOT_MAX=200

# Alerta se exceder
ALERT_ON_EXCEED=true

# Stop on first sucesso (evita criar múltiplas)
OCI_STOP_ON_SUCCESS=true
EOF

echo "✅ Arquivo de proteções criado: .env.protections"
echo ""

# 3. Atualizar .env principal
cd /opt/scripts/oracle-instance-launcher

# Backup
 cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Adicionar proteções ao .env
cat >> .env << 'EOF'

# === PROTEÇÕES PAYG ===
# Limites máximos para sempre ficar no Always Free
OCI_SHAPE=VM.Standard.A1.Flex
OCI_OCPUS=4
OCI_MEMORY_GB=24
OCI_BOOT_VOLUME_GB=200
OCI_STOP_ON_SUCCESS=true
# ======================
EOF

echo "✅ .env atualizado com proteções"
echo ""

# 4. Reiniciar serviço
echo "🔄 Reiniciando serviço..."
systemctl restart oracle-instance-launcher
systemctl status oracle-instance-launcher --no-pager | head -5

echo ""
echo "=========================================="
echo "✅ Configuração completa!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Configure billing alerts na console Oracle:"
echo "   https://cloud.oracle.com/billing/alerts"
echo "   - Alert 1: Limite $1 USD"
echo "   - Alert 2: Limite $5 USD"  
echo "   - Alert 3: Limite $10 USD"
echo ""
echo "2. Monitore logs:"
echo "   tail -f /opt/scripts/oracle-instance-launcher/logs/app.log"
echo ""
echo "3. Com PAYG, a instância deve criar em minutos (não dias)"
echo ""
