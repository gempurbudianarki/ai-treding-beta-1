<div align="center">

# ⚡ **NEON QUANT V17**  
### *AI Autonomous Trading System for XAUUSD / BTCUSDT*

<img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge"/>
<img src="https://img.shields.io/badge/AI_Models-DeepSeek_V3_|_Qwen_2.5_|_Gemini_Flash_2.0-blue?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Platform-MetaTrader_5-orange?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Risk-Smart_Adaptive-red?style=for-the-badge"/>

---

### **🔥 NEXT-GEN ALGO TRADING FRAMEWORK**
### **BUILT LIKE A MINI HEDGE FUND TRADING DESK**

```
╔███╗   ██╗███████╗ ██████╗ ███╗   ██╗     ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗
██╔██╗  ██║██╔════╝██╔═══██╗████╗  ██║    ██╔═══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝
██║╚██╗ ██║█████╗  ██║   ██║██╔██╗ ██║    ██║   ██║██║   ██║███████║██╔██╗ ██║   ██║   
██║ ╚██╗██║██╔══╝  ██║   ██║██║╚██╗██║    ██║   ██║██║   ██║██╔══██║██║╚██╗██║   ██║   
╚██╗ ╚████║███████╗╚██████╔╝██║ ╚████║    ╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║   
 ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝     ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   
```

</div>

---

# 🚀 **EXECUTIVE SUMMARY**

**NEON QUANT V17** bukan bot trading biasa.  
Ini adalah **sistem otonom** yang bekerja seperti **HFT / Hedge Fund MINI**:

✔ Multi-model AI Decision Engine  
✔ Debat AI sebelum eksekusi trade  
✔ Dashboard real-time ala monitor Terminal  
✔ Auto-Risk Management + Self-Learning Journal  
✔ MT5 Live Feed (REAL MARKET – NO DELAY)

> **“Trade like an Algorithm. Think like an Institution.”**

---

# 🧠 **THE AI BRAIN ARCHITECTURE**

Sistem ini memakai metode **AI Council Debate**:

## ⚔️ 1. Qwen 2.5 — *“The Market Sniper”*
- Membaca struktur market (SMC)
- Deteksi momentum & candle pattern
- Mengusulkan BUY/SELL + alasan logis  

## 🦾 2. DeepSeek V3 — *“The Risk Commander”*
- Mengaudit proposal Qwen  
- Mengecek spread, volatilitas, drawdown  
- Bisa **VETO** trade jika berbahaya  

## 📚 3. Gemini — *“The Historian”*
- Membandingkan pola dengan *history losses*
- Menolak setup yang pernah bikin MC  
- Menyimpan “lesson learned” otomatis

💡 **Trade hanya dieksekusi jika semua AI sepakat.**  
💡 Jika tidak → *HOLD*.

---

# 🛡️ **ADVANCED RISK GOVERNOR**

### ✔ Dynamic Lot Sizing  
Lot dihitung dari persentase equity → anti MC.

### ✔ Anti-Stacking Engine  
Cegah open posisi beruntun di area sama.

### ✔ Daily Drawdown Limit  
Jika kerugian harian menyentuh angka tertentu → AI auto-pause.

### ✔ Smart Trailing System  
Trailing otomatis berdasarkan volatilitas realtime.

---

# 🖥️ **THE COMMAND CENTER DASHBOARD**

### 🟦 **Tab 1 — LIVE MONITOR**
- Candlestick real-time dari MetaTrader 5  
- Live Wallet: Balance, Equity, Floating PnL  
- Tabel posisi → warna dinamis, auto blink  
- AI Chat Stream (lihat debat AI real-time)  
- START / STOP / CLOSE-ALL dengan animasi pulse  

### 🟪 **Tab 2 — AI MEMORY**
- Semua jurnal kemenangan & kekalahan  
- Evaluasi otomatis dari Gemini  
- Lesson Learned per trade  
- “AI yang beneran belajar”, bukan bot statis  

### 🟧 **Tab 3 — TRADE HISTORY**
- Riwayat transaksi lengkap  
- Profit/Loss berwarna  
- Ringkas dan mudah dibaca  

---

# ⚙️ **INSTALLATION**

## 1️⃣ Clone Repository
```bash
git clone https://github.com/gempurbudianarki/ai-treding-beta-1.git
cd ai-treding-beta-1
```

## 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

## 3️⃣ Setup `.env`
```ini
MT5_LOGIN=12345678
MT5_PASSWORD="password"
MT5_SERVER="Exness-MT5Trial"

DEEPSEEK_API_KEY="sk-xxx"
MEGALLM_API_KEY="sk-xxx"
TRADING_MODE="SCALPING_M1"
```

## 4️⃣ Run the System

### Terminal 1 — BOT ENGINE
```bash
python -m core.main_loop
```

### Terminal 2 — DASHBOARD
```bash
python -m dashboard.app
```

Akses dashboard:  
👉 **http://localhost:5000**

---

# 📁 **FOLDER STRUCTURE**

```
ai-treding-beta-1/
│
├── ai_api/               # Multi-LLM Engine (Qwen, DeepSeek, Gemini)
├── core/
│   ├── brains/           # Technical, Sentiment, Evaluation, Condition
│   ├── execution/        # Order Execution to MT5
│   ├── feeder/           # Price Feed & General Data Fetching
│   ├── orchestrator/     # AI Council Logic
│   ├── risk/             # Risk Manager
│   ├── config.py         # Global Configuration (Pydantic)
│   └── main_loop.py      # AI Loop Heartbeat
│
├── dashboard/            # Full Web UI (Tailwind + Alpine)
├── data/                 # JSON Logs: history, memory, status
├── requirements.txt
└── .env.example
```

---

# ⚠️ DISCLAIMER

Trading itu **high-risk**.  
Bot ini membantu analisa & eksekusi, tapi **tidak menjamin profit**.  
Uji dulu di **Demo Account** sebelum real.  
Gunakan dengan tanggung jawab penuh.

---

<div align="center">

### **DEVELOPED BY GEMPUR BUDI ANARKI**  
#### *“The Future of Algorithmic Trading with Multi-Agent AI.”*

</div>
