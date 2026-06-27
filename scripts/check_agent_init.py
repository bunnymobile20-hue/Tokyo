import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.173", username="GrupsBunny", password="32215820", timeout=10)
stdin, stdout, stderr = client.exec_command("docker exec tokyoos python -c \"import livekit.agents as agents; import inspect; print(inspect.signature(agents.Agent.__init__)) if hasattr(agents, 'Agent') else print('No Agent')\"")
for line in stdout.readlines(): print(line, end="")
client.close()
