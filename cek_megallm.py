import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load konfigurasi dari .env
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY") # Kita pake variabel ini buat nyimpen key MegaLLM tadi
base_url = os.getenv("DEEPSEEK_BASE_URL")

print("="*40)
print("🕵️‍♂️ MEGALLM ACCESS CHECKER")
print("="*40)
print(f"📡 Server  : {base_url}")
print(f"🔑 API Key : {api_key[:15]}... (Terbaca)")
print("-" * 40)

if not api_key or not base_url:
    print("❌ ERROR: API Key atau Base URL belum diisi di .env!")
    exit()

try:
    # 2. Inisialisasi Client
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # 3. Minta Daftar Model
    print("⏳ Sedang menghubungi server MegaLLM...")
    models = client.models.list()
    
    print("\n✅ KONEKSI BERHASIL! Akses Diterima.")
    print("📋 Daftar Model yang Tersedia buat Akun Lo:")
    
    available_models = []
    for m in models.data:
        print(f"   - {m.id}")
        available_models.append(m.id)
        
    print("-" * 40)
    print("💡 SARAN:")
    if "gpt-4o-mini" in available_models:
        print("✅ 'gpt-4o-mini' tersedia! Pake ini di .env biar hemat/gratis.")
    elif "deepseek-chat" in available_models:
        print("✅ 'deepseek-chat' tersedia! Gas pake ini kalau bisa.")
    else:
        print("⚠️ Pilih salah satu model di atas dan update file .env bagian DEEPSEEK_MODEL")

except Exception as e:
    print(f"\n❌ KONEKSI GAGAL: {e}")
    print("\nKemungkinan Penyebab:")
    print("1. API Key salah.")
    print("2. Server MegaLLM lagi down.")
    print("3. Koneksi internet diblokir (perlu VPN/DNS).")