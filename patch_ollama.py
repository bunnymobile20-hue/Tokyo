#!/usr/bin/env python3
import os

os.system('''
cat << 'EOF' > /tmp/override.conf
[Service]
Environment="OLLAMA_ORIGINS=*"
Environment="OLLAMA_HOST=0.0.0.0"
EOF
''')

os.system('sudo mkdir -p /etc/systemd/system/ollama.service.d')
os.system('sudo cp /tmp/override.conf /etc/systemd/system/ollama.service.d/override.conf')
os.system('sudo systemctl daemon-reload')
os.system('sudo systemctl restart ollama')
print("OLLAMA_CORS_PATCH_OK")
