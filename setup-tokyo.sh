#!/bin/bash
# ============================================================================
# TokyoOS Agent Setup Script (ZimaOS / Docker)
# ============================================================================
# Quick setup for developers and GrupsBunny environments.
#
# This script:
# 1. Detects Docker & docker-compose
# 2. Creates necessary AppData directories for ZimaOS
# 3. Sets up the .env from template
# 4. Builds and runs the Docker containers
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo -e "${CYAN}⚕ TokyoOS Agent Setup (ZimaOS Mode)${NC}"
echo ""

# ============================================================================
# Check Docker Requirements
# ============================================================================
echo -e "${CYAN}→${NC} Checking Docker..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗${NC} Docker not found. Please install Docker."
    exit 1
fi

DOCKER_COMPOSE_CMD=""
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    echo -e "${RED}✗${NC} Docker Compose not found. Please install Docker Compose."
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker and Docker Compose found"

# ============================================================================
# Environment file
# ============================================================================
echo -e "${CYAN}→${NC} Checking .env file..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        chmod 600 .env 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Created .env from template"
    else
        echo -e "${YELLOW}⚠${NC} .env.example not found. You must create a .env file manually."
    fi
else
    chmod 600 .env 2>/dev/null || true
    echo -e "${GREEN}✓${NC} .env exists"
fi

# ============================================================================
# Host Volume Setup (ZimaOS specific path /DATA/AppData/tokyoos)
# ============================================================================
echo -e "${CYAN}→${NC} Setting up Host Volumes..."
HOST_DATA_PATH="/DATA/AppData/tokyoos"

if [ -w "/DATA" ] || [ "$(id -u)" = "0" ]; then
    mkdir -p "$HOST_DATA_PATH/memory/local"
    mkdir -p "$HOST_DATA_PATH/memory/obsidian"
    mkdir -p "$HOST_DATA_PATH/intelligence"
    mkdir -p "$HOST_DATA_PATH/logs"
    echo -e "${GREEN}✓${NC} Host directories created at $HOST_DATA_PATH"
else
    echo -e "${YELLOW}⚠${NC} Cannot write to /DATA. Ensure the directory exists or run with sudo if deploying to CasaOS/ZimaOS native paths."
    echo "  Local docker volumes will be used if paths are inaccessible."
fi

# ============================================================================
# Build and Run
# ============================================================================
echo -e "${CYAN}→${NC} Starting TokyoOS Services..."

# Workaround for ZimaOS read-only /root/.docker
HOME=/tmp $DOCKER_COMPOSE_CMD up -d --build --force-recreate

echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Access the Interface at: http://localhost:8788/ui"
echo "  2. Go to 'Voz' tab and click 'Iniciar Sessão'."
echo "  3. The Voice Agent should automatically respond, no manual backend dispatch needed."
echo ""
echo "Logs:"
echo "  $DOCKER_COMPOSE_CMD logs -f"
echo ""
