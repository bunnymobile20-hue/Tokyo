import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.173", username="GrupsBunny", password="32215820", timeout=10)
stdin, stdout, stderr = client.exec_command("docker exec tokyoos python -c \"import livekit.agents.llm as llm; import inspect; print(inspect.signature(llm.function_tool)) if hasattr(llm, 'function_tool') else print('No function_tool')\"")
for line in stdout.readlines(): print(line, end="")
client.close()
