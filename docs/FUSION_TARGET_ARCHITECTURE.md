# TOKYOOS UNIFIED TARGET ARCHITECTURE

This document describes the unified directory structure and component integration for **TokyoOS** after absorbing OpenJarvis.

---

## 1. Unified Directory Layout

To maintain full backward compatibility and prevent broken imports in existing Tokyo code, we map the target architecture onto Tokyo's directory structure, creating clean namespaces for the newly integrated components.

```text
/Users/dalilabarreto/.gemini/antigravity/scratch/Tokyo/
├── app.py                       # FastAPI application (entry point, port 8788)
├── config/                      # Unified settings schema & JSON configurations
├── tokyo_orchestrator/          # Intent parser & local LLM router
├── tokyo_security/              # API keys and security logic
├── tokyo_plugins/
│   └── hermes_bridge/
│       ├── audit.py             # SafetyGate component (system firewall)
│       └── hermes_shim.py       # Shim service and adapter
├── tokyo_voice_agent/           # LiveKit and Gemini Realtime audio voice loops
├── siberian_connector/          # Siberian ERP interface
├── finance_engine/              # Business logic: DRE, cash flow, cycle calculations
├── interface/                   # HTML/CSS/JS frontend files
│   ├── index.html               # Main single-page application dashboard
│   ├── static/                  # Shared static assets (CSS, images)
│   └── components/              # Modals and subviews
├── tokyo_agent_core/            # Absorbed OpenJarvis Core Engine (Python 3.12)
│   ├── agents/                  # Multi-agent orchestrators
│   ├── skills/                  # YAML and Markdown skill loaders
│   ├── tools/                   # Extensible tool bindings
│   ├── memory/                  # FAISS, BM25, and local file storage memory
│   ├── workflows/               # Composite task orchestration
│   ├── scheduler/               # Scheduled cron jobs
│   └── doctor/                  # Diagnostic health checkers
├── data/                        # Local databases, workspaces, and cached files
├── docs/                        # Specifications, manuals, and audit reports
├── tests/                       # Integrated test suites
└── scripts/                     # Helper verification and build scripts
```

---

## 2. Component Integration Matrix

### A. Request Orchestration Flow
When a user interacts with TokyoOS via text or voice, the request travels through:
1. **Tokyo UI / Voice Gateway** (`interface/` or `tokyo_voice_agent/`)
2. **Tokyo Orchestrator** (`tokyo_orchestrator/router.py`)
3. **SafetyGate Verification** (`tokyo_plugins/hermes_bridge/audit.py`)
4. **Agent Core Execution** (`tokyo_agent_core/agents/` using tools and skills)
5. **Connector / Database Action** (`siberian_connector/` or `finance_engine/`)
6. **Unified Sanitized Response** returned to the user and registered in Jobs.

### B. Security Enforcement (SafetyGate)
All dynamic agents and workflow blocks must pass their generated execution plans through `SafetyGate.evaluate()` before executing any tool or command. Destructive CLI instructions or unauthorized file mutations are blocked.

### C. Unified Doctor API
The endpoint `/tokyo/doctor` is updated to perform checks on:
* **System**: App state, database connections.
* **Voice**: LiveKit socket, Gemini Realtime config.
* **Agent Core**: Availability of `openjarvis_rust`, registered skills.
* **Workspace**: Permissions of `/data/tokyo/workspace`.
