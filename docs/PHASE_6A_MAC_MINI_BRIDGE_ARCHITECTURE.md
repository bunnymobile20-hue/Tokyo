# PHASE 6A: MAC MINI BRIDGE ARCHITECTURE

## Visão Geral
A TokyoOS funciona como o cérebro central da operação no ZimaOS/Xeon. O Mac Mini atua como um "braço visual", recebendo comandos para abrir browsers, manipular arquivos em interfaces gráficas e exibir notificações na tela, sem comprometer a estabilidade do servidor Linux.

## Arquitetura de Comunicação
A ponte entre ZimaOS e macOS se dá via dois protocolos principais que garantem estabilidade e segurança sem exigir desenvolvimento de agentes pesados do lado do Mac:

### 1. SSH (Command Channel)
- **Como funciona**: O container Docker da TokyoOS no ZimaOS se conecta ao Mac Mini usando uma chave assimétrica `ed25519` via porta 22.
- **Isolamento**: A chave não tem senha (_passphrase_), mas só autoriza acesso de um IP confiável (o IP do ZimaOS/Tailscale). Nenhuma senha flutua no banco de dados.
- **Automação (AppleScript/osascript)**: O SSH invoca o binário nativo `osascript` no macOS para controlar janelas do Safari, Finder e pop-ups de sistema. A injeção direta de scripts customizados é bloqueada; apenas _templates_ rígidos (allowlist) definidos pela Tokyo podem ser chamados.

### 2. SMB (File Channel)
- **Como funciona**: O Mac Mini cria uma pasta pública (ex: `/Users/user/TokyoShared`) que é exposta via protocolo SMB na rede local ou Tailscale.
- **Montagem**: O ZimaOS monta esse SMB localmente em `/DATA/AppData/tokyoos/mac_shared`, e o Docker volume injeta essa pasta dentro do container da TokyoOS.
- **Objetivo**: Ler e gravar planilhas (CSV) ou documentos (Markdown, PDF) diretamente na mesa do Mac de forma transparente, permitindo que o `open_file_on_mac` (via SSH) ache o arquivo físico com sucesso no Mac.

## Camadas de Segurança (Safety Gate)
- **Anti-RM / Anti-Sudo**: Bloqueados antes de abrir conexão SSH.
- **Sanitização de URLs**: O AppleScript para abrir URL exige protocolos válidos (http, https), impedindo vetores como `file://`, `javascript:` ou `data:`.
- **Token_exposed = False**: Senhas nunca retornam no JSON. O painel visual apenas diz "Executado" ou "Not Configured".

## Evolução Futura
O "Tokyo Mac Agent" poderá evoluir para um daemon local (escrito em Python/Swift) para evitar timeouts do SSH ou contornar as severas políticas de acesso da Apple (_Privacy & Security_) caso o `osascript` deixe de ser viável em versões futuras do macOS.
