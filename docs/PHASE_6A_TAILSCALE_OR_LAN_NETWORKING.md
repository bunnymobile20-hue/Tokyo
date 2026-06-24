# PHASE 6A: TAILSCALE OR LAN NETWORKING

## Contexto
O ZimaOS (que hospeda a TokyoOS) e o Mac Mini (que atua como braço executor) precisam de um caminho de rede desimpedido para as conexões SSH (porta 22) e SMB (porta 445).

## Opção 1: Rede Local Estrita (LAN)
Se o ZimaOS e o Mac Mini estiverem no mesmo prédio/roteador corporativo do GrupsBunny:
- Defina o IP do Mac Mini como **Fixo/Estático** nas configurações do roteador ou no macOS (Ajustes do Sistema > Rede > Wi-Fi/Ethernet > Detalhes > TCP/IP). Exemplo: `192.168.1.100`.
- No `config/tokyo_mac_bridge.json`, configure `mac_host` como `192.168.1.100`.
- **Segurança**: O tráfego SSH não deve ser exposto (port forwarding) para a internet pública sob hipótese alguma. Fica restrito apenas à Intranet.

## Opção 2: Tailscale (Recomendada para Estabilidade e Mobilidade)
O Tailscale é uma VPN Mesh baseada em WireGuard que atribui um IP fixo (`100.x.y.z`) permanente para seus dispositivos, não importa a rede física em que estejam conectados.
1. Instale o Tailscale no Mac Mini e faça login com a conta de rede do GrupsBunny.
2. Instale o Tailscale no ZimaOS (geralmente existe um app na ZimaOS App Store ou pode ser injetado via Docker).
3. Pegue o IP Tailscale do Mac Mini (ex: `100.80.30.40`).
4. No `config/tokyo_mac_bridge.json`, configure `mac_host` como o IP Tailscale.

**Vantagens do Tailscale**:
- O Mac Mini Bridge vai responder à TokyoOS mesmo se a equipe de marketing levar o Mac para um evento externo conectado ao roteador do celular.
- Acesso SMB fica automaticamente criptografado (E2EE).

## Firewall do macOS
Se a opção 1 ou 2 falhar, lembre-se de conferir:
- Ajustes do Sistema > Rede > Firewall > Opções: O aplicativo `Acesso Remoto` (Remote Login / SSH) precisa estar permitido para receber conexões entrantes.
