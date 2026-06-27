import paramiko
import sys

def get_logs():
    ip = "192.168.1.173"
    user = "GrupsBunny"
    senha = "32215820"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, username=user, password=senha, timeout=10)
        cmd = "echo '32215820' | sudo -S docker logs tokyoos"
        stdin, stdout, stderr = client.exec_command(cmd)
        
        lines = stdout.readlines()
        print("STDOUT LAST 50 LINES:")
        for line in lines[-50:]:
            print(line, end="")
            
        lines_err = stderr.readlines()
        print("STDERR LAST 10 LINES:")
        for line in lines_err[-10:]:
            print(line, end="")
            
    except Exception as e:
        print("Error:", e)
    finally:
        client.close()

if __name__ == "__main__":
    get_logs()
