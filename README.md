
<div align="center">

# ⚡ **NEON QUANT V17**
### *AI Autonomous Trading System | XAUUSD & BTCUSDT*

<img src="https://img.shields.io/badge/VERSION-V17_STABLE-00f0ff?style=for-the-badge&logo=appveyor"/>
<img src="https://img.shields.io/badge/STATUS-ACTIVE-00ff9d?style=for-the-badge&logo=statuspage"/>
<img src="https://img.shields.io/badge/PLATFORM-METATRADER_5-orange?style=for-the-badge&logo=metatrader"/>
<img src="https://img.shields.io/badge/RISK-SMART_ADAPTIVE-ff003c?style=for-the-badge&logo=security"/>

---

### **🔥 NEXT-GEN ALGO TRADING FRAMEWORK**
### **"BUILT LIKE A MINI HEDGE FUND TRADING DESK"**

```text
╔███╗   ██╗███████╗ ██████╗ ███╗   ██╗     ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗
██╔██╗  ██║██╔════╝██╔═══██╗████╗  ██║    ██╔═══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝
██║╚██╗ ██║█████╗  ██║   ██║██╔██╗ ██║    ██║   ██║██║   ██║███████║██╔██╗ ██║   ██║   
██║ ╚██╗██║██╔══╝  ██║   ██║██║╚██╗██║    ██║   ██║██║   ██║██╔══██║██║╚██╗██║   ██║   
╚██╗ ╚████║███████╗╚██████╔╝██║ ╚████║    ╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║   
 ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝     ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   

```

<p align="center">
<i>Powered by Multi-Agent Consensus: DeepSeek V3 + Qwen 2.5 + Gemini Flash 2.0</i>
</p>

</div>

---

# 🚀 **EXECUTIVE SUMMARY**

**NEON QUANT V17** bukan sekadar bot trading biasa. Ini adalah **Autonomous Financial System** yang dirancang untuk meniru cara kerja *trading desk* institusional.

Sistem ini tidak bergantung pada satu indikator, melainkan menggunakan **"AI Council Debate"** (Debat Dewan AI) di mana beberapa model AI dengan kepribadian berbeda berdiskusi sebelum mengambil keputusan eksekusi.

### **🌟 Key Features:**

* **Multi-Model Intelligence:** Menggabungkan logika SMC, Price Action, dan Risk Management.
* **Time-Aware:** Otomatis "Tidur" saat market sepi (Asian Session) dan "Berburu" saat liquid (London/NY).
* **Self-Healing:** Fitur *Instant Recovery* jika order ditolak broker karena margin.
* **Blackbox Logging:** Mencatat setiap alasan keputusan ke dalam Jurnal JSON yang bisa diaudit.

> **“Trade like an Algorithm. Think like an Institution.”**

---

# 🧠 **THE AI BRAIN ARCHITECTURE**

Sistem ini menggunakan topologi **Tri-Layer Consensus**:

### ⚔️ **1. THE STRATEGIST (Qwen 2.5)**

* **Role:** Market Sniper & Alpha Seeker.
* **Tugas:** Membaca struktur pasar (SMC), mencari Order Block, dan mendeteksi momentum M15/H1.
* **Output:** Proposal Entry (Buy/Sell) beserta TP & SL.

### 🛡️ **2. THE RISK GOVERNOR (DeepSeek V3)**

* **Role:** Risk Manager & Gatekeeper.
* **Tugas:** Mengaudit proposal Strategist. Menghitung Drawdown harian, mengecek RSI extremum, dan memvalidasi tren H1.
* **Power:** Memiliki hak **VETO** mutlak untuk membatalkan trade berbahaya.

### 📚 **3. THE HISTORIAN (Gemini Flash 2.0)**

* **Role:** Evaluation & Learning.
* **Tugas:** Menganalisa hasil trade pasca-eksekusi, menyimpan *lesson learned*, dan menyempurnakan prompt di masa depan.

---

# 🛡️ **ADVANCED SAFETY SYSTEMS**

Sistem keamanan berlapis untuk melindungi modal:

1. **Smart Wallet Awareness (V5.2)**
* Menghitung lot berdasarkan saldo *real-time*.
* Jika margin kurang, melakukan *Forced Downgrade* (memotong lot otomatis) agar trade tetap masuk.


