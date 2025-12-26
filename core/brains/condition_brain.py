import pandas as pd
from datetime import datetime
import pytz
from loguru import logger

class ConditionBrain:
    """
    CONDITION BRAIN V4.0: THE GATEKEEPER
    
    Tugas Utama:
    1. TIME FILTER: Memastikan bot hanya trading di jam Liquid (London & New York).
       - Mencegah trading di Asian Session (Spread lebar, gerakan semu).
    2. VOLATILITY FILTER: Mencegah trading saat market mati suri (Low Volatility).
    """
    
    def __init__(self):
        # --- KONFIGURASI JAM KERJA (WIB / GMT+7) ---
        # Jam mulai: 13:00 WIB (Pre-London)
        # Jam selesai: 01:00 WIB (Pertengahan New York, sebelum swap/sepi)
        self.start_hour = 13
        self.end_hour = 1 
        self.timezone = pytz.timezone('Asia/Jakarta')
        
        logger.info(f"🧠 ConditionBrain Initialized | Active Hours: {self.start_hour}:00 - {self.end_hour}:00 WIB")

    def _check_operating_hours(self):
        """
        Mengecek apakah waktu sekarang masuk dalam 'Office Hours' trading.
        """
        try:
            now = datetime.now(self.timezone)
            current_hour = now.hour
            
            is_active = False
            
            # Logika Lintas Hari (Start > End, misal 13:00 - 01:00)
            if self.start_hour > self.end_hour:
                if current_hour >= self.start_hour or current_hour < self.end_hour:
                    is_active = True
            # Logika Satu Hari (Start < End, misal 08:00 - 17:00)
            else:
                if self.start_hour <= current_hour < self.end_hour:
                    is_active = True
            
            if is_active:
                return True, "Market Open (Liquid Session)"
            else:
                return False, f"Sleep Mode (Hours: {self.start_hour}-0{self.end_hour} WIB)"
                
        except Exception as e:
            logger.error(f"Time Check Error: {e}")
            # Jika error waktu, default ke True (Fail-Open) atau False (Fail-Safe)
            # Kita pilih True biar gak macet, tapi log error
            return True, "Time Check Error (Bypassed)"

    def analyze(self, df: pd.DataFrame) -> dict:
        """
        Analisa Komprehensif: Waktu + Volatilitas Dataframe.
        """
        
        # --- 1. CEK WAKTU DULU (PRIORITAS UTAMA) ---
        is_time_ok, time_msg = self._check_operating_hours()
        
        if not is_time_ok:
            return {
                "allowed": False,
                "reason": time_msg
            }

        # --- 2. CEK KELENGKAPAN DATA ---
        if df is None or df.empty:
            return {
                "allowed": False, 
                "reason": "Waiting for Data..."
            }

        # --- 3. CEK VOLATILITAS (JANGAN TRADE DI MARKET MATI) ---
        try:
            # Hitung Range (High - Low)
            # Kita gunakan copy biar gak ngerusak df asli
            df_calc = df.copy()
            df_calc['range'] = df_calc['high'] - df_calc['low']
            
            # Rata-rata range 20 candle terakhir
            avg_range = df_calc['range'].rolling(20).mean().iloc[-1]
            current_range = df_calc['range'].iloc[-1]
            
            # Ambang Batas Volatilitas
            # Jika range sekarang < 20% dari rata-rata -> Market Mati Suri
            if current_range < (avg_range * 0.2):
                return {
                    "allowed": False, 
                    "reason": "Low Volatility (Dead Market)"
                }
            
            # Jika range sekarang > 500% rata-rata -> News Spike / Bahaya
            # (Opsional: Bisa di-disable kalau suka news trading)
            if current_range > (avg_range * 5.0):
                return {
                    "allowed": True, 
                    "reason": "High Volatility Warning"
                }

            return {
                "allowed": True, 
                "reason": "Market Healthy"
            }

        except Exception as e:
            logger.error(f"Volatility Check Error: {e}")
            return {"allowed": True, "reason": "Vol Check Skipped"}