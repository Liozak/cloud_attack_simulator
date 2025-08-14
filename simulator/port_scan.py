# simulator/port_scan.py

import socket
from datetime import datetime

def port_scan(target_ip, port_range=(1, 1024)):
    print(f"\n[+] Starting port scan on {target_ip}")
    open_ports = []
    start_time = datetime.now()

    for port in range(port_range[0], port_range[1] + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((target_ip, port))
        if result == 0:
            open_ports.append(port)
            print(f"[OPEN] Port {port}")
        sock.close()

    end_time = datetime.now()
    print(f"\n[✓] Scan completed in {end_time - start_time}")
    return open_ports

# Run this only if this script is executed directly
if __name__ == "__main__":
    target = input("Enter target IP (e.g. 127.0.0.1): ")
    ports = port_scan(target)
    print(f"\n[✔] Open ports: {ports}")
