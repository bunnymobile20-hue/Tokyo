import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.173", username="GrupsBunny", password="32215820", timeout=10)
stdin, stdout, stderr = client.exec_command("docker exec tokyoos pgrep -f run_tokyo_voice_agent")
pids = stdout.read().decode().strip().split('\n')
print(f"PIDs: {pids}")

# Get the latest logs
stdin, stdout, stderr = client.exec_command("docker logs --tail 200 tokyoos | grep -i agent")
print(stdout.read().decode())
print("ERRORS:", stderr.read().decode())
client.close()
