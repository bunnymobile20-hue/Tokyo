# CHECKPOINT PRÉ-FUSÃO (PHASE 14 REVISED)

**Data e Hora**: 2026-06-26 11:11:00-03:00  
**Status**: INVENTORY AND PLANNING COMPLETE  
**Sistema Alvo**: TokyoOS (ZimaOS / Docker na porta 8788)  

## Estrutura Atual (Antes da Fusão Core)
- `app.py`: Controlando rotas principais com endpoints de status básicos (fake/mocks).
- `tokyo_agent_core/`: Pasta presente na TokyoOS, originada de migrações passadas, que deverá receber o código fonte robusto do repositório OpenJarvis, mas de forma empacotada.
- `siberian_connector/` & `finance_engine/`: Módulos de negócios estáveis e operantes em modo Safe (Mock).
- `frontend/`: Build frontend Vite/React da interface operando localmente sob a pasta `src/openjarvis/server/static`.
- Docker/ZimaOS deploy funcional (A compilação via `scp` funcionou na Phase 13/14).

## Arquivos Críticos para Backup Constante
- `app.py`
- `docker-compose.yml` e `Dockerfile`
- `frontend/src/App.tsx` e `frontend/src/main.tsx` (não podem perder o routing `/ui`)
- `.env` e `.env.example`

## Plano de Rollback
Caso qualquer mudança na incorporação do OpenJarvis quebre a API, cause vazamento de memória ou conflitos no FastAPI:
1. Reverter o arquivo `app.py` para a versão atual intacta (que suporta `/tokyo/doctor`).
2. Remover os pacotes e dependências não conformes do `requirements.txt` se houver quebra de biblioteca de sistema.
3. Se a interface falhar, utilizar `git restore` nos diretórios de `src/` e recompilar o `npm run build`.
4. Os módulos `tokyo_openjarvis_bridge` serão sempre criados em pastas isoladas para não contaminar a estrutura original do `app.py`.

## Riscos
1. **Sobrescrita do Backend**: O OpenJarvis possui o seu próprio servidor FastAPI (jarvis serve). Existe o risco de tentar fundir `app.py` com `server/api.py` do OpenJarvis e destruir as rotas nativas da Tokyo (`/ui`, `/tokyo/doctor`, etc).
2. **Conflito de Identidade**: OpenJarvis pode alterar títulos, logs, retornos da API ou mensagens de erro expondo o nome "OpenJarvis" em vez de "TokyoOS".
3. **Quebra do Frontend**: Mudanças nas APIs nativas do OpenJarvis (`/v1/*`) que foram migradas podem quebrar a interface gráfica atual já compilada da TokyoOS.

**Decisão**: O checkpoint é válido. Aguardando aprovação para prosseguir à codificação da FASE 14.
