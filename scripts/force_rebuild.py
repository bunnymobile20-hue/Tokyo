import paramiko
import os

def force_rebuild():
    print("===============================================")
    print("🔨 FORÇANDO REBUILD SEM CACHE NO ZIMAOS")
    print("===============================================")
    
    ip = "192.168.1.173"
    user = "GrupsBunny"
    senha = "32215820"
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=user, password=senha, timeout=10)
        
        cmd = """
        cd /tmp/Tokyo
        # Removemos o container atual para forçar recriação
        echo '32215820' | sudo -S docker rm -f tokyoos || true
        # Força o build sem cache para a camada do python (para garantir que os novos arquivos React subam)
        echo '32215820' | sudo -S HOME=/tmp docker compose build --no-cache
        echo '32215820' | sudo -S HOME=/tmp docker compose up -d --force-recreate
        """
        
        print("Enviando comando para reconstruir do zero (ISSO VAI DEMORAR UM POUCO E PODE PARECER TRAVADO, MAS ESTÁ RODANDO).")
        stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
        
        for line in iter(stdout.readline, ""):
            print(line, end="")
            
        client.close()
        print("\n✅ REBUILD FINALIZADO!")
    except Exception as e:
        print("❌ Erro:", e)

if __name__ == "__main__":
    force_rebuild()
