import time
import json
import os
from datetime import datetime, timedelta
import MetaTrader5 as mt5
from loguru import logger
from core.config import settings
from core.utils.control_loader import load_control
from core.feeder.mt5_feeder import MT5Feeder
from core.feeder.news_feeder import NewsFeeder
from core.brains.technical_brain import TechnicalBrain
from core.brains.sentiment_brain import SentimentBrain
from core.brains.condition_brain import ConditionBrain
from core.orchestrator.orchestrator import Orchestrator
from core.execution.mt5_executor import MT5Executor
from core.risk.risk_governor import RiskGovernor
from dashboard.status_loader import save_status, log_trade_history

# Global variable buat tracking waktu terakhir cek history
last_history_check = datetime.now()

def manage_trailing_stop_aggressive(executor, position, current_price):
    """
    TRAILING STOP V2: AGGRESSIVE SECURE (POINTS BASED)
    Sangat efektif untuk XAUUSD (Gold) yang volatile.
    Logika: Begitu profit > X points, geser SL ke Break Even + Profit Kuncian.
    Lalu buntuti harga dengan jarak Y points.
    """
    try:
        # Hitung jarak profit dalam bentuk harga
        profit_dist = 0.0
        if position.type == mt5.ORDER_TYPE_BUY:
            profit_dist = current_price - position.price_open
        elif position.type == mt5.ORDER_TYPE_SELL:
            profit_dist = position.price_open - current_price

        # === KONFIGURASI TRAILING (Dalam Satuan Harga) ===
        # Contoh XAUUSD: 1.00 = 100 pips (tergantung digit broker)
        ACTIVATION_DIST = 1.00  # Aktif jika profit sudah > 1.00 (misal $1 di gold)
        TRAIL_DIST = 0.50       # Jarak buntut SL dari harga running
        SECURE_LOCK = 0.20      # Minimum profit yang dikunci (Break Even + dikit)

        if profit_dist > ACTIVATION_DIST:
            if position.type == mt5.ORDER_TYPE_BUY:
                # Target SL baru: Harga sekarang dikurang jarak trail
                proposed_sl = current_price - TRAIL_DIST
                # Tapi SL gak boleh kurang dari (Open + Secure Lock)
                # Ini menjamin trade sudah 'Risk Free'
                min_lock = position.price_open + SECURE_LOCK
                final_sl = max(proposed_sl, min_lock)
                
                # Eksekusi cuma kalau SL baru lebih tinggi dari SL lama
                if final_sl > position.sl:
                    logger.info(f"🏃 TRAILING BUY: Ticket {position.ticket} | Locked Profit: {final_sl}")
                    executor.modify_position(position.ticket, sl=final_sl, tp=position.tp)

            elif position.type == mt5.ORDER_TYPE_SELL:
                # Target SL baru: Harga sekarang ditambah jarak trail
                proposed_sl = current_price + TRAIL_DIST
                # Tapi SL gak boleh lebih dari (Open - Secure Lock)
                max_lock = position.price_open - SECURE_LOCK
                final_sl = min(proposed_sl, max_lock)
                
                # Eksekusi cuma kalau SL baru lebih rendah dari SL lama
                if position.sl == 0.0 or final_sl < position.sl:
                    logger.info(f"🏃 TRAILING SELL: Ticket {position.ticket} | Locked Profit: {final_sl}")
                    executor.modify_position(position.ticket, sl=final_sl, tp=position.tp)

    except Exception as e:
        logger.error(f"Trailing Error: {e}")