2. **Office Hours Protocol**
* Hanya trading di jam 13:00 WIB s/d 01:00 WIB.
* Menghindari spread lebar dan *fake moves* di pagi buta.


3. **Daily Drawdown Circuit Breaker**
* Otomatis mematikan sistem jika kerugian harian menyentuh **3%** (Configurable).



---

# ⚙️ **INSTALLATION GUIDE**

Ikuti langkah ini dengan teliti agar sistem berjalan sempurna.

### **1️⃣ Clone Repository**

Download source code ke komputer lokal Anda.

```bash
git clone [https://github.com/gempurbudianarki/ai-treding-beta-1.git](https://github.com/gempurbudianarki/ai-treding-beta-1.git)
cd ai-treding-beta-1

```

### **2️⃣ Create Virtual Environment (PENTING!)**

Kita buat ruang isolasi agar library tidak berantakan.

**Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate

```

**Mac / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate

```

*(Tanda berhasil: Di terminal muncul tulisan `(venv)` di sebelah kiri)*

### **3️⃣ Install Dependencies**

Install semua "otak" dan "saraf" sistem.

```bash
pip install -r requirements.txt

```

### **4️⃣ Configure Environment**

Duplikasi file `.env.example`, ubah namanya menjadi `.env`, dan isi data Anda:

```ini
# MT5 CREDENTIALS
MT5_LOGIN=12345678
MT5_PASSWORD="password_broker_anda"
MT5_SERVER="Exness-MT5Trial"

# AI API KEYS
GOOGLE_API_KEY="AIzaSy..."
OPENAI_API_KEY="sk-..."

# TRADING SETTINGS
SYMBOL="XAUUSDm"
RISK_PER_TRADE_PCT=1.0
MAX_DAILY_DRAWDOWN_PCT=3.0

```

### **5️⃣ Launch The System**

Buka **2 Terminal** (pastikan venv aktif di keduanya):

**Terminal 1: Menjalankan Otak Trading (Backend)**

```bash
python -m core.main_loop

```

**Terminal 2: Menjalankan Dashboard (Frontend)**

```bash
python -m dashboard.app

```

Akses Dashboard di Browser:
👉 **http://localhost:5000**

---

# 🖥️ **DASHBOARD PREVIEW**

Dashboard **NEON QUANT** dirancang dengan estetika Cyberpunk untuk monitoring maksimal:

| Feature | Description |
| --- | --- |
| **Tactical Monitor** | Grafik TradingView real-time + Panel Sinyal AI. |
| **Probability Meter** | Menghitung Win Rate dari 100 trade terakhir secara live. |
| **The Consensus Log** | Chatroom transparan dimana Anda bisa membaca debat antara AI. |
| **Memory Bank** | Arsip pembelajaran AI dari kemenangan dan kekalahan masa lalu. |

---

# 📁 **PROJECT STRUCTURE**

```
NEON-QUANT-V17/
│
├── ai_api/                 # Modul komunikasi ke LLM (Gemini/OpenAI)
├── core/
│   ├── brains/             # Otak Analisa (Technical, Condition, Sentiment)
│   ├── execution/          # Eksekutor Order MT5 (Instant Recovery logic)
│   ├── orchestrator/       # Dirigen Utama (Pengambil Keputusan)
│   ├── risk/               # Manajemen Risiko & Keuangan
│   └── main_loop.py        # Jantung Sistem
│
├── dashboard/              # Web Interface (Flask + Tailwind + AlpineJS)
├── data/                   # Database JSON (Logs, History, Status)
├── .env                    # Konfigurasi Rahasia
├── .gitignore              # Keamanan Repository
└── requirements.txt        # Daftar Pustaka

```

---

# ⚠️ **DISCLAIMER & WARNING**

> **Algorithmic Trading involves significant risk.**
> Sistem ini adalah alat bantu keputusan, bukan jaminan kekayaan instan.
> 1. Gunakan di **DEMO ACCOUNT** minimal 2 minggu.
> 2. Penulis tidak bertanggung jawab atas kerugian finansial yang terjadi.
> 3. Pastikan VPS/PC Anda memiliki koneksi internet stabil (Latency < 200ms).
> 
> 

---

<div align="center">

### **DEVELOPED BY GEMPUR BUDI ANARKI**

#### *“Forging the Future of Quant Finance.”*

</div>