import pandas as pd
import pandas_ta as ta
from loguru import logger

class TechnicalBrain:
    def __init__(self):
        logger.info("🧠 TechnicalBrain: M15 Swing Edition")

    def _detect_order_blocks(self, df: pd.DataFrame):
        try:
            if df is None or len(df) < 5: return 0.0, 0.0
            bull_ob = 0.0
            bear_ob = 0.0
            for i in range(len(df)-3, len(df)-20, -1):
                curr = df.iloc[i]
                next_c = df.iloc[i+1]
                next_next = df.iloc[i+2]
                
                if curr['close'] < curr['open']: 
                    if next_c['close'] > next_c['open'] and next_c['close'] > curr['high']: 
                         if next_next['close'] > next_c['high']: bull_ob = curr['low']
                             
                if curr['close'] > curr['open']: 
                    if next_c['close'] < next_c['open'] and next_c['close'] < curr['low']:
                        if next_next['close'] < next_c['low']: bear_ob = curr['high']
            return bull_ob, bear_ob
        except: return 0.0, 0.0

    def analyze_mtf(self, mtf_data: dict):
        try:
            if not mtf_data: return {}
            
            def analyze(df):
                if df is None or df.empty: return {}
                df.columns = [x.lower() for x in df.columns]
                df.ta.ema(length=20, append=True); df.ta.ema(length=50, append=True)
                df.ta.rsi(length=14, append=True); df.ta.adx(length=14, append=True)
                last = df.iloc[-1]
                ema20, ema50 = last.get('EMA_20'), last.get('EMA_50')
                return {
                    "trend": "BULLISH" if ema20 > ema50 else "BEARISH",
                    "rsi": float(last.get('RSI_14', 50)),
                    "adx": float(last.get('ADX_14', 0)),
                    "close": float(last['close'])
                }

            h1_res = analyze(mtf_data.get('H1'))
            m15_res = analyze(mtf_data.get('M15')) # Fokus utama
            
            # Cari OB di M15 (Valid untuk Swing Harian)
            bull_ob, bear_ob = self._detect_order_blocks(mtf_data.get('M15'))
            
            # Sup/Res dari H1 (Lebih Kuat)
            df_h1 = mtf_data.get('H1')
            if df_h1 is not None:
                res = df_h1['high'].tail(50).max()
                sup = df_h1['low'].tail(50).min()
            else: res, sup = 0.0, 0.0

            return {
                "H1": h1_res, "M15": m15_res, "M1": {}, # M1 gak dipake
                "patterns": "Swing Mode",
                "support": float(sup), "resistance": float(res),
                "bullish_ob": float(bull_ob), "bearish_ob": float(bear_ob),
                "current_price": m15_res.get('close', 0.0)
            }
        except Exception as e:
            return {"H1":{}, "M15":{}, "current_price":0.0}