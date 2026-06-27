# CHECKPOINT PRÉ-DEPLOY ZIMAOS (PHASE 15)

**Data e Hora**: 2026-06-26 12:05:00-03:00  
**Status**: DEPLOYMENT TO ZIMAOS READY
**Sistema Alvo**: TokyoOS (ZimaOS / Docker na porta 8788 em 192.168.1.173)  

## Alterações Pendentes para o Deploy
- A fusão estrutural (Bridge) do OpenJarvis foi concluída e testada localmente.
- O script `scripts/deploy_via_scp.py` foi modificado para **excluir o `.env`** durante a compactação (`tar -czf tokyo_deploy.tar.gz --exclude='.env' ...`).
- O script `setup-tokyo.sh` já assegura que, se o `/DATA/AppData/tokyoos` não existir, ele é criado, mas não apaga nada existente. O `.env` só é copiado se não existir, e mesmo se tentar, não estará no tarball de deploy.

## Plano de Rollback Remoto (ZimaOS)
Se o deploy falhar e o serviço principal (`app.py`) quebrar no ZimaOS:
1. Reverter os arquivos `app.py`, `tokyo_agent_core/routes.py` na máquina remota apagando a pasta `tokyo_openjarvis_bridge/`.
2. Restaurar o `.env` via snapshot se ele fosse corrompido (embora tenhamos garantido sua exclusão do upload).
3. Reiniciar os containers Docker: `docker-compose restart`.

## Segurança Garantida
- **Sem senhas e chaves vazadas**: As exclusões (`.env`, `.git`) no TAR garantem que nenhum estado local confidencial ou secrets sejam transportados para o servidor e causem sobrescritas no ambiente produtivo.
- **Porta**: Mapeamento 8788 continua preservado e a porta 443 do painel principal não foi tocada.
