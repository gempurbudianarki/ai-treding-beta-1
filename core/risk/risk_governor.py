import MetaTrader5 as mt5
from loguru import logger
from dataclasses import dataclass
from core.config import settings

@dataclass
class RiskEvaluation:
    """Struktur Data hasil evaluasi risiko"""
    allowed: bool
    lot: float
    reason: str

class RiskGovernor:
    """
    RISK GOVERNOR V5.0: THE FINANCIAL GUARDIAN (FULL VERSION)
    
    Tugas Utama:
    1. Menghitung Lot Size yang AMAN dan LEGAL (sesuai aturan broker).
    2. Mencegah Margin Call dengan menghitung kapasitas Free Margin.
    3. Mencegah Over-Risk dengan menghitung Stop Loss value.
    """

    def __init__(self):
        # Load konfigurasi dari .env
        self.risk_pct = settings.RISK_PER_TRADE_PCT
        self.max_drawdown = settings.MAX_DAILY_DRAWDOWN_PCT
        logger.info(f"🛡️ RiskGovernor V5 Active | Risk Profile: {self.risk_pct}% | Max Daily Drawdown: {self.max_drawdown}%")

    def _get_account_info(self):
        """Mengambil data akun terbaru dari MT5"""
        return mt5.account_info()

    def _get_symbol_info(self, symbol):
        """Mengambil spesifikasi kontrak symbol"""
        return mt5.symbol_info(symbol)

    def _calculate_margin_cost(self, symbol: str, volume: float, order_type: int) -> float:
        """
        FITUR CANGGIH: Margin Check Real-time.
        Bertanya ke Server MT5: 'Berapa duit yang harus disetor untuk lot segini?'
        """
        try:
            # Dapatkan harga market saat ini untuk estimasi akurat
            tick = mt5.symbol_info_tick(symbol)
            if not tick: return 0.0
            
            price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid
            
            # API MT5 untuk hitung margin
            margin = mt5.order_calc_margin(order_type, symbol, volume, price)
            return margin if margin is not None else 0.0
        except Exception as e:
            logger.error(f"⚠️ Margin Calc Error: {e}")
            return 0.0

    def evaluate(self, symbol: str, sl_pips: float, entry_price: float) -> RiskEvaluation:
        """
        Fungsi Utama Evaluasi.
        Menggabungkan Logika Risiko + Logika Saldo Dompet.
        """
        
        # 1. VALIDASI KONEKSI & AKUN
        acc = self._get_account_info()
        if not acc:
            return RiskEvaluation(False, 0.0, "Critical: MT5 Account Info Unavailable")

        symbol_info = self._get_symbol_info(symbol)
        if not symbol_info:
            return RiskEvaluation(False, 0.0, f"Critical: Symbol {symbol} Not Found")

        # 2. CEK BATAS KERUGIAN HARIAN (DAILY DRAWDOWN PROTECTION)
        # Menghitung penurunan equity dari balance
        current_drawdown_pct = ((acc.balance - acc.equity) / acc.balance) * 100
        
        if current_drawdown_pct > self.max_drawdown:
            logger.warning(f"⛔ STOP TRADING: Daily Drawdown Limit Hit ({current_drawdown_pct:.2f}% > {self.max_drawdown}%)")
            return RiskEvaluation(False, 0.0, "Daily Loss Limit Reached")

        # 3. PERSIAPAN DATA BROKER
        min_lot = symbol_info.volume_min
        max_lot = symbol_info.volume_max
        step_lot = symbol_info.volume_step
        tick_value = symbol_info.trade_tick_value if symbol_info.trade_tick_value > 0 else 1.0

        # --- STEP A: HITUNG LOT BERDASARKAN RISIKO (SOFT LIMIT) ---
        # "Saya mau rugi maksimal 1% dari Equity jika kena SL"
        risk_money = acc.equity * (self.risk_pct / 100.0)
        
        if sl_pips > 0:
            # Rumus: Uang Resiko / (Jarak SL * Nilai Per Poin)
            # Asumsi sl_pips dikonversi ke points jika perlu
            max_lot_risk = risk_money / (sl_pips * tick_value)
        else:
            # Jika strategi tidak kirim SL (bahaya), kita batasi ke min lot atau logic margin
            max_lot_risk = max_lot 

        # --- STEP B: HITUNG LOT BERDASARKAN DOMPET (HARD LIMIT) ---
        # "Saya cuma punya duit sekian di Free Margin"
        
        # Hitung harga margin untuk 1 Lot standar (Buy)
        margin_per_1_lot = self._calculate_margin_cost(symbol, 1.0, mt5.ORDER_TYPE_BUY)
        
        max_lot_wallet = 0.0
        if margin_per_1_lot > 0:
            # Gunakan 95% dari Free Margin (Buffer 5% untuk fluktuasi spread)
            usable_margin = acc.margin_free * 0.95
            max_lot_wallet = usable_margin / margin_per_1_lot
        else:
            # Fallback jika gagal hitung margin (sangat jarang), pakai lot terkecil
            max_lot_wallet = min_lot

        # --- STEP C: KEPUTUSAN FINAL (AMBIL YANG TERKECIL) ---
        # Bandingkan keinginan (Risk) vs Kemampuan (Wallet)
        final_lot = min(max_lot_risk, max_lot_wallet)
        
        # Normalisasi ke Step Lot Broker (misal kelipatan 0.01)
        final_lot = round(final_lot / step_lot) * step_lot
        
        # Pastikan tidak melanggar batas Min/Max Broker
        final_lot = max(final_lot, min_lot)
        final_lot = min(final_lot, max_lot)
        
        # Rounding desimal agar rapi (2 desimal biasanya cukup)
        final_lot = round(final_lot, 2)

        # --- STEP D: REALITY CHECK TERAKHIR ---
        # Cek apakah final_lot ini benar-benar cukup marginnya (Double Check)
        final_margin_req = self._calculate_margin_cost(symbol, final_lot, mt5.ORDER_TYPE_BUY)
        
        reason = "Risk Approved"
        
        if final_margin_req > acc.margin_free:
            # Jika setelah dibulatkan ternyata masih kurang duitnya
            if final_lot <= min_lot:
                 return RiskEvaluation(False, 0.0, f"Insufficient Funds for Min Lot (Need ${final_margin_req:.2f})")
            else:
                 # Coba turunkan satu step lagi
                 final_lot -= step_lot
                 final_lot = round(final_lot, 2)
        
        # Set Reason untuk Log
        if final_lot < max_lot_risk:
            reason = f"Lot Capped by Wallet (Risk wants {max_lot_risk:.2f}, Wallet max {max_lot_wallet:.2f})"
        
        return RiskEvaluation(True, final_lot, reason)