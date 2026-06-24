# SETUP MAC BRIDGE SSH (SEM SENHA)

Para que a TokyoOS no ZimaOS controle o Mac Mini, o servidor Docker precisa estar autorizado a se comunicar com o macOS via SSH de forma automática.

## Requisitos Iniciais no Mac Mini
1. Acesse **Ajustes do Sistema > Geral > Compartilhamento**.
2. Ative o **Acesso Remoto** (Remote Login / SSH).
3. Na janela de informação `(i)` do Acesso Remoto, anote o usuário administrador e permita o acesso apenas para o seu usuário corporativo.

## Rodando o Setup Automático no ZimaOS
Abra o terminal e execute o script SH incluso no projeto. Ele gerará uma chave criptográfica blindada e a empurrará para o Mac Mini.

```bash
cd /DATA/AppData/tokyoos_src/Tokyo-main
bash scripts/setup_mac_bridge_ssh.sh
```

Durante a execução do script:
1. Ele vai pedir o IP (LAN ou Tailscale) do Mac.
2. Ele vai pedir o nome do seu usuário no Mac.
3. Ele vai pedir a sua senha do Mac **uma única vez** para enviar a chave de acesso. A Tokyo não salvará essa senha em lugar nenhum.

### O Que o Script Faz?
Ele roda os comandos de `ssh-keygen -t ed25519` salvando a chave privada estritamente em `/data/tokyo/security/mac_bridge/id_ed25519` (pasta persistente do ZimaOS) e transfere a chave pública usando `ssh-copy-id`. Depois disso, o Mac reconhecerá a TokyoOS definitivamente pelo seu certificado, viabilizando as execuções de comandos AppleScript seguros em background sem interromper o trabalho do humano.
