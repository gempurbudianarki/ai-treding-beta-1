import pandas as pd
from loguru import logger

class ConditionBrain:
    def __init__(self):
        logger.info("🧠 ConditionBrain Initialized")

    def analyze(self, df: pd.DataFrame) -> dict:
        """
        Menganalisa kondisi pasar umum (Volatility Check).
        """
        # --- FIX: SAFETY CHECK DATA KOSONG ---
        if df is None or df.empty:
            # logger.warning("ConditionBrain: DataFrame kosong/belum siap.") # Mute biar gak spam log
            return {"tradable": False, "reason": "waiting_data"}

        try:
            # Hitung Volatilitas Sederhana (Range High - Low)
            df['range'] = df['high'] - df['low']
            avg_range = df['range'].rolling(20).mean().iloc[-1]
            current_range = df['range'].iloc[-1]
            
            # Kalau range terlalu kecil (mati suri), jangan trade
            if current_range < (avg_range * 0.2):
                return {"tradable": False, "reason": "market_sleeping"}
            
            # Kalau range terlalu gila (news spike), hati-hati (opsional)
            if current_range > (avg_range * 5.0):
                return {"tradable": True, "reason": "high_volatility_warning"}

            return {"tradable": True, "reason": "ok"}

        except Exception as e:
            logger.error(f"ConditionBrain Error: {e}")
            return {"tradable": False, "reason": "error"}