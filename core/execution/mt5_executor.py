import MetaTrader5 as mt5
from loguru import logger
import time
import math

class MT5Executor:
    """
    MT5 EXECUTOR V5.2: FORCED RECOVERY EDITION
    
    Perbaikan Vital:
    - Menangani anomali dimana kalkulasi margin lokal > lot yang ditolak.
    - Menggunakan logika 'Force Cut 50%' jika matematika tidak sinkron dengan broker.
    - Memastikan order TETAP MASUK berapapun lot-nya (selama > min_lot).
    """
    
    def __init__(self, symbol):
        self.symbol = symbol
        self.magic_number = 998877 
        self.deviation = 20
        logger.info(f"🔫 MT5Executor V5.2 Ready for {symbol}")

    def _get_fill_policy(self):
        """Menentukan Filling Mode yang aman"""
        try:
            symbol_info = mt5.symbol_info(self.symbol)
            if not symbol_info: return mt5.ORDER_FILLING_IOC
            
            filling_modes = symbol_info.filling_mode
            if filling_modes & mt5.SYMBOL_FILLING_FOK:
                return mt5.ORDER_FILLING_FOK
            elif filling_modes & mt5.SYMBOL_FILLING_IOC:
                return mt5.ORDER_FILLING_IOC
            else:
                return mt5.ORDER_FILLING_RETURN
        except:
            return mt5.ORDER_FILLING_IOC

    def _send_order(self, request, max_retries=5):
        """
        Fungsi eksekusi dengan logika survival (bertahan hidup).
        """
        current_retry = 0
        
        while current_retry < max_retries:
            # 1. Kirim Order
            result = mt5.order_send(request)
            
            # --- SKENARIO SUKSES ---
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.success(f"✅ Order Executed: Ticket {result.order} | Vol: {result.volume}")
                return result
            
            # --- SKENARIO MARGIN KURANG (10019 / 10014) ---
            elif result.retcode in [10019, 10014]: 
                rejected_vol = request['volume']
                logger.warning(f"⚠️ Margin Reject for {rejected_vol} Lot. Attempting Recovery...")
                
                acc = mt5.account_info()
                tick = mt5.symbol_info_tick(self.symbol)
                sym = mt5.symbol_info(self.symbol)
                
                if acc and tick and sym:
                    # Ambil spesifikasi lot broker
                    min_lot = sym.volume_min
                    step_lot = sym.volume_step
                    price = tick.ask if request['type'] == mt5.ORDER_TYPE_BUY else tick.bid
                    
                    # Hitung margin untuk lot terkecil
                    margin_min = mt5.order_calc_margin(request['type'], self.symbol, min_lot, price)
                    
                    new_vol = 0.0
                    
                    if margin_min and margin_min > 0:
                        # Hitung kapasitas maksimal berdasarkan 95% free margin
                        max_capacity = (acc.margin_free * 0.95 / margin_min) * min_lot
                        
                        # Rounding ke step terdekat
                        # Rumus: round(value / step) * step
                        new_vol = round(max_capacity / step_lot) * step_lot
                        new_vol = round(new_vol, 2)
                    
                    # --- LOGIKA PENYELAMAT (THE FIX) ---
                    # Jika hitungan baru (new_vol) LEBIH BESAR atau SAMA dengan lot yang ditolak,
                    # Berarti hitungan lokal salah/tidak sinkron. Kita harus PAKSA TURUN.
                    if new_vol >= rejected_vol:
                        logger.warning(f"⚠️ Anomaly: Math says {new_vol} is ok, but Broker rejected {rejected_vol}.")
                        logger.warning(f"⚠️ Action: Forcing 50% Cut.")
                        
                        # Paksa potong setengah dari lot yang ditolak
                        new_vol = rejected_vol * 0.5
                        
                        # Normalisasi lagi ke step lot
                        new_vol = round(new_vol / step_lot) * step_lot
                        new_vol = round(new_vol, 2)

                    # Validasi batas minimum broker
                    if new_vol < min_lot:
                        # Kalau hasil potongan di bawah minimum, coba paksa ke minimum
                        if acc.margin_free > margin_min:
                            new_vol = min_lot
                        else:
                            logger.error(f"❌ Saldo Habis Total. Sisa ${acc.margin_free:.2f}, butuh ${margin_min:.2f}.")
                            return result

                    # --- COBA LAGI ---
                    if new_vol < rejected_vol:
                        logger.info(f"🔄 Retry Immediate: {new_vol} Lot")
                        request['volume'] = new_vol
                        current_retry += 1
                        continue # Langsung loop lagi tanpa delay
                    else:
                        # Safety break jika logic macet
                        logger.error("❌ Recovery Logic Failed (Loop detected).")
                        return result
                
                return result

            # --- SKENARIO REQUOTE (10004) ---
            elif result.retcode == 10004:
                logger.warning("⚠️ Requote detected. Refreshing price...")
                tick = mt5.symbol_info_tick(self.symbol)
                if tick:
                    request['price'] = tick.ask if request['type'] == mt5.ORDER_TYPE_BUY else tick.bid
                time.sleep(0.5)
                current_retry += 1
                continue
                
            # --- ERROR LAINNYA ---
            else:
                logger.error(f"❌ MT5 Reject: {result.retcode} ({result.comment})")
                return result
                
        return None

    def buy_market(self, volume, sl=0.0, tp=0.0, comment="AI Buy"):
        """Wrapper Buy"""
        tick = mt5.symbol_info_tick(self.symbol)
        if not tick: return

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": float(volume),
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "sl": float(sl),
            "tp": float(tp),
            "deviation": self.deviation,
            "magic": self.magic_number,
            "comment": str(comment[:25]),
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": self._get_fill_policy(),
        }
        
        logger.info(f"📝 Sending BUY Order: {volume} Lot...")
        return self._send_order(request)

    def sell_market(self, volume, sl=0.0, tp=0.0, comment="AI Sell"):
        """Wrapper Sell"""
        tick = mt5.symbol_info_tick(self.symbol)
        if not tick: return

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": float(volume),
            "type": mt5.ORDER_TYPE_SELL,
            "price": tick.bid,
            "sl": float(sl),
            "tp": float(tp),
            "deviation": self.deviation,
            "magic": self.magic_number,
            "comment": str(comment[:25]),
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": self._get_fill_policy(),
        }
        
        logger.info(f"📝 Sending SELL Order: {volume} Lot...")
        return self._send_order(request)

    def close_position(self, ticket, volume, order_type, comment="AI Close"):
        """Wrapper Close"""
        tick = mt5.symbol_info_tick(self.symbol)
        if not tick: return
        
        close_type = mt5.ORDER_TYPE_SELL if order_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        close_price = tick.bid if close_type == mt5.ORDER_TYPE_SELL else tick.ask
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": float(volume),
            "type": close_type,
            "position": ticket,
            "price": close_price,
            "deviation": self.deviation,
            "magic": self.magic_number,
            "comment": str(comment[:25]),
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": self._get_fill_policy(),
        }
        
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.success(f"🏁 Closed Position {ticket} | Vol: {volume}")
        else:
            logger.error(f"Failed to Close {ticket}: {result.retcode}")

    def modify_position(self, ticket, sl, tp):
        """Wrapper Modify"""
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "sl": float(sl),
            "tp": float(tp)
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            if result.retcode != 10025:
                logger.error(f"Modify Failed Ticket {ticket}: {result.retcode}")