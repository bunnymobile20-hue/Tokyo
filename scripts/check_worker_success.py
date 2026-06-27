import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.173", username="GrupsBunny", password="32215820", timeout=10)
stdin, stdout, stderr = client.exec_command("docker exec tokyoos timeout 5 python scripts/run_tokyo_voice_agent.py")
print("OUT:", stdout.read().decode())
print("ERR:", stderr.read().decode())
client.close()
