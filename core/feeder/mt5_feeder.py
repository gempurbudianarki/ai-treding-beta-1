import MetaTrader5 as mt5
import pandas as pd
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
        if not mt5.initialize(path=path):
            logger.error(f"Gagal init MT5: {mt5.last_error()}")
            return False
        
        # Login (Opsional jika sudah auto-login)
        login = settings.MT5_LOGIN
        password = settings.MT5_PASSWORD
        server = settings.MT5_SERVER
        
        if login and password and server:
            authorized = mt5.login(login=login, password=password, server=server)
            if not authorized:
                logger.error(f"Gagal login MT5: {mt5.last_error()}")
                return False
        
        # Select Symbol
        if not mt5.symbol_select(self.symbol, True):
            logger.error(f"Gagal select symbol {self.symbol}: {mt5.last_error()}")
            return False
            
        self.connected = True
        logger.info(f"MT5 Connected. Symbol: {self.symbol}")
        return True

    def get_history(self, timeframe_code, bars=200) -> pd.DataFrame:
        """
        Mengambil data history fleksibel berdasarkan timeframe yang diminta.
        """
        rates = mt5.copy_rates_from_pos(self.symbol, timeframe_code, 0, bars)
        if rates is None or len(rates) == 0:
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
        FITUR BARU: Ambil data M1, M15, dan H1 sekaligus.
        """
        data = {}
        # Data Jangka Pendek (Eksekusi)
        data['M1'] = self.get_history(mt5.TIMEFRAME_M1, bars=100)
        # Data Jangka Menengah (Trend)
        data['M15'] = self.get_history(mt5.TIMEFRAME_M15, bars=100)
        # Data Jangka Panjang (Trend Besar)
        data['H1'] = self.get_history(mt5.TIMEFRAME_H1, bars=100)
        
        return data