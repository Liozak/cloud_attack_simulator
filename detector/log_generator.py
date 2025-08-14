import time
import random
import json

LOG_FILE = "simulated_traffic.log"

def generate_log_entry():
    attack_ips = ["192.168.1.10", "10.0.0.5"]
    normal_ips = [f"192.168.1.{i}" for i in range(20, 30)]

    # Bias: attack IPs appear more often
    ip_pool = attack_ips * 4 + normal_ips

    ip = random.choice(ip_pool)
    timestamp = time.time()

    if ip == "192.168.1.10":
        # Port scan traffic
        return {
            "source_ip": ip,
            "timestamp": timestamp,
            "event_type": "connection_attempt"
        }
    elif ip == "10.0.0.5":
        # Brute-force attack
        return {
            "source_ip": ip,
            "timestamp": timestamp,
            "event_type": "login_failure"
        }
    else:
        # Normal traffic
        return {
            "source_ip": ip,
            "timestamp": timestamp,
            "event_type": "normal_traffic"
        }

def run():
    print("[*] Log generator started. Press Ctrl+C to stop.\n")
    try:
        while True:
            entry = generate_log_entry()
            with open(LOG_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")
            time.sleep(0.3)  # ~3 logs/sec
    except KeyboardInterrupt:
        print("\n[+] Log generation stopped.")

if __name__ == "__main__":
    run()
