import paramiko

def run():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Conectando ao ZimaOS para ler os logs com SUDO...")
        client.connect("192.168.1.173", username="GrupsBunny", password="32215820", timeout=10)
        
        print("\n[STATUS DO CONTAINER]")
        stdin, stdout, stderr = client.exec_command("echo '32215820' | sudo -S docker ps -a | grep tokyo")
        print(stdout.read().decode())
        
        print("\n[LOGS DO TOKYOOS]")
        stdin, stdout, stderr = client.exec_command("echo '32215820' | sudo -S docker logs --tail 100 tokyoos")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        client.close()
    except Exception as e:
        print("Erro:", e)

if __name__ == "__main__":
    run()
