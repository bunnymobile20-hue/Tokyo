# INVENTÁRIO DOS REPOSITÓRIOS - TOKYOOS E OPENJARVIS

## TOKYOOS (Repositório Principal)
**Identidade Visual e Proposta**: Sistema Operacional IA local, com interface própria, agentes especializados de negócio ("Bunny") e voz principal, rodando prioritariamente em ZimaOS/Docker na porta 8788.

### Pastas e Módulos Principais
- `app.py`: O coração do backend (FastAPI), contendo as rotas, integração de middlewares e a API principal (`/ui`, `/health`, `/tokyo/doctor`, etc). **Função:** Orquestrador principal.
- `finance_engine/`: Motor financeiro da GrupsBunny (DRE, Cash Flow, Break Even, etc). **Função:** Cálculos de negócio em mock/sandbox ou produção real.
- `siberian_connector/`: Conector do ERP Siberian. **Função:** Acesso read-only seguro ao sistema de vendas, estoque e CRM.
- `tokyo_agent_core/`: Atualmente um rascunho de migração de ferramentas do OpenJarvis, contendo lógica para LLMs, memória, habilidades e agentes.
- `tokyo_security/`: (SafetyGate) Validação de comandos, rotas, e segurança.
- `tokyo_voice_agent/`: Gerenciador do LiveKit Voice Agent.
- `tokyo_plugins/` / `tokyo_mac_bridge/`: Conectores para execução em Mac Mini via SSH e integrações extras (Hermes, etc).
- `frontend/`: (Recém-portado do OpenJarvis) Interface em React customizada para TokyoOS.
- `scripts/`: Scripts de build e deploy focados em ZimaOS (scp, compose, env checks).

### Decisão Preliminar para TokyoOS
- **Devem ser preservados:** `app.py`, `finance_engine/`, `siberian_connector/`, `tokyo_security/`, `tokyo_voice_agent/`, e todos os agentes Bunny. A porta `8788` e o ambiente de deploy.
- **Módulos adaptáveis/duplicados com OpenJarvis:** `tokyo_agent_core/` já parece ser um clone preliminar do OpenJarvis.

## OPENJARVIS (Repositório Base)
**Identidade Visual e Proposta**: Agente desktop/web IA local e conectável (Tauri/Python/Rust) para produtividade diária (chat, arquivos, ferramentas do sistema).

### Pastas e Módulos Principais
- `src/openjarvis/`: O Core do Agent Runtime, Memory Bindings (mem0), Skills (os/browser/code), Workflows.
- `frontend/`: Interface React robusta (rotas, chats, logs, integrações).
- `rust/`: Bibliotecas de performance para manipulação e system hooks.
- `tests/` & `examples/`: Código de verificação e templates de agentes.

### Decisão Preliminar para OpenJarvis
- **Módulos Úteis para Incorporar:** `src/openjarvis/core` (Agent Runtime), sistema de Memory (mem0 e vector local), registro de Skills/Tools, e Workflows.
- **Módulos Base Técnica:** Todo o motor de execução de IA e as ferramentas nativas de OS que ajudarem os agentes "Bunny".
- **Módulos a Evitar (Não sobrescrever TokyoOS):** Interface e branding puros do OpenJarvis (já estão substituídos no `frontend/` da Tokyo), inicialização padrão e porta (não usar as portas do OpenJarvis ou a UI default sem os toques do ZimaOS).
