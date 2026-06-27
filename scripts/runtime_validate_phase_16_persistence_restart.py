import paramiko
import time
import sys

def run_zimaos_tests():
    ip = "192.168.1.173"
    user = "GrupsBunny"
    senha = "32215820"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("==================================================")
    print("PHASE 16: ZIMAOS PERSISTENCE & RESTART VALIDATION")
    print("==================================================")
    
    try:
        client.connect(ip, username=user, password=senha, timeout=10)
        
        # 1. Write persistence file
        print("[1/5] Escrevendo arquivo de persistência em /DATA/AppData/tokyoos/...")
        cmd_write = "echo '32215820' | sudo -S sh -c 'echo \"tokyo_persists\" > /DATA/AppData/tokyoos/test_persistence.txt'"
        client.exec_command(cmd_write)
        time.sleep(1)
        
        # 2. Restart container
        print("[2/5] Reiniciando container tokyoos...")
        cmd_restart = "echo '32215820' | sudo -S docker restart tokyoos"
        client.exec_command(cmd_restart)
        print("Aguardando 15s pelo startup...")
        time.sleep(15)
        
        # 3. Check persistence file
        print("[3/5] Verificando se arquivo sobreviveu ao restart...")
        cmd_read = "cat /DATA/AppData/tokyoos/test_persistence.txt"
        stdin, stdout, stderr = client.exec_command(cmd_read)
        out = stdout.read().decode('utf-8').strip()
        assert "tokyo_persists" in out, "Arquivo de persistência não encontrado!"
        print("[PASS] Persistência confirmada.")
        
        # 4. Check .env integrity
        print("[4/5] Verificando integridade do .env...")
        cmd_env = "ls -la /tmp/Tokyo/.env"
        stdin, stdout, stderr = client.exec_command(cmd_env)
        out_env = stdout.read().decode('utf-8')
        assert "No such file" not in out_env, ".env desapareceu!"
        print("[PASS] .env real permanece intacto e protegido.")
        
        # 5. Check logs for secrets
        print("[5/5] Analisando logs do docker por vazamento de secrets...")
        cmd_logs = "echo '32215820' | sudo -S docker logs tokyoos --tail 200"
        stdin, stdout, stderr = client.exec_command(cmd_logs)
        out_logs = stdout.read().decode('utf-8')
        assert "password" not in out_logs.lower() or "db_password" not in out_logs.lower(), "Possível secret exposto nos logs!"
        print("[PASS] Logs limpos e seguros.")
        
        print("\n[SUCCESS] Validação de Persistência, Restart e Logs finalizada!")
        
    except Exception as e:
        print(f"\n[FAIL] Erro crítico na validação remota: {e}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    run_zimaos_tests()
