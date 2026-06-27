import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.173", username="GrupsBunny", password="32215820", timeout=10)
stdin, stdout, stderr = client.exec_command("curl -s http://localhost:8788/tokyo/desktop-agent/status")
for line in stdout.readlines(): print(line, end="")
for line in stderr.readlines(): print("ERR:", line, end="")
client.close()
