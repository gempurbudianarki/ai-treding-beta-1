import pandas as pd
import pandas_ta as ta
from loguru import logger

class TechnicalBrain:
    """
    TECHNICAL BRAIN V3.5: FULL DIAGNOSTIC & SMC SCANNER
    
    Fitur:
    1. Order Block Detection (SMC): Mencari zona Supply & Demand dari 50 candle ke belakang.
    2. Multi-Timeframe (MTF): Menggabungkan Tren H1 dan Eksekusi M15.
    3. Momentum Booster: Logika khusus untuk market sesi Asia yang low-volatility.
    4. Diagnostic Logging: Memberi alasan detail kenapa NO TRADE.
    """
    
    def __init__(self):
        logger.info("🧠 TechnicalBrain: Diagnostic Mode Active (Full Analysis)")

    def _detect_order_blocks(self, df: pd.DataFrame):
        """
        Logika Deteksi Smart Money Concepts (SMC) Order Blocks.
        Mencari candle terakhir sebelum pergerakan impulsif.
        """
        try:
            if df is None or len(df) < 5: 
                return 0.0, 0.0
            
            bull_ob = 0.0
            bear_ob = 0.0
            
            # Loop mundur dari candle terbaru (index -3) sampai 50 candle ke belakang
            # Kita skip 2 candle terakhir karena mungkin belum close sempurna
            for i in range(len(df)-3, len(df)-50, -1):
                curr = df.iloc[i]     # Candle yang dicek
                next_c = df.iloc[i+1] # Candle setelahnya (konfirmasi)
                
                # --- DETEKSI BULLISH OB (Demand Zone) ---
                # Definisi: Candle Merah (Bearish) terakhir sebelum kenaikan kuat
                if curr['close'] < curr['open']: # Candle Merah
                    # Konfirmasi: Candle depannya Hijau & Close-nya menembus High candle merah
                    if next_c['close'] > curr['high']: 
                        bull_ob = curr['low'] # Low candle merah jadi support kuat
                             
                # --- DETEKSI BEARISH OB (Supply Zone) ---
                # Definisi: Candle Hijau (Bullish) terakhir sebelum penurunan kuat
                if curr['close'] > curr['open']: # Candle Hijau
                    # Konfirmasi: Candle depannya Merah & Close-nya menembus Low candle hijau
                    if next_c['close'] < curr['low']: 
                        bear_ob = curr['high'] # High candle hijau jadi resistance kuat
                            
            return bull_ob, bear_ob
            
        except Exception as e:
            logger.error(f"Error detecting Order Blocks: {e}")
            return 0.0, 0.0

    def analyze_mtf(self, mtf_data: dict):
        """
        Fungsi Utama: Menganalisis Data H1 dan M15 secara bersamaan.
        """
        try:
            if not mtf_data: return {}
            
            # --- FUNGSI HELPER: ANALISA SATU DATAFRAME ---
            def analyze(df):
                if df is None or df.empty: return {}
                
                # 1. Normalisasi Header
                df.columns = [x.lower() for x in df.columns]
                
                # 2. Hitung Indikator (Pandas TA)
                # Trend
                df.ta.ema(length=20, append=True)
                df.ta.ema(length=50, append=True)
                df.ta.ema(length=200, append=True)
                
                # Momentum & Volatilitas
                df.ta.rsi(length=14, append=True)
                df.ta.adx(length=14, append=True)
                df.ta.macd(fast=12, slow=26, signal=9, append=True)
                
                # Ambil data candle terakhir dan sebelumnya
                last = df.iloc[-1]
                prev = df.iloc[-2]
                
                # 3. Logika Trend (EMA Structure)
                trend_status = "SIDEWAYS"
                ema50 = last.get('EMA_50', 0)
                if last['close'] > ema50: 
                    trend_status = "BULLISH"
                elif last['close'] < ema50: 
                    trend_status = "BEARISH"
                
                # 4. Logika Momentum (MACD Histogram Acceleration)
                macd_hist = last.get('MACDh_12_26_9', 0)
                prev_hist = prev.get('MACDh_12_26_9', 0)
                
                momentum = "NEUTRAL"
                if macd_hist > prev_hist and macd_hist > 0: momentum = "BULLISH_ACCEL" # Hijau Membesar
                elif macd_hist < prev_hist and macd_hist < 0: momentum = "BEARISH_ACCEL" # Merah Membesar

                return {
                    "trend": trend_status,
                    "momentum": momentum,
                    "rsi": float(last.get('RSI_14', 50)),
                    "adx": float(last.get('ADX_14', 0)),
                    "close": float(last['close'])
                }

            # --- EKSEKUSI ANALISA ---
            h1 = analyze(mtf_data.get('H1'))
            m15 = analyze(mtf_data.get('M15'))
            
            # Data Harga saat ini & SMC Zones dari M15
            current_price = m15.get('close', 0.0)
            bull_ob, bear_ob = self._detect_order_blocks(mtf_data.get('M15'))
            
            # --- LOGIKA KEPUTUSAN (SNIPER + MOMENTUM BOOSTER) ---
            pattern = "None"
            debug_reason = "Scanning..."
            
            # Cek Trend Besar (H1)
            is_bull_trend = "BULLISH" in h1.get('trend', '')
            is_bear_trend = "BEARISH" in h1.get('trend', '')
            
            # Ambil Data Indikator M15
            rsi_val = m15.get('rsi')
            mom_val = m15.get('momentum')
            
            # Toleransi Jarak ke Order Block (0.15%)
            ob_tolerance = current_price * 0.0015
            dist_to_bull = abs(current_price - bull_ob) if bull_ob else 9999
            dist_to_bear = abs(current_price - bear_ob) if bear_ob else 9999
            
            # === LOGIKA BUY (LONG) ===
            if is_bull_trend:
                # Sinyal Valid Jika:
                # 1. Momentum M15 Bullish Kuat (ACCEL)
                # 2. ATAU Momentum Netral TAPI RSI Sehat (45-68) dan Harga dekat Support/OB
                
                is_mom_strong = (mom_val == "BULLISH_ACCEL")
                is_rsi_healthy = (45 <= rsi_val <= 68)
                is_near_ob = (dist_to_bull < ob_tolerance)
                
                # Momentum Booster: Jika RSI sehat + Momentum Netral, kita anggap drift entry
                trigger_buy = is_mom_strong or (is_rsi_healthy and (mom_val == "NEUTRAL" or is_near_ob))
                
                if trigger_buy:
                    if rsi_val < 70: # Filter Overbought
                        pattern = "SNIPER_BUY"
                    else:
                        debug_reason = f"Bullish Trend but RSI Overbought ({rsi_val:.1f})"
                else:
                    debug_reason = f"Bullish Trend but Weak Momentum (RSI: {rsi_val:.1f})"
            
            # === LOGIKA SELL (SHORT) ===
            elif is_bear_trend:
                # Sinyal Valid Jika:
                # 1. Momentum M15 Bearish Kuat (ACCEL)
                # 2. ATAU Momentum Netral TAPI RSI Sehat (32-55) dan Harga dekat Resist/OB
                
                is_mom_strong = (mom_val == "BEARISH_ACCEL")
                is_rsi_healthy = (32 <= rsi_val <= 55)
                is_near_ob = (dist_to_bear < ob_tolerance)
                
                # Momentum Booster
                trigger_sell = is_mom_strong or (is_rsi_healthy and (mom_val == "NEUTRAL" or is_near_ob))
                
                if trigger_sell:
                    if rsi_val > 30: # Filter Oversold
                        pattern = "SNIPER_SELL"
                    else:
                        debug_reason = f"Bearish Trend but RSI Oversold ({rsi_val:.1f})"
                else:
                    debug_reason = f"Bearish Trend but Weak Momentum (RSI: {rsi_val:.1f})"
            
            else:
                debug_reason = f"Market Sideways (H1 Trend: {h1.get('trend')})"

            # --- DIAGNOSTIC LOGGING ---
            # Jika tidak ada trade, beri tahu user alasannya (Hanya log info ringkas)
            if pattern == "None":
                log_msg = (
                    f"🔍 SCAN: {h1.get('trend')} | "
                    f"M15 Mom: {mom_val} | "
                    f"RSI: {rsi_val:.1f} | "
                    f"Msg: {debug_reason}"
                )
                logger.info(log_msg)

            # Return Hasil Lengkap
            return {
                "H1": h1, 
                "M15": m15, 
                "patterns": pattern, 
                "bullish_ob": float(bull_ob), 
                "bearish_ob": float(bear_ob),
                "current_price": current_price
            }
            
        except Exception as e:
            logger.error(f"Analysis Failed: {e}")
            return {"H1":{}, "M15":{}, "current_price":0.0, "patterns": "None"}
        