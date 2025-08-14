import time
import logging
import json
from datetime import datetime

# Configure standard log file
logging.basicConfig(
    filename='alerts.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# JSON alert logger (for GUI)
def log_json_alert(alert_type, ip):
    alert_data = {
        "timestamp": time.time(),  # float timestamp for charting
        "type": alert_type,
        "ip": ip
    }
    with open("alerts.json.log", "a") as json_file:
        json.dump(alert_data, json_file)
        json_file.write("\n")

LOG_FILE = "simulated_traffic.log"

# Port scan detection rule
def detect_port_scan(ip_events):
    suspicious = []
    for ip, timestamps in ip_events.items():
        recent = [ts for ts in timestamps if time.time() - ts < 10]
        if len(recent) >= 5:
            suspicious.append(ip)
    return suspicious

# Brute-force login detection rule
def detect_brute_force(failed_logins):
    suspicious = []
    for ip, events in failed_logins.items():
        recent = [ts for ts in events if time.time() - ts < 15]
        if len(recent) >= 5:
            suspicious.append(ip)
    return suspicious

def run_detection():
    print("[*] Real-time detection started... Press Ctrl+C to stop.")
    seen_lines = 0
    ip_events = {}
    failed_logins = {}

    try:
        while True:
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()

            new_lines = lines[seen_lines:]
            seen_lines = len(lines)

            for line in new_lines:
                try:
                    entry = json.loads(line)
                    ip = entry.get("source_ip")
                    ts = entry.get("timestamp", time.time())

                    ip_events.setdefault(ip, []).append(ts)

                    if entry.get("event_type") == "login_failure":
                        failed_logins.setdefault(ip, []).append(ts)

                except json.JSONDecodeError:
                    continue

            # Port scan detection
            portscan_ips = detect_port_scan(ip_events)
            for ip in portscan_ips:
                msg = f"Port scan detected from IP: {ip}"
                print("[!] " + msg)
                logging.warning(msg)
                log_json_alert("Port Scan", ip)
                ip_events[ip] = []

            # Brute-force detection
            brute_ips = detect_brute_force(failed_logins)
            for ip in brute_ips:
                msg = f"Brute-force login attack from IP: {ip}"
                print("[!] " + msg)
                logging.warning(msg)
                log_json_alert("Brute Force", ip)
                failed_logins[ip] = []

            time.sleep(2)

    except KeyboardInterrupt:
        print("\n[+] Detection stopped.")

if __name__ == "__main__":
    run_detection()
