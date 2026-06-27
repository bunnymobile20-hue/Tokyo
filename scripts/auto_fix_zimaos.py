import os
import sys
import time
import subprocess

print("===============================================")
print("🤖 ZIMAOS AUTO-FIX & DEPLOY SCRIPT (PHASE 14)")
print("===============================================")
print("Preparando dependências locais (paramiko)...")
subprocess.run([sys.executable, "-m", "pip", "install", "paramiko", "-q"])

import paramiko

def run():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    ip = "192.168.1.173"
    user = "GrupsBunny"
    senha = "32215820"
    
    try:
        print(f"\n[1/4] Conectando via SSH em {user}@{ip}...")
        client.connect(ip, username=user, password=senha, timeout=10)
        print("✅ Conectado com sucesso!")
        
        print("\n[2/4] Analisando o container que causou a tela preta (tokyoos)...")
        stdin, stdout, stderr = client.exec_command("docker logs --tail 30 tokyoos")
        logs = stdout.read().decode() + stderr.read().decode()
        if logs:
            print("--- ÚLTIMOS LOGS DO ERRO ---")
            print(logs)
            print("----------------------------")
        else:
            print("Nenhum log encontrado. O container pode ter sido removido.")

        print("\n[3/4] Removendo os containers travados e limpando a porta 8788...")
        client.exec_command("docker stop tokyoos && docker rm tokyoos")
        time.sleep(2)

        print("\n[4/4] Baixando a Phase 14 e refazendo o Deploy no ZimaOS...")
        # Atualiza o repositório no ZimaOS e roda o setup
        deploy_cmd = """
        if [ ! -d 'Tokyo' ]; then
            git clone https://github.com/bunnymobile20-hue/Tokyo.git
        fi
        cd Tokyo
        git reset --hard
        git pull origin fusion-tokyo-openjarvis
        chmod +x setup-tokyo.sh
        ./setup-tokyo.sh
        """
        stdin, stdout, stderr = client.exec_command(deploy_cmd)
        
        # Lendo output do deploy
        while True:
            line = stdout.readline()
            if not line:
                break
            print(line.strip())
            
        print("\n✅ DEPLOY DA PHASE 14 CONCLUÍDO NO ZIMAOS!")
        print("▶ Abra no navegador: http://192.168.1.173:8788/ui")
        print("▶ Painel do ZimaOS: http://192.168.1.173/#/")
        
    except Exception as e:
        print(f"\n❌ Erro crítico ao conectar com o ZimaOS: {e}")
        print("Verifique se o IP 192.168.1.173 está correto e a máquina está ligada.")
    finally:
        client.close()

if __name__ == "__main__":
    run()
