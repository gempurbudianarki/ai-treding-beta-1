import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load .env biar baca API Key lo
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ API KEY GAK KEBACA! Cek file .env lo bro.")
else:
    print(f"✅ API Key Terdeteksi: {api_key[:10]}...")
    genai.configure(api_key=api_key)

    print("\n=== MENGECEK MODEL YANG TERSEDIA BUAT AKUN LO ===")
    try:
        found = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
                found = True
        
        if not found:
            print("⚠️ Tidak ada model yang tersedia. Mungkin API Key belum aktif?")
            
    except Exception as e:
        print(f"❌ Error Koneksi ke Google: {e}")