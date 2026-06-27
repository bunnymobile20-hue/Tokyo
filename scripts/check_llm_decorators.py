import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.173", username="GrupsBunny", password="32215820", timeout=10)
stdin, stdout, stderr = client.exec_command("docker exec tokyoos python -c \"import livekit.agents.llm as llm; print(llm.ai_callable if hasattr(llm, 'ai_callable') else 'not found'); print(llm.ai_callable) if hasattr(llm, 'ai_callable') else None\"")
for line in stdout.readlines(): print(line, end="")
for line in stderr.readlines(): print("ERR:", line, end="")
client.close()
