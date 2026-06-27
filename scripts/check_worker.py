import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.173", username="GrupsBunny", password="32215820", timeout=10)
stdin, stdout, stderr = client.exec_command("docker exec tokyoos ps aux | grep -i run_tokyo_voice_agent")
for line in stdout.readlines(): print(line, end="")
client.close()
