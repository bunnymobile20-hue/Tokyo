import socket
import concurrent.futures

def check_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def scan_network():
    print("Procurando o ZimaOS na sua rede local (192.168.1.x)...")
    print("Isso pode levar alguns segundos.\n")
    
    base_ip = "192.168.1."
    found_ips = []
    
    # Scanner de IPs (1 a 254)
    ips_to_scan = [f"{base_ip}{i}" for i in range(1, 255)]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        # Vamos buscar quem está com a porta 80 (Web) e 22 (SSH) abertas
        future_to_ip = {executor.submit(check_port, ip, 80): ip for ip in ips_to_scan}
        
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                if future.result():
                    ssh_open = check_port(ip, 22)
                    found_ips.append((ip, ssh_open))
            except Exception:
                pass

    if found_ips:
        print("Dispositivos encontrados com interface Web (possíveis ZimaOS):")
        for ip, ssh in found_ips:
            status_ssh = "Aberta" if ssh else "Fechada/Bloqueada"
            print(f" -> IP: {ip} | Porta SSH: {status_ssh}")
            if ip == "192.168.1.173":
                print("    (Este é o IP que estávamos tentando acessar!)")
    else:
        print("Nenhum dispositivo com interface web foi encontrado na rede 192.168.1.x!")

if __name__ == "__main__":
    scan_network()
