import json
import os
import time
from loguru import logger

# --- KONFIGURASI PATH ---
DATA_DIR = 'data'
STATUS_FILE = os.path.join(DATA_DIR, 'status.json')
HISTORY_FILE = os.path.join(DATA_DIR, 'trade_history.json')
JOURNAL_FILE = os.path.join(DATA_DIR, 'journal.json')
CONTROL_FILE = os.path.join(DATA_DIR, 'control.json')

def _ensure_dir():
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

def load_status():
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r') as f: return json.load(f)
    except: pass
    return {}

def save_status(data):
    _ensure_dir()
    try:
        temp = STATUS_FILE + '.tmp'
        with open(temp, 'w') as f: json.dump(data, f, indent=4)
        os.replace(temp, STATUS_FILE)
    except Exception as e: logger.error(f"Save Status Error: {e}")

def log_trade_history(trade_data):
    _ensure_dir()
    try:
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f: 
                try: history = json.load(f) 
                except: history = []
        
        trade_data['closed_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
        trade_data['timestamp'] = time.time()
        history.append(trade_data)
        
        with open(HISTORY_FILE, 'w') as f: json.dump(history[-100:], f, indent=4)
    except Exception as e: logger.error(f"Log History Error: {e}")

def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f: return json.load(f)
    except: return []
    return []

def load_journal():
    """FUNGSI BARU: Baca file memori AI"""
    try:
        if os.path.exists(JOURNAL_FILE):
            with open(JOURNAL_FILE, 'r') as f: return json.load(f)
    except: return []
    return []