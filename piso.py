#!/usr/bin/env python3
from flask import Flask, request, jsonify
import threading
import time
import random
from colorama import Fore, Style, init

init()

app = Flask(__name__)

class PisoWifiState:
    def __init__(self):
        self.credits = 0.0
        self.coin_slot_active = False
        self.system_crashed = False
        self.mac_address = "0A:73:BF:77:31:BF"
        self.ghost_coins = 0
        self.debug = True
        self.crash_chance = 0.7  # 70% chance to crash on malicious requests

state = PisoWifiState()

def log(message, color=Fore.WHITE):
    if state.debug:
        print(color + f"[SIMULATOR] {message}" + Style.RESET_ALL)

@app.route('/')
def home():
    return "PisoWifi Simulator - Debug Mode Active"

@app.route('/insert_coin', methods=['POST'])
def insert_coin():
    if state.system_crashed:
        log("Coin insertion blocked - system crashed", Fore.RED)
        return "System rebooting...", 503
    
    amount = float(request.form.get('amount', '1'))
    state.credits += amount
    state.coin_slot_active = True
    log(f"Real coin inserted: P{amount}. Credits: P{state.credits}", Fore.GREEN)
    
    # Coin slot stays active for 8 seconds
    threading.Timer(8, lambda: setattr(state, 'coin_slot_active', False)).start()
    return jsonify(status="success", credits=state.credits)

@app.route('/status')
def get_status():
    if state.system_crashed:
        return jsonify(status="rebooting"), 503
    return jsonify(
        credits=state.credits,
        mac_address=state.mac_address,
        coin_slot_active=state.coin_slot_active,
        ghost_coins=state.ghost_coins
    )

@app.route('/config')
def get_config():
    if should_crash():
        crash_system()
        return "System rebooting...", 503
    return jsonify(version="1.0", memory=random.randint(1000, 50000))

@app.route('/admin/reboot')
def reboot():
    threading.Thread(target=do_reboot).start()
    return "Rebooting system..."

def should_crash():
    """Determine if current request should crash the system"""
    user_agent = request.headers.get('User-Agent', '')
    is_malicious = any(x in user_agent for x in ['curl', 'python', 'exploit'])
    return is_malicious and random.random() < state.crash_chance

def crash_system():
    state.system_crashed = True
    log("SYSTEM CRASH TRIGGERED!", Fore.RED)
    
    # Generate ghost coin if coin slot was active
    if state.coin_slot_active:
        state.credits += 1
        state.ghost_coins += 1
        log(f"GHOST COIN GENERATED! Total credits: P{state.credits}", Fore.YELLOW)
    
    # Auto-recover after crash
    threading.Timer(3, do_reboot).start()

def do_reboot():
    state.system_crashed = False
    log("System reboot completed", Fore.CYAN)

def run_simulator():
    print(Fore.BLUE + """
    PisoWifi Simulator (Debug Mode)
    ------------------------------
    Endpoints:
    POST /insert_coin - Insert coins (amount=1)
    GET /status - Check system status
    GET /config - Vulnerable endpoint
    GET /admin/reboot - Manual reboot
    
    Configuration:
    - Crash chance: 70%
    - Coin slot active for 8s after insertion
    - Auto-recovery after 3s crash
    """ + Style.RESET_ALL)
    
    app.run(host='0.0.0.0', port=80, threaded=True)

if __name__ == '__main__':
    run_simulator()