import paramiko

def run():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Conectando ao ZimaOS...")
        client.connect("192.168.1.173", username="GrupsBunny", password="32215820", timeout=10)
        
        print("\n[VERIFICANDO ARQUIVOS]")
        stdin, stdout, stderr = client.exec_command("ls -la Tokyo || echo 'Diretorio Tokyo nao existe'")
        print(stdout.read().decode())
        
        print("\n[TENTANDO BUILD DO DOCKER COM SUDO]")
        cmd = "cd Tokyo && echo '32215820' | sudo -S docker compose up -d --build"
        stdin, stdout, stderr = client.exec_command(cmd)
        
        print("[SAIDA (STDOUT)]")
        print(stdout.read().decode())
        
        print("[ERROS (STDERR)]")
        print(stderr.read().decode())
        
        client.close()
    except Exception as e:
        print("Erro:", e)

if __name__ == "__main__":
    run()
