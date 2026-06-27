import paramiko
import os
import sys

def check_status():
    print("===============================================")
    print("🔍 VERIFICANDO STATUS DO BUILD NO ZIMAOS")
    print("===============================================")
    
    ip = "192.168.1.173"
    user = "GrupsBunny"
    senha = "32215820"
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=user, password=senha, timeout=10)
        
        print("1. Verificando processos do Docker (se o build ainda está rodando)...")
        stdin, stdout, stderr = client.exec_command("ps aux | grep docker")
        ps_output = stdout.read().decode('utf-8')
        if "build" in ps_output:
            print("⏳ O processo de build ainda está ativo no servidor.")
        else:
            print("🛑 Não há processo de build rodando ativamente no momento.")

        print("\n2. Capturando as últimas 50 linhas de log do sistema para ver onde travou...")
        # Since it runs via docker-compose up, the output might not be logged to a file unless we check syslog or docker daemon logs.
        # But we can check if the container actually started
        stdin, stdout, stderr = client.exec_command("docker ps -a")
        print(stdout.read().decode('utf-8'))
        
        client.close()
    except Exception as e:
        print("❌ Erro ao conectar:", e)

if __name__ == "__main__":
    check_status()
