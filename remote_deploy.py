import pexpect
import sys

host = "192.168.1.252"
user = "GrupsBunny"
password = "32215820"

print(f"Connecting to {user}@{host}...")
child = pexpect.spawn(f"ssh -o StrictHostKeyChecking=no {user}@{host}", encoding='utf-8', timeout=30)

try:
    child.expect("password:")
    child.sendline(password)
    
    # Wait for prompt
    child.expect(r"\$ ")
    print("Logged in successfully.")
    
    # Clone repository
    print("Cloning repository...")
    child.sendline("rm -rf /tmp/tokyo_deploy && git clone https://github.com/bunnymobile20-hue/Tokyo.git /tmp/tokyo_deploy")
    child.expect(r"\$ ", timeout=60)
    print("Repository cloned.")
    
    # Run setup script
    print("Running setup script...")
    child.sendline("cd /tmp/tokyo_deploy && echo '" + password + "' | sudo -S ./setup-tokyo.sh")
    
    # Capture the output of setup-tokyo.sh until it finishes
    child.expect(r"\$ ", timeout=300)
    print(child.before)
    
    print("Deployment finished!")
    child.sendline("exit")

except Exception as e:
    print(f"Error occurred: {e}")
    print(child.before)
    sys.exit(1)
