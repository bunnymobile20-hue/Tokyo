# PHASE 6A: MAC SMB SETUP

## Contexto
A TokyoOS (rodando no ZimaOS) precisará criar e salvar arquivos diretamente no Mac Mini e também ler respostas produzidas localmente pelo Mac. A forma mais estável de transferir esses arquivos na rede local (LAN ou Tailscale) é pelo protocolo de compartilhamento de rede SMB, nativo do macOS.

## Passo a Passo para Configurar o Mac Mini

### 1. Criar a Pasta Base
No Mac Mini, abra o Finder e crie uma pasta exclusiva para a TokyoOS:
`Macintosh HD > Users > (Seu Usuario) > TokyoShared`

### 2. Ativar o Compartilhamento SMB
1. Abra **Ajustes do Sistema** (System Settings).
2. Vá em **Geral > Compartilhamento** (General > Sharing).
3. Ative **Compartilhamento de Arquivos** (File Sharing) e clique no ícone de Informação (i).
4. Em "Pastas Compartilhadas", clique no botão `+` e selecione a pasta `TokyoShared` que você acabou de criar.
5. Em "Usuários", garanta que o seu usuário tenha permissão de Leitura e Gravação.
6. Clique no botão **Opções...** e marque a caixa **Compartilhar arquivos e pastas usando SMB** e marque a caixa ao lado do nome da sua conta (será pedida a senha do Mac).

### 3. Conectar a Pasta no ZimaOS
O ZimaOS (sistema operacional base) deverá se conectar a essa pasta via SMB de forma persistente. Como o ZimaOS usa o CasaOS sob os panos:
1. No Dashboard do ZimaOS, vá em **Arquivos** (Files).
2. Na lateral esquerda, em **Armazenamento de Rede** (Network Storage), clique no sinal `+` e selecione "Connect to Server".
3. Digite o IP do Mac ou o IP do Tailscale (ex: `smb://192.168.1.50` ou `smb://100.80.x.y`).
4. Coloque seu usuário e senha do Mac Mini.
5. Selecione a pasta `TokyoShared`.

> **Mapeamento do Docker**: O `docker-compose.yml` da Tokyo deve espelhar essa pasta mapeando o diretório de rede do ZimaOS diretamente em `/data/tokyo/mac_shared` dentro do container da TokyoOS.

### Fallback
Se a montagem SMB via CasaOS for complexa de realizar no ambiente atual, a `tokyo_mac_bridge` pode ser ajustada nas próximas fases para efetuar _Secure Copy_ (SCP) de arquivos diretamente pelo canal SSH já existente, que também é transparente ao usuário, não bloqueando assim esta fase.
