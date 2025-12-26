import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime
from loguru import logger
from core.config import settings

class MT5Feeder:
    def __init__(self):
        self.symbol = settings.SYMBOL
        self.timeframe = settings.TIMEFRAME_MINUTES
        self.connected = False

    def initialize(self) -> bool:
        path = settings.MT5_PATH
        # Coba init dengan path khusus
        if not mt5.initialize(path=path):
            logger.error(f"Gagal init MT5 (Path: {path}): {mt5.last_error()}")
            # Fallback: Coba init tanpa path (siapa tau sudah di path environment)
            if not mt5.initialize():
                logger.critical(f"FATAL: MT5 Init Failed Total.")
                return False
        
        # Login (Opsional jika sudah auto-login di terminal)
        login = settings.MT5_LOGIN
        password = settings.MT5_PASSWORD
        server = settings.MT5_SERVER
        
        if login and password and server:
            authorized = mt5.login(login=login, password=password, server=server)
            if not authorized:
                logger.error(f"Gagal login MT5: {mt5.last_error()}")
                return False
        
        # Select Symbol (PENTING: Pastikan masuk Market Watch)
        if not mt5.symbol_select(self.symbol, True):
            logger.error(f"Gagal select symbol {self.symbol}. Cek ejaan!")
            return False
            
        self.connected = True
        logger.info(f"✅ MT5 Connected. Symbol: {self.symbol}")
        return True

    def get_history(self, timeframe_code, bars=500) -> pd.DataFrame:
        """
        Mengambil data history. 
        UPGRADE: Default bars dinaikkan ke 500 agar EMA200 bisa dihitung.
        """
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe_code, 0, bars)
        
        # Retry Logic sederhana kalau data kosong (kadang MT5 belum sync)
        if rates is None or len(rates) == 0:
            time.sleep(0.5)
            rates = mt5.copy_rates_from_pos(self.symbol, timeframe_code, 0, bars)
            
        if rates is None or len(rates) == 0:
            logger.warning(f"⚠️ Data kosong untuk {self.symbol}")
            return pd.DataFrame()
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def get_tick_info(self):
        tick = mt5.symbol_info_tick(self.symbol)
        if tick:
            return {'bid': tick.bid, 'ask': tick.ask, 'time': tick.time}
        return None
        
    def get_mtf_data(self):
        """
        Ambil data Multi-Timeframe untuk analisis SNIPER.
        """
        data = {}
        # M1: Untuk eksekusi presisi (opsional, tapi bagus ada)
        data['M1'] = self.get_history(mt5.TIMEFRAME_M1, bars=200)
        
        # M15: Timeframe Utama (Signal & Momentum)
        # Butuh 500 bar untuk EMA 200 yang akurat
        data['M15'] = self.get_history(mt5.TIMEFRAME_M15, bars=500)
        
        # H1: Timeframe Tren (Big Picture)
        data['H1'] = self.get_history(mt5.TIMEFRAME_H1, bars=500)
        
        return data