import re
from typing import Optional
import MetaTrader5 as mt5
from loguru import logger
from config.settings import settings

class MT5Executor:
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.dry_run = settings.DRY_RUN

    def _clean_comment(self, text: str) -> str:
        if not text: return ""
        text = str(text).replace("\n", " ").replace("\r", " ").replace("\t", " ")
        cleaned = re.sub(r'[^a-zA-Z0-9 \.,-]', '', text)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned[:20].strip() # Kita perpendek jadi 20 char biar aman

    def _send_order(self, request: dict) -> bool:
        """
        Internal helper sakti: Kalau gagal karena komen, retry tanpa komen.
        """
        # 1. Sanitasi dulu
        if "comment" in request:
            request["comment"] = self._clean_comment(request["comment"])
            
        logger.debug(f"📝 Sending: {request.get('action')} | Comment: '{request.get('comment')}'")

        if self.dry_run:
            logger.info(f"[DRY_RUN] Request: {request}")
            return True

        # === PERCOBAAN PERTAMA (DENGAN KOMEN) ===
        result = mt5.order_send(request)

        # Cek jika GAGAL di level Library (Return None)
        if result is None:
            err_code, err_msg = mt5.last_error()
            # Kalau errornya soal "comment" atau generic error (-2)
            if "comment" in str(err_msg).lower() or err_code == -2:
                logger.warning(f"⚠️ MT5 menolak komentar. Retrying TANPA komentar...")
                
                # === PERCOBAAN KEDUA (TANPA KOMEN) ===
                request["comment"] = "" # Hapus komen
                result = mt5.order_send(request) # Kirim ulang
            else:
                # Error lain (misal koneksi putus), laporin aja
                logger.error(f"MT5 Order Failed: {err_code}, {err_msg}")
                return False

        # Cek jika GAGAL di level Server Broker (Retcode != Done)
        if result is None: # Masih None setelah retry?
            logger.error(f"MT5 Retry Failed: {mt5.last_error()}")
            return False

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            if result.retcode == 10009: # 10009 = Done (Placed)
                logger.info(f"✅ Order OK (10009): Ticket {result.order}")
                return True
                
            logger.error(f"❌ MT5 Server Reject: {result.retcode} ({result.comment})")
            return False

        logger.success(f"✅ Order Executed: Ticket {result.order}")
        return True

    def buy_market(self, lot: float, sl: float, tp: float, reason: str) -> bool:
        price = mt5.symbol_info_tick(self.symbol).ask
        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": float(sl),
            "tp": float(tp),
            "deviation": 20,
            "magic": 123456,
            "comment": reason,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        return self._send_order(req)

    def sell_market(self, lot: float, sl: float, tp: float, reason: str) -> bool:
        price = mt5.symbol_info_tick(self.symbol).bid
        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": float(sl),
            "tp": float(tp),
            "deviation": 20,
            "magic": 123456,
            "comment": reason,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        return self._send_order(req)

    def close_position(self, ticket: int, volume: float, type_op: int, reason: str) -> bool:
        close_type = mt5.ORDER_TYPE_SELL if type_op == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(self.symbol).bid if close_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(self.symbol).ask

        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": volume,
            "type": close_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": 123456,
            "comment": f"Close: {reason}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        logger.info(f"🔒 Closing Position {ticket}...")
        return self._send_order(req)

    def modify_position(self, ticket: int, sl: float, tp: float) -> bool:
        req = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "symbol": self.symbol,
            "sl": float(sl),
            "tp": float(tp),
            "magic": 123456,
        }
        if self.dry_run: return True

        result = mt5.order_send(req)
        if result is None: return False
        if result.retcode == 10009 or result.retcode == 10025: return True
        return True