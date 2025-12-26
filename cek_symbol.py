import MetaTrader5 as mt5
import os
from dotenv import load_dotenv

load_dotenv()

# Ambil kredensial dari .env
login = int(os.getenv("MT5_LOGIN"))
password = os.getenv("MT5_PASSWORD")
server = os.getenv("MT5_SERVER")
path = os.getenv("MT5_PATH")

if not mt5.initialize(path=path):
    print("Gagal init MT5")
    quit()

if not mt5.login(login=login, password=password, server=server):
    print("Gagal login")
    quit()

print(f"✅ Login Sukses ke {server}")
print("🔍 Mencari symbol yang mengandung 'XAU' atau 'GOLD'...")

# Cari semua symbol
symbols = mt5.symbols_get()
found = False

for s in symbols:
    if "XAU" in s.name or "GOLD" in s.name:
        print(f"👉 DITEMUKAN: {s.name}")
        found = True

if not found:
    print("❌ Tidak ada symbol XAU/GOLD. Coba cek Market Watch di aplikasi MT5.")

mt5.shutdown()