#!/bin/bash
# TokyoOS Healthcheck Script
# Validates core system health

set -e

HOST="${TOKYO_HOST:-localhost}"
PORT="${TOKYO_HTTP_PORT:-8788}"
BASE="http://${HOST}:${PORT}"

echo "=== TokyoOS Healthcheck ==="
echo ""

check_endpoint() {
    local endpoint=$1
    local label=$2
    if curl -sf "${BASE}${endpoint}" > /dev/null 2>&1; then
        echo "[OK] ${label} (${endpoint})"
    else
        echo "[FAIL] ${label} (${endpoint})"
        return 1
    fi
}

# System
check_endpoint "/tokyo/system/health" "System Health"
check_endpoint "/tokyo/setup/status" "Setup Status"
check_endpoint "/tokyo/setup/checklist" "Setup Checklist"
check_endpoint "/tokyo/doctor" "Tokyo Doctor"

# LLM & Providers
check_endpoint "/tokyo/llm/status" "LLM Status"
check_endpoint "/tokyo/providers/registry" "Providers Registry"
check_endpoint "/tokyo/providers/status" "Providers Status"

# Integrations & Connectors
check_endpoint "/tokyo/integrations/registry" "Integrations Registry"
check_endpoint "/tokyo/integrations/status" "Integrations Status"
check_endpoint "/tokyo/connectors/registry" "Connectors Registry"
check_endpoint "/tokyo/plugins/registry" "Plugins Registry"
check_endpoint "/tokyo/api-hub/status" "API Hub Status"

# Optional
check_endpoint "/tokyo/mcp/status" "MCP Status"

# Memory & Voice
check_endpoint "/tokyo/memory/status" "Memory Status"
check_endpoint "/tokyo/voice/status" "Voice Status"

# Security
check_endpoint "/tokyo/security/status" "Security Status"

# Business
check_endpoint "/tokyo/business/status" "Business Status"
check_endpoint "/tokyo/grupsbunny/status" "GrupsBunny Status"
check_endpoint "/tokyo/bunnydreams/status" "Bunny Dreams Status"
check_endpoint "/tokyo/bunnysiberian/status" "Bunny Siberian Status"
check_endpoint "/tokyo/siberian/status" "Siberian Status"

# Finance
check_endpoint "/tokyo/finance/status" "Finance Status"
check_endpoint "/tokyo/finance/models" "Finance Models"
check_endpoint "/tokyo/finance/references" "Finance References"

echo ""
echo "=== Healthcheck Complete ==="