def start_bot():
    """Fungsi Utama Loop Bot."""
    global last_history_check
    logger.info(f"=== NEON SNIPER V3.2 (AGGRESSIVE MODE) ===")
    logger.info(f"Symbol: {settings.SYMBOL} | Mode: {settings.TRADING_MODE}")
    
    # 1. INITIALIZATION
    mt5_feeder = MT5Feeder()
    if not mt5_feeder.initialize(): 
        logger.critical("Bot Stopped due to MT5 Error.")
        return

    # Initialize All Brains & Controllers
    news_feeder = NewsFeeder() 
    tech_brain = TechnicalBrain()
    sent_brain = SentimentBrain()
    cond_brain = ConditionBrain()
    orchestrator = Orchestrator()
    risk_governor = RiskGovernor()
    executor = MT5Executor(symbol=settings.SYMBOL)

    last_news_time = 0
    cached_sentiment = {"sentiment": "Neutral", "score": 0}

    # Set history check mundur 1 menit biar gak kelewatan deal terakhir
    last_history_check = datetime.now() - timedelta(minutes=1)

    # === INFINITE LOOP ===
    while True:
        try:
            # A. CEK KONTROL DASHBOARD
            control = load_control()
            if not control["trading_enabled"]:
                save_status({"status": "PAUSED", "mode": "PAUSED", "account": {}, "positions": [], "market": {}})
                # Sleep sebentar biar gak makan CPU pas idle
                time.sleep(2)
                continue

            # B. AMBIL DATA MARKET
            mtf_data = mt5_feeder.get_mtf_data()
            tick = mt5_feeder.get_tick_info()
            
            if not mtf_data or not tick:
                logger.warning("Waiting for data feed...")
                time.sleep(2)
                continue

            # C. UPDATE SENTIMENT (Setiap 5 Menit)
            if time.time() - last_news_time > 300:
                if settings.USE_GEMINI_FOR_SENTIMENT: 
                    cached_sentiment = sent_brain.analyze()
                    logger.info(f"📰 Sentiment Update: {cached_sentiment.get('sentiment')}")
                last_news_time = time.time()

            # D. ANALISA TEKNIKAL
            tech_res = tech_brain.analyze_mtf(mtf_data)
            cond_res = cond_brain.analyze(df=None) 
            acc_info = mt5.account_info()
            
            # E. UPDATE DASHBOARD REAL-TIME
            if acc_info:
                account_data = {
                    "balance": acc_info.balance,
                    "equity": acc_info.equity,
                    "margin_free": acc_info.margin_free,
                    "profit": acc_info.profit
                }
            else:
                account_data = {}

            # Ambil Posisi Terbuka
            raw_positions = mt5.positions_get(symbol=settings.SYMBOL)
            pos_list = []
            if raw_positions:
                for p in raw_positions:
                    pos_list.append({
                        "ticket": p.ticket,
                        "type": "BUY" if p.type == 0 else "SELL",
                        "volume": p.volume,
                        "open_price": p.price_open,
                        "profit": p.profit,
                        "sl": p.sl,
                        "tp": p.tp
                    })

            # Data Market untuk Dashboard
            signal_status = tech_res.get('patterns', 'None')
            market_data = {
                "symbol": settings.SYMBOL,
                "price": tick['bid'],
                "trend_h1": tech_res.get('H1', {}).get('trend', 'N/A'),
                "momentum": tech_res.get('M15', {}).get('momentum', 'N/A'),
                "adx": f"{tech_res.get('M15', {}).get('adx', 0):.2f}",
                "pattern": signal_status
            }

            # Kirim status ke JSON
            save_status({
                "account": account_data,
                "positions": pos_list,
                "market": market_data,
                "risk_profile": {"mode": settings.TRADING_MODE},
                "mode": "ACTIVE",
                "timestamp": time.time()
            })

            # F. CEK HISTORY TRADING (Untuk Evaluasi)
            now = datetime.now()
            deals = mt5.history_deals_get(last_history_check, now)
            
            if deals:
                for deal in deals:
                    # Filter: Deal OUT (Exit) pada Symbol kita
                    if deal.entry == mt5.DEAL_ENTRY_OUT and deal.symbol == settings.SYMBOL:
                        logger.success(f"🏁 TRADE CLOSED: Ticket {deal.ticket} | PnL: ${deal.profit}")
                        
                        log_data = {
                            "ticket": deal.position_id,
                            "symbol": deal.symbol,
                            "type": "BUY" if deal.type == 1 else "SELL", # Type deal exit biasanya kebalikan
                            "volume": deal.volume,
                            "profit": deal.profit,
                            "reason": "Closed (MT5 Detect)"
                        }
                        
                        # Simpan log
                        log_trade_history(log_data)
                        
                        # Panggil Evaluator AI (Llama)
                        market_snapshot = f"Trend {market_data['trend_h1']}, Pattern {signal_status}"
                        orchestrator.record_trade_result(log_data, market_snapshot)

            last_history_check = now

            # G. LOGIKA EKSEKUSI & MANAJEMEN
            
            # 1. Management Posisi (Trailing & AI Exit)
            if raw_positions:
                for pos in raw_positions:
                    current_p = tick['bid'] if pos.type == 0 else tick['ask']
                    
                    # a. Aggressive Trailing Stop (Mechanical)
                    manage_trailing_stop_aggressive(executor, pos, current_p)
                    
                    # b. AI Smart Exit (Decision)
                    pos_dict = {
                        "ticket": pos.ticket, 
                        "type": "BUY" if pos.type==0 else "SELL", 
                        "open_price": pos.price_open, 
                        "profit": pos.profit, 
                        "volume": pos.volume
                    }
                    decision = orchestrator.analyze_open_position(pos_dict, tech_res, cached_sentiment)
                    
                    if decision == "CLOSE_NOW": 
                        executor.close_position(pos.ticket, pos.volume, pos.type, "AI Smart Exit")

            # 2. Entry Baru (Hanya jika ada Signal Sniper)
            is_sniper_signal = signal_status in ["SNIPER_BUY", "SNIPER_SELL"]
            
            if is_sniper_signal:
                # Filter Risk: Jangan open kalau max trades tercapai
                if len(raw_positions) < settings.MAX_OPEN_TRADES:
                    logger.info(f"🎯 SNIPER SIGNAL DETECTED: {signal_status}")
                    
                    # Validasi Risk Governor (Basic Lot Calc)
                    risk_eval = risk_governor.evaluate(settings.SYMBOL, 50, 0.0)
                    
                    if risk_eval.allowed:
                        acc_simple = {"balance": acc_info.balance, "equity": acc_info.equity}
                        
                        # Konsultasi AI Orchestrator
                        decision = orchestrator.decide(tech_res, cached_sentiment, cond_res, acc_simple)
                        action = decision.get("action", "HOLD")
                        
                        if action in ["BUY", "SELL"]:
                            # Override Logic: Gunakan SL/TP dari AI, atau fallback ke default
                            ai_sl = decision.get('sl', 0.0)
                            ai_tp = decision.get('tp', 0.0)
                            
                            lot = round(risk_eval.lot * decision.get("lot_factor", 1.0), 2)
                            reason = decision.get('reason', 'Sniper AI')
                            
                            logger.success(f"🚀 EXECUTING {action} | Lot: {lot} | {reason}")
                            
                            if action == "BUY": 
                                executor.buy_market(lot, ai_sl, ai_tp, reason)
                            elif action == "SELL": 
                                executor.sell_market(lot, ai_sl, ai_tp, reason)

            # H. SLEEP (Tunggu cycle berikutnya)
            time.sleep(settings.LOOP_SLEEP_SECONDS)

        except Exception as e:
            logger.exception(f"Loop Error: {e}")
            time.sleep(5) # Safety pause kalau error

if __name__ == "__main__":
    start_bot()