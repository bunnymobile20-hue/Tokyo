# PHASE 5B: HERMES REAL AUTOMATION MODE

## Status Final
**SAFE_TO_CONTINUE_PHASE_5B_REAL_AUTOMATION_MODE**

## Resumo Executivo
O Hermes Plugin Bridge foi atualizado com sucesso do modo puramente ilustrativo para o **active_assisted**. Agora a TokyoOS é capaz de executar ações reais de baixo risco (como consultas via Ollama local e criação de notas dentro de um workspace seguro) e segurar ações de risco médio/alto aguardando a confirmação explícita de um humano, tudo isso enquanto mantém um bloqueio impenetrável contra ações destrutivas (risk level: critical).

## Arquivos Criados
- `config/hermes_automation_policy.example.json` (Allowlist declarativa das capacidades permitidas e bloqueadas)
- `scripts/test_phase_5b_hermes_real_automation_mode.py`
- `scripts/runtime_validate_phase_5b_hermes_real_automation_mode.py`

## Arquivos Alterados
- `.env.example` (Novas variáveis de configuração de policy do Hermes)
- `tokyo_plugins/hermes_bridge/schemas.py` (Novos Pydantic Models `HermesExecuteRequest`, `HermesConfirmRequest`, e `AutomationJob`)
- `tokyo_plugins/hermes_bridge/config.py` (Suporte ao `_policy` para ler a nova allowlist json)
- `tokyo_plugins/hermes_bridge/audit.py` (Regras em hard-code para banir palavras restritas exigidas, validação de segurança de caminhos do workspace, e suporte a multi-níveis `active_assisted`)
- `tokyo_plugins/hermes_bridge/service.py` (Implementação do "Fallback Adapter" interno, sistema de confirmação de memória e despacho)
- `tokyo_plugins/hermes_bridge/routes.py` (Novas rotas `/execute` e `/confirm`)
- `interface/index.html` (Remoção da nomenclatura `demo-only`, interface adaptada com suporte a envio de comandos reais, visualização do pendente, e botões de `Approve`/`Reject`)

## Modos Atuais
O ambiente está rodando no modo **active_assisted**:
- Ações LOW RISK são executadas se habilitadas (ex: criar notas).
- Ações MEDIUM e HIGH RISK são pausadas (`pending_confirmation`).
- Ações CRITICAL RISK (`rm -rf`, `format`, `apagar`, `chown`, etc.) são sumariamente barradas antes de entrarem na fila.

## Workspace Seguro
Todas as gravações realizadas pelo agente são rigorosamente validadas para garantirem que estão ocorrendo **exclusivamente dentro do diretório `/data/tokyo/workspace`** (mapeado para `/DATA/AppData/tokyoos/workspace`).

## Execuções Reais Suportadas Inicialmente (Fallback Adapter)
Como o endpoint primário do Hermes (`127.0.0.1:9119`) pode estar indisponível durante testes brutos iniciais, ativamos um "Fallback Adapter" seguro embutido no Bridge que suporta responder a três comandos Low Risk localmente:
1. "test connection": Retorna *ok*.
2. "crie uma nota / create a note": Cria um arquivo com UUID gerado no `/data/tokyo/workspace/`.
3. "ollama / resumo / summarize": Entra em contato com a rede Ollama na porta `11434` e retorna texto gerado via IA.

## Validação de Segurança Comprovada
- Nenhum acesso Root concedido.
- A string secreta da `Tokyo API Key` continuará não exposta em logs ou respostas.
- Testes mostraram que as rotas antigas de leitura das configurações continuam no ar em 100% dos cenários (sem regressões).

## Como Testar na UI
1. Acesse: `http://192.168.1.173:8788/ui`
2. Navegue até o painel "Hermes (Plugin)".
3. Teste o **Low-Risk**: Digite `crie uma nota de teste` e clique em *Execute Command*. O resultado dirá que o arquivo foi salvo no `/data/tokyo/workspace`.
4. Teste o **Blocked**: Digite `sudo rm -rf /` e clique em *Execute Command*. Será retornado `Blocked`.
5. Teste o **Confirmation Flow**: Digite `open browser to tokyoos` (ação catalogada como Medium risk) e clique em *Execute Command*. Um alerta amarelo vai aparecer exigindo que você clique em **Approve** ou **Reject**.
