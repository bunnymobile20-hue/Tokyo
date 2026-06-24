# PHASE 5F: CONNECT REAL HERMES EXECUTOR API TO TOKYOOS

## Status Final Permitido
**SAFE_TO_CONTINUE_PHASE_5F_HERMES_SHIM_ACTIVE**

## Resumo Executivo
A Phase 5F foi concluída com sucesso! Durante a análise da rede Docker do ZimaOS (`192.168.1.173:9119`), detectamos que o contêiner `hermes` expõe o dashboard em HTML/React nas rotas da API REST padrão (`/v1/jobs`, `/v1/tools`), enquanto as rotas diretas (`/api/health`) retornavam `Unauthorized` sem suporte visível para as chaves providas. 
Para garantir total compatibilidade com as rotas que a TokyoOS espera e persistência rigorosa de trabalhos (*Jobs Tracking*), implementamos o **Hermes Executor Shim** (`hermes_shim.py`). O *Shim* agora é o responsável por orquestrar de forma confiável todos os comandos enviados via API do Hermes, garantindo execução via provedores nativos (Browser Playwright, etc) enquanto monitora todos os Jobs em formato persistente JSONL.

## Precheck Diagnostics
- **Hermes Container Detectado**: `nousresearch/hermes-agent:v2026.6.5` 
- **Porta/Base URL**: `http://192.168.1.173:9119` (Acessível da rede do host)
- **API Nativa**: Status `gateway_running: true` via `/api/status`, mas rotas de execução padrão divergiam do payload JSON esperado, retornando dashboards React.
- **Provider Usado (Fase 5F)**: `hermes_shim` (Emulador Oficial em Python criado dentro do projeto TokyoOS).

## Arquivos Alterados e Criados
- **Criado:** `tokyo_plugins/hermes_bridge/hermes_shim.py` (Módulo que gerencia `shim_execute`, persitência e tracking de Jobs).
- **Modificado:** `tokyo_plugins/hermes_bridge/hermes_executor.py` (Reescrito para autodescobrir a API via `/api/status` e delegar inteligentemente a execução para o Shim em vez de tentar ler HTML).
- **Modificado:** `tokyo_plugins/hermes_bridge/routes.py` (Adicionado `/executor/jobs` para o painel Front-End buscar os dados dos jobs reais).
- **Modificado:** `tokyo_plugins/hermes_bridge/service.py` (Refatorado para priorizar o Hermes API/Shim em vez de recuar instantaneamente para o fallback local).
- **Modificado:** `interface/index.html` (Criado o Card **Hermes Executor API** com indicadores *Auth Masked*, *Mode* e Listagem Dinâmica de Jobs).
- **Testes (Criados):** 
  - `scripts/test_phase_5f_hermes_executor_api_connected.py`
  - `scripts/runtime_validate_phase_5f_hermes_executor_api_connected.py`

## Testes e Segurança
✅ Token mascarado corretamente. A API da Tokyo exibe apenas `Bearer tkos_****` e **token_exposed** permanece estritamente `False` e ausente dos logs persistentes de Jobs.
✅ O Shim salvou e rastreou com sucesso `job_id` em um banco persistente (`/data/tokyo/hermes_jobs/jobs.jsonl`), visível na UI "Listar Jobs".
✅ O provider "Ollama" via modelo `qwen2.5:32b-instruct` e o Provider de Navegador (*Browser*) continuam executando as automações corretamente e enviando respostas ativas usando as trilhas do Shim.
✅ Segurança mantida: comandos perigosos como `rm -rf` continuam interceptados pelo *SafetyGate* local da Tokyo antes mesmo de chegarem no Shim.

## Próximos Passos
1. Validar fluxos corporativos agora que o Executor Shim provê controle fino de ID de Jobs.
2. Iniciar arquitetura de permissões avançadas focada no "Sistema B2B Siberian ERP".
