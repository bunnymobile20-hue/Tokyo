# TokyoOS MCP Optional Model

## Status

MCP (Model Context Protocol) is treated as an **optional connector** in TokyoOS.

## Configuration

```env
MCP_ENABLED=false
MCP_BASE_URL=
MCP_API_KEY=
MCP_MODE=optional
MCP_SAFE_MODE=true
```

## MCP in TokyoOS

- **required**: false
- **status**: not_configured
- **mode**: optional
- **default_port**: 8789
- **Not core** of TokyoOS

## Purpose

MCP will be used in the future as an optional tool connector for external MCP servers. It provides tools, context, and server communication.

## Current Phase

Phase 1 only sets up the registry entry and configuration schema. No MCP server is installed or connected.

## Connection

When enabled, MCP connects via:
- `MCP_BASE_URL` — MCP server endpoint
- `MCP_API_KEY` — Authentication key (optional)

MCP failure does not affect TokyoOS operation.
