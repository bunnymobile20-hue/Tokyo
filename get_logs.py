import paramiko

ip = "192.168.1.173"
user = "GrupsBunny"
senha = "32215820"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(ip, username=user, password=senha, timeout=10)

stdin, stdout, stderr = client.exec_command("docker logs --tail 100 tokyoos")
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())
client.close()
