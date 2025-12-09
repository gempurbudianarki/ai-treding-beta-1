from dataclasses import dataclass
from typing import Optional

import MetaTrader5 as mt5
from loguru import logger

from config.settings import settings


@dataclass
class RiskDecision:
    allowed: bool
    lot: float
    reason: str


class RiskGovernor:
    """
    Polisi Resiko & Keuangan.
    Tugas:
    1. Cek Drawdown Harian (Biar gak boncos).
    2. Cek Saldo & Margin (Biar gak 'No Money').
    3. Hitung Lot Ideal (Berdasarkan resiko & kekuatan dana).
    """

    def __init__(self) -> None:
        self.risk_pct = settings.RISK_PER_TRADE_PCT
        self.max_daily_dd_pct = settings.MAX_DAILY_DRAWDOWN_PCT
        self.max_open_trades = settings.MAX_OPEN_TRADES

    def _count_open_trades(self, symbol: str) -> int:
        positions = mt5.positions_get(symbol=symbol)
        if positions is None:
            return 0
        return len(positions)

    def _calc_max_lot_by_margin(self, symbol: str, free_margin: float, order_type: int, price: float) -> float:
        """
        Menghitung lot maksimal berdasarkan Free Margin yang tersedia.
        Supaya tidak kena error 'No Money' (10019).
        """
        try:
            # Gunakan fungsi MT5 untuk estimasi margin per 1.0 lot
            # order_calc_margin(action, symbol, volume, price) -> required_margin
            margin_per_lot = mt5.order_calc_margin(mt5.ORDER_TYPE_BUY, symbol, 1.0, price)
            
            if margin_per_lot is None or margin_per_lot <= 0:
                logger.warning("Gagal hitung margin per lot. Pakai estimasi kasar.")
                return 0.01 # Fallback aman

            # Hitung maksimal lot yang bisa dibeli dengan free margin (sisakan buffer 10% biar aman)
            safe_margin = free_margin * 0.90 
            max_lot = safe_margin / margin_per_lot
            
            return float(max_lot)
        except Exception as e:
            logger.error(f"Error calc margin lot: {e}")
            return 0.01

    def evaluate(
        self,
        symbol: str,
        sl_pips: float,
        daily_pl_pct: Optional[float],
    ) -> RiskDecision:
        # 1. Ambil Info Akun
        account = mt5.account_info()
        if not account:
            logger.error("RiskGovernor: gagal ambil account_info.")
            return RiskDecision(False, 0.0, "no_account")

        equity = account.equity
        free_margin = account.margin_free

        # 2. Cek Daily Drawdown (Stop kalau hari ini udah rugi banyak)
        if daily_pl_pct is not None and daily_pl_pct <= -self.max_daily_dd_pct:
            logger.warning(
                "RiskGovernor: daily drawdown {}% melewati limit {}%",
                daily_pl_pct,
                self.max_daily_dd_pct,
            )
            return RiskDecision(False, 0.0, "max_daily_drawdown_reached")

        # 3. Cek Jumlah Posisi
        open_trades = self._count_open_trades(symbol)
        if open_trades >= self.max_open_trades:
            return RiskDecision(False, 0.0, "max_trades_limit")

        # 4. Ambil Info Simbol
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return RiskDecision(False, 0.0, "symbol_error")

        # 5. HITUNG LOT (LOGIKA GABUNGAN)
        
        # A. Lot Berdasarkan Resiko (Kalau kena SL, ilang X% Equity)
        if sl_pips <= 0: sl_pips = 50.0 # Default jaga-jaga
        
        tick_value = symbol_info.trade_tick_value
        if tick_value == 0: tick_value = 1.0 # Hindari bagi nol
        
        # Rumus: (Equity * Risk%) / (JarakSL_Points * NilaiPerPoin)
        # Catatan: sl_pips di sini diasumsikan dalam Poin/Tick standard
        risk_money = equity * (self.risk_pct / 100.0)
        lot_by_risk = risk_money / (sl_pips * tick_value) if sl_pips > 0 else 0.01

        # B. Lot Berdasarkan Saldo (Margin Check) - BIAR GAK ERROR 'NO MONEY'
        current_price = symbol_info.ask
        lot_by_margin = self._calc_max_lot_by_margin(symbol, free_margin, mt5.ORDER_TYPE_BUY, current_price)

        # C. Ambil yang terkecil (Paling Aman)
        final_lot = min(lot_by_risk, lot_by_margin)

        # D. Sesuaikan dengan batasan Broker (Min/Max/Step)
        if final_lot < symbol_info.volume_min:
            # Kalau duit bener-bener gak cukup buat Min Lot, tolak.
            if lot_by_margin < symbol_info.volume_min:
                return RiskDecision(False, 0.0, f"insufficient_margin_for_min_lot_{symbol_info.volume_min}")
            final_lot = symbol_info.volume_min # Paksa ke min lot kalau masih masuk margin

        if final_lot > symbol_info.volume_max:
            final_lot = symbol_info.volume_max

        # Bulatkan sesuai volume step (misal kelipatan 0.01)
        step = symbol_info.volume_step
        final_lot = round(final_lot / step) * step
        final_lot = round(final_lot, 2)

        # logger.info(f"⚖️ Risk Calc: ByRisk={lot_by_risk:.2f} | ByMargin={lot_by_margin:.2f} -> Final={final_lot}")

        if final_lot <= 0:
            return RiskDecision(False, 0.0, "zero_lot")

        return RiskDecision(True, final_lot, "ok")