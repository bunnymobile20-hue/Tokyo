import paramiko
import time

def run():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Conectando ao ZimaOS...")
        client.connect("192.168.1.173", username="GrupsBunny", password="32215820", timeout=10)
        
        print("\n[1/3] Forçando Build Blindado (Ignorando quedas de rede)...")
        # ZimaOS bloqueia /root como read-only. Precisamos forçar o HOME=/tmp para o sudo
        cmd_start = "cd /tmp/Tokyo && echo '32215820' | sudo -S env HOME=/tmp DOCKER_CONFIG=/tmp nohup docker compose up -d --build > /tmp/build_log.txt 2>&1 &"
        client.exec_command(cmd_start)
        
        print("[2/3] Aguardando o Build terminar (Isso leva cerca de 2 minutos)...")
        # Vamos monitorar o arquivo de log a cada 5 segundos
        while True:
            time.sleep(5)
            stdin, stdout, stderr = client.exec_command("tail -n 1 /tmp/build_log.txt")
            last_line = stdout.read().decode().strip()
            if "Started" in last_line or "Running" in last_line or "Container tokyoos" in last_line:
                print("-> Sucesso detectado no log!")
                break
            if "Error" in last_line or "failed" in last_line:
                print("-> Possível erro detectado ou processando:", last_line)
                
            # Verifica se o processo do docker-compose ainda está rodando
            _, out_ps, _ = client.exec_command("pgrep -f 'docker compose'")
            if not out_ps.read().decode():
                break
                
        print("\n[3/3] Build Finalizado. Capturando as últimas 20 linhas do resultado:")
        stdin, stdout, stderr = client.exec_command("tail -n 20 /tmp/build_log.txt")
        print(stdout.read().decode())
        
        client.close()
    except Exception as e:
        print("Erro:", e)

if __name__ == "__main__":
    run()
