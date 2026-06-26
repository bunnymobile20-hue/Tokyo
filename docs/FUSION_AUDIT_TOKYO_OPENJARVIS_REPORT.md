# FUSION AUDIT REPORT: TOKYOOS & OPENJARVIS

This report documents the structural, technical, and architectural details of both the **TokyoOS** and **OpenJarvis** repositories before their unified fusion.

---

## 1. TokyoOS Audit

* **Repository Location**: `/Users/dalilabarreto/.gemini/antigravity/scratch/Tokyo`
* **Port**: `8788` (Default)
* **Frontend**: Vanilla HTML/JS with glassmorphic dark-theme UI. Single entry page: `interface/index.html`.
* **Backend**: FastAPI app (`app.py`), orchestrating custom modules.

### Directory Structure & Modules
* `app.py`: Main entry point, mounts routes, manages configurations, serves frontend static UI.
* `tokyo_orchestrator/`: Router that uses Ollama and Qwen to translate user input into tool executions.
* `tokyo_security/`: Manages API keys and SafetyGate configuration.
* `tokyo_plugins/hermes_bridge/`: Core integration layer. Contains `audit.py` (SafetyGate command filtering) and `hermes_shim.py` (command execution adapter).
* `tokyo_voice_agent/`: Python LiveKit Agent framework using Gemini Realtime for native audio streaming.
* `finance_engine/`: Business logic calculations for cash flow, DRE, and break-even.
* `siberian_connector/`: Gateway connecting to the external Siberian ERP system.

### Configuration & Docker
* **Runtime**: Python 3.11-slim
* **Compose File**: Deploys `tokyoos` container, maps `/DATA/AppData/tokyoos` volume for workspace persistence, and injects API credentials.
* **SafetyGate**: Validates command execution safety (e.g. intercepts `rm -rf`, `sudo`, and unconfirmed edits to database/assets).

---

## 2. OpenJarvis Audit

* **Repository Location**: `/Users/dalilabarreto/.gemini/antigravity/scratch/OpenJarvis`
* **Main Tech**: Highly modular python architecture + Rust compilation bridge (`openjarvis_rust`).
* **Frontend**: React SPA (which will be discarded in favor of Tokyo's UI).

### Key Modules
* `src/openjarvis/agents/`: Advanced multi-agent orchestrator framework.
* `src/openjarvis/memory/`: Multi-tiered memory layers (Local filesystem, BM25 text indexer, FAISS vector embeddings, PDF parsing).
* `src/openjarvis/skills/` & `tools/`: Dynamic loading of YAML-based skills and python tool bindings.
* `src/openjarvis/server/`: FastAPI server and API endpoints (`/v1/agents`, `/v1/memory`, etc.).
* `rust/`: Cargo workspace for compilation of high-performance security modules and python wrappers.

### Incompatible / To Be Discarded Modules
* `frontend/`: The React web app will be completely excluded.
* `desktop/`: Tauri-based wrapper and desktop binaries will be discarded.
* `media/` (partially): Video/image generation tools that are out of scope for this text-voice agent.

---

## 3. Duplicate Modules & Dependencies

| Area | TokyoOS Implementation | OpenJarvis Implementation | Fusion Strategy |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | FastAPI 0.100.0 | FastAPI 0.110+ | Standardize on FastAPI 0.110+ |
| **Python Version** | Python 3.11 | Python 3.12 | Standardize on Python 3.12 |
| **Memory Backend** | Local FS + Mem0 Cloud | Local FS + BM25 + FAISS | Retain both. Wrap Mem0 and BM25 inside `tokyo_agent_core/memory.py` |
| **Security/Audit** | Python-based `SafetyGate` | Rust-compiled scanners | Use Tokyo's `SafetyGate` as the primary firewall, using OpenJarvis Rust scanners as secondary validation |
| **API Endpoints** | `/tokyo/*` | `/v1/*` | Retain `/tokyo/*` and register OpenJarvis APIs under `/tokyo/agent-core/*` |

---

## 4. Key Security & Implementation Risks

1. **Rust Toolchain Overhead**:
   * *Risk*: Host OS (macOS) does not have cargo/rustc installed. 
   * *Mitigation*: The Rust module `openjarvis_rust` will only be compiled during the Docker multi-stage build. Maturin and cargo will not be required on the developer's local machine for basic runs if mock/python fallback is active.
2. **Settings Collision**:
   * *Risk*: Both projects load environment variables from `.env`.
   * *Mitigation*: Unify all settings under `/config/` and prefix all new OpenJarvis variables with `TOKYO_` to avoid conflicts.
3. **SafetyGate Integrity**:
   * *Risk*: The new modular agent core could execute tools bypassing the SafetyGate.
   * *Mitigation*: Wrap all tool call executions by the OpenJarvis agent core with a mandatory check against `SafetyGate.evaluate()`.

---

## 5. Fusion Roadmap

1. **Phase 1**: Audit report (This file).
2. **Phase 2**: Pre-merge fixes in both codebases.
3. **Phase 3**: Unified architecture definition (`FUSION_TARGET_ARCHITECTURE.md`).
4. **Phase 4**: Backend integration (Copying OpenJarvis modules under `tokyo_agent_core` and exposing unified FastAPI endpoints).
5. **Phase 5**: UI Expansion (Adding panels to `index.html` for Agent Core, CFO, COO, Doctor).
6. **Phase 6**: Docker & ZimaOS packaging (Multi-stage Dockerfile + unified compose).
7. **Phase 7**: Automated testing and validation of the CFO mandatory flow.
