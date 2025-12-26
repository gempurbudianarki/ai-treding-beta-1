import json
import os
import time
from loguru import logger

# PATH FILE
STATUS_FILE = "data/status.json"
HISTORY_FILE = "data/trade_history.json"
JOURNAL_FILE = "data/journal.json"
CHAT_FILE = "data/ai_chat_log.json"
CONTROL_FILE = "data/control.json"

def _ensure_dir():
    if not os.path.exists("data"):
        os.makedirs("data")

# === LOADERS (BACA DATA) ===

def load_status():
    if not os.path.exists(STATUS_FILE): return {}
    try:
        with open(STATUS_FILE, 'r') as f: return json.load(f)
    except: return {}

def load_history():
    """Membaca seluruh riwayat trading"""
    if not os.path.exists(HISTORY_FILE): return []
    try:
        with open(HISTORY_FILE, 'r') as f:
            data = json.load(f)
            # Validasi: Pastikan formatnya LIST, bukan dict/objek tunggal
            if isinstance(data, list):
                return data
            else:
                return []
    except: return []

def load_journal():
    if not os.path.exists(JOURNAL_FILE): return []
    try:
        with open(JOURNAL_FILE, 'r') as f: return json.load(f)
    except: return []

def load_chat_log():
    if not os.path.exists(CHAT_FILE): return []
    try:
        with open(CHAT_FILE, 'r') as f: return json.load(f)
    except: return []

# === SAVERS (SIMPAN DATA) ===

def save_status(data):
    """Menyimpan status real-time (Atomic Write)"""
    _ensure_dir()
    temp = f"{STATUS_FILE}.tmp"
    try:
        with open(temp, 'w') as f:
            json.dump(data, f, indent=2)
        os.replace(temp, STATUS_FILE)
    except Exception as e:
        logger.error(f"Status Save Error: {e}")

def log_trade_history(trade_data):
    """
    PERBAIKAN UTAMA: APPEND LOGIC
    1. Baca history lama.
    2. Tambah trade baru.
    3. Simpan ulang semua.
    """
    _ensure_dir()
    
    # 1. Baca data lama dulu
    current_history = load_history()
    
    # 2. Tambah data baru
    trade_data['closed_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
    current_history.append(trade_data)
    
    # 3. Simpan kembali (Limit 500 transaksi terakhir biar file gak kegedean)
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(current_history[-500:], f, indent=2)
    except Exception as e:
        logger.error(f"History Save Error: {e}")

# Fungsi Control Panel (Opsional jika dibutuhkan app.py)
def load_control():
    if not os.path.exists(CONTROL_FILE): 
        return {"trading_enabled": True}
    try:
        with open(CONTROL_FILE, 'r') as f: return json.load(f)
    except: return {"trading_enabled": True}

def save_control(data):
    _ensure_dir()
    try:
        with open(CONTROL_FILE, 'w') as f: json.dump(data, f)
    except: pass