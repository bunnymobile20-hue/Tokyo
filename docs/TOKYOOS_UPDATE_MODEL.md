# TokyoOS Update Model

## Current Version

**1.0.0-phase1** — Professional Core

## Update Philosophy

TokyoOS is designed for in-place upgrades that preserve user data.

## Data Preservation

All user data is stored in mounted Docker volumes:
- `/data/tokyo/memory/` — Conversation memory
- `/data/tokyo/intelligence/` — Documents and files
- `/data/tokyo/logs/` — System logs

During upgrades, the Docker container is replaced but the volume persists.

## Upgrade Process (Planned)

1. Pull new image
2. Stop current container
3. Start new container with same volume mount
4. Run migration scripts (if any)
5. Verify healthcheck

## Phase Roadmap

### Phase 1: Professional Core (CURRENT)
- Setup Wizard
- Tokyo Doctor
- API Hub
- Plugin/Connector registry
- MCP optional model
- LLM Gateway
- GrupsBunny Dashboard
- Financial models (placeholders)
- Docker/ZimaOS preparation

### Phase 2: Real Integrations (PLANNED)
- Connect Sistema Siberian API (read-only)
- Enable financial calculations
- LLM Gateway routing
- Spreadsheet upload/parsing
- Real financial data display

### Phase 3: Advanced Features (PLANNED)
- Multi-agent network
- macOS agent
- Full write operations
- Advanced analytics
- External integrations activation

## API Versioning

All TokyoOS APIs are prefixed with `/tokyo/` for clear namespace separation.

Future API versions will use:
- `/tokyo/v1/` — Current
- `/tokyo/v2/` — Breaking changes

Current Phase 1 endpoints are unversioned for simplicity.

## Backward Compatibility

- Voice agent (agent.py) is preserved across all phases
- Config JSON files maintain backward-compatible schemas
- Environment variable names do not change
- Volume mount paths do not change
