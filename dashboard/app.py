from flask import Flask, render_template, jsonify, request
import json
import os
# Import fungsi loader dengan aman
from dashboard.status_loader import load_status, load_history, load_journal, CONTROL_FILE

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

# --- API ENDPOINTS ---

@app.route('/api/status')
def get_status_api():
    """Mengembalikan data real-time (saldo, posisi)"""
    return jsonify(load_status())

@app.route('/api/history')
def get_history_api():
    """Mengembalikan riwayat trade (win/loss)"""
    return jsonify(load_history())

@app.route('/api/journal')
def get_journal_api():
    """Mengembalikan memori/pelajaran AI"""
    return jsonify(load_journal())

@app.route('/api/chat')
def get_chat_api():
    """Mengambil log percakapan Qwen & DeepSeek"""
    try:
        path = 'data/ai_chat_log.json'
        if os.path.exists(path):
            with open(path, 'r') as f: return jsonify(json.load(f))
    except: pass
    return jsonify([])

@app.route('/api/control', methods=['POST'])
def send_command():
    """Menerima tombol Start/Stop/Panic"""
    data = request.json
    command = data.get('command')
    
    ctrl = {"trading_enabled": True} # Default
    if os.path.exists(CONTROL_FILE):
        with open(CONTROL_FILE, 'r') as f: ctrl = json.load(f)
    
    if command == 'START': ctrl['trading_enabled'] = True
    elif command == 'STOP': ctrl['trading_enabled'] = False
    elif command == 'CLOSE_ALL': ctrl['command'] = 'CLOSE_ALL'
    
    with open(CONTROL_FILE, 'w') as f: json.dump(ctrl, f)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # Pastikan folder data ada biar gak error
    if not os.path.exists('data'): os.makedirs('data')
    
    print("🚀 DASHBOARD SERVER STARTED ON http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')