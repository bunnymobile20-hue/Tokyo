#!/bin/bash
# TokyoOS - Mac Bridge SSH Setup
# Gera a chave ed25519 e exporta para o Mac Mini

set -e

# Define data directory from environment or fallback to /DATA/AppData/tokyoos
DATA_DIR="${TOKYO_DATA_DIR:-/DATA/AppData/tokyoos}"
SECURITY_DIR="$DATA_DIR/security/mac_bridge"
KEY_FILE="$SECURITY_DIR/id_ed25519"

echo "========================================="
echo " TokyoOS - Configuração Segura de Mac SSH"
echo "========================================="

# 1. Configurar o diretório e gerar chave se não existir
mkdir -p "$SECURITY_DIR"

if [ ! -f "$KEY_FILE" ]; then
    echo ">> Gerando chave criptográfica isolada para o ZimaOS..."
    # -N "" significa sem passphrase (senha) para permitir automação
    ssh-keygen -t ed25519 -f "$KEY_FILE" -N "" -q
    echo "Chave SSH Ed25519 criada com sucesso em $KEY_FILE."
else
    echo ">> Chave SSH Ed25519 já existe em $KEY_FILE. Pulando criação."
fi

# 2. Obter informações de conexão do Mac
echo ""
read -p "Digite o IP do Mac Mini (Tailscale ou LAN): " MAC_IP
if [ -z "$MAC_IP" ]; then
    echo "Erro: IP é obrigatório."
    exit 1
fi

read -p "Digite o Nome de Usuário do Mac (ex: user, admin, grupsbunny): " MAC_USER
if [ -z "$MAC_USER" ]; then
    echo "Erro: Usuário é obrigatório."
    exit 1
fi

echo ""
echo "Enviando chave pública para $MAC_USER@$MAC_IP..."
echo "Aviso: Você será solicitado a digitar a SENHA DO MAC agora. Esta é a ÚNICA vez."

# 3. Exportar chave usando ssh-copy-id e forçando o uso de um arquivo de identidade customizado
ssh-copy-id -i "${KEY_FILE}.pub" -o StrictHostKeyChecking=no "$MAC_USER@$MAC_IP"

echo ""
echo "Testando conexão..."
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no "$MAC_USER@$MAC_IP" "echo 'MAC_BRIDGE_OK'"

echo "========================================="
echo " SUCESSO!"
echo " A chave foi ativada. Atualize o arquivo config/tokyo_mac_bridge.json com:"
echo " \"mac_host\": \"$MAC_IP\""
echo " \"mac_user\": \"$MAC_USER\""
echo "========================================="
