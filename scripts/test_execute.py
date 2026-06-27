import requests
payload = {
    "command": "Criar pasta foo",
    "action_type": "create_folder",
    "payload": {
        "folder_name": "teste_direto"
    }
}
r = requests.post("http://192.168.1.173:8788/tokyo/operator/execute", json=payload)
print(r.status_code, r.text)
