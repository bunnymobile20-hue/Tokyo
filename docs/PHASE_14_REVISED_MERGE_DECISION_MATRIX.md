# MATRIZ DE DECISÃO DA FUSÃO TOKYOOS + OPENJARVIS

A seguinte matriz determina o que acontece com cada módulo para garantir a filosofia **TokyoOS Principal, OpenJarvis como Base**.

| Componente/Módulo | Origem Original | Decisão | Justificativa e Ação |
| :--- | :--- | :--- | :--- |
| `app.py` | TokyoOS | **KEEP_TOKYO** | Mantém a porta 8788, rotas customizadas de saúde e a identidade do projeto. |
| `frontend/` | TokyoOS (Portado do OpenJarvis) | **KEEP_TOKYO** | Já foi ajustado para o visual GrupsBunny, cores Tokyo e a arquitetura React Router (`/ui`). |
| `siberian_connector/` | TokyoOS | **KEEP_TOKYO** | É a integração proprietária e segura do ERP. Não existe no OpenJarvis. |
| `finance_engine/` | TokyoOS | **KEEP_TOKYO** | O cérebro financeiro dos Agentes CFO (Bunny). Não tem equivalência no OpenJarvis. |
| `tokyo_voice_agent/` | TokyoOS | **KEEP_TOKYO** | LiveKit integration exclusiva para a voz real-time da Tokyo. |
| `tokyo_security/` (SafetyGate) | TokyoOS | **KEEP_TOKYO** | Módulo de barreira (Zero Mock Gate). É a autoridade final de permissões e segurança. |
| `tokyo_agent_core/` | Ambos (Transição) | **IMPORT_OPENJARVIS** | O runtime, memórias, e skills do OpenJarvis devem substituir o core cru que estava aqui, mantendo a pasta `tokyo_agent_core/` para não quebrar referências, e copiando `src/openjarvis/` do OpenJarvis oficial. |
| `tokyo_openjarvis_bridge/` | Novo | **WRAP_OPENJARVIS_WITH_TOKYO_BRIDGE** | Nova camada que fará a tradução entre as requisições nativas da Tokyo e o core interno importado do OpenJarvis, gerenciando saúde, status, e invocação. |
| `config/.env` | TokyoOS | **ADAPT_OPENJARVIS_TO_TOKYO** | Manter a proteção de segredos da TokyoOS, mas incluir variáveis de memória/provedores que o OpenJarvis espera (Ollama, Mem0, etc). |
| `docker-compose.yml` e `Dockerfile` | TokyoOS | **KEEP_TOKYO** | O modelo de deploy no ZimaOS é robusto, o mapeamento do `/DATA/AppData/tokyoos` não pode ser removido, nem as dependências `maturin/rust` cruciais. |

## Regra Fundamental: ZERO MOCK GATE
Nenhum módulo importado do OpenJarvis tem permissão de usar dados fictícios (Mock Data) fingindo ser real no sistema financeiro ou de estoque (Siberian). Qualquer request que use o core do OpenJarvis para obter dados de negócios deverá passar pelo `tokyo_openjarvis_bridge/` e pelo `tokyo_security/`, atestando a validade dos dados ou sinalizando explicitamente: `MOCK DATA ACTIVE` / `DATA_SOURCE_NOT_REAL`.
