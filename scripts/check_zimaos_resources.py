import paramiko

def run():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Conectando ao ZimaOS para verificar os recursos (Memória/Disco)...")
        client.connect("192.168.1.173", username="GrupsBunny", password="32215820", timeout=10)
        
        print("\n[VERIFICANDO MEMORIA (RAM)]")
        stdin, stdout, stderr = client.exec_command("free -m")
        print(stdout.read().decode())
        
        print("\n[VERIFICANDO DISCO (/DATA)]")
        stdin, stdout, stderr = client.exec_command("df -h /DATA")
        print(stdout.read().decode())
        
        client.close()
    except Exception as e:
        print("Erro:", e)

if __name__ == "__main__":
    run()
