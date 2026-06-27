# SETUP MANUAL: CREDENCIAIS REAIS DO SIBERIAN (ZIMAOS)

> [!WARNING]  
> Este procedimento ensina como ligar a TokyoOS ao Siberian ERP em modo 100% Read-Only.  
> As credenciais abaixo **jamais** devem ser inseridas em chats de IA, enviadas por e-mail sem criptografia, ou "hardcoded" em arquivos `.py`.

## 1. Conectando no ZimaOS
Abra seu terminal e acesse o servidor principal:
```bash
ssh GrupsBunny@192.168.1.173
```
*(Digite sua senha SSH de operador, não a do ERP)*

## 2. Editando o Arquivo de Ambiente (.env)
Acesse a pasta persistente onde os segredos estão isolados.
```bash
sudo nano /tmp/Tokyo/.env
```
*(Nota: O deploy via SCP envia o código para `/tmp/Tokyo`, então é lá que o `.env` real fica hospedado temporariamente, antes de ser carregado pelos containers. Caso você mapeie de outra forma futuramente, edite o `.env` no root do projeto no ZimaOS).*

## 3. Inserindo as Variáveis
No final do arquivo `.env`, adicione exatamente estas linhas e substitua as strings pelo seu endpoint real e token do Siberian. **Não altere** os parâmetros de segurança.

```env
# SIBERIAN READ-ONLY INTEGRATION
SIBERIAN_API_BASE_URL="https://sua-empresa.siberian.com.br/api/v1"
SIBERIAN_API_TOKEN="cole_seu_token_real_aqui_sem_aspas_e_sem_espacos"
SIBERIAN_API_MODE="read_only"
SIBERIAN_WRITE_ENABLED="false"
SIBERIAN_TIMEOUT_SECONDS="30"
SIBERIAN_VERIFY_SSL="true"
```

## 4. Reiniciando a TokyoOS Seguramente
Após salvar (`CTRL+O`, `Enter`, `CTRL+X`), você precisa forçar a TokyoOS a ler as novas variáveis do `.env` e fazer o boot a frio:
```bash
sudo docker restart tokyoos
```

## 5. Validação Visual
Após 10 segundos, acesse o painel da TokyoOS no seu navegador:
- **URL**: `http://192.168.1.173:8788/ui`
- Observe se o badge Siberian deixou de ser "not_configured" e passou a constar "real_data" e "read_only".

Se os Agentes (CFO, COO, Estoque) começarem a retornar números precisos de relatórios reais, o conector teve sucesso no handshake seguro (GET).
