import paramiko
import os
import subprocess

def run():
    print("===============================================")
    print("🚀 DEPLOY DEFINITIVO VIA SCP (SEM DEPENDER DO GIT)")
    print("===============================================")
    
    # 1. Zip local directory
    print("[1/4] Compactando os arquivos do Mac...")
    os.chdir("/Users/dalilabarreto/.gemini/antigravity/scratch/")
    # Zip the Tokyo folder excluding .git and heavy node_modules to keep it fast
    subprocess.run("tar -czf tokyo_deploy.tar.gz --exclude='.git' --exclude='node_modules' --exclude='.npm-cache' --exclude='__pycache__' Tokyo/", shell=True)
    
    ip = "192.168.1.173"
    user = "GrupsBunny"
    senha = "32215820"
    
    try:
        print(f"[2/4] Conectando via SSH em {user}@{ip}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=user, password=senha, timeout=10)
        
        print("[3/4] Enviando os arquivos para o ZimaOS (Upload)...")
        sftp = client.open_sftp()
        sftp.put("tokyo_deploy.tar.gz", "/tmp/tokyo_deploy.tar.gz")
        sftp.close()
        
        print("[4/4] Extraindo arquivos e forçando o Build com SUDO...")
        cmd = """
        cd /tmp
        tar -xzf tokyo_deploy.tar.gz
        cd Tokyo
        echo '32215820' | sudo -S chmod +x setup-tokyo.sh
        echo '32215820' | sudo -S ./setup-tokyo.sh
        """
        stdin, stdout, stderr = client.exec_command(cmd)
        
        # Leitura em tempo real para não perder nenhum log
        for line in iter(stdout.readline, ""):
            print(line, end="")
            
        for line in iter(stderr.readline, ""):
            print("ERRO:", line, end="")
            
        client.close()
        print("\n✅ DEPLOY FINALIZADO!")
        print("Acesse o painel: http://192.168.1.173:8788/ui")
    except Exception as e:
        print("\n❌ Erro durante o deploy:", e)

if __name__ == "__main__":
    run()
