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

def manage_trailing_stop(executor, position, current_price):
    price_dist = abs(current_price - position.price_open)
    if position.price_open == 0: return
    pct_profit = (price_dist / position.price_open) * 100
    if pct_profit > 0.02: 
        if position.type == mt5.ORDER_TYPE_BUY:
            new_sl = position.price_open + (position.price_open * 0.0001)
            step_sl = current_price - (position.price_open * 0.0002)
            final_sl = max(new_sl, step_sl)
            if final_sl > position.sl: executor.modify_position(position.ticket, sl=final_sl, tp=position.tp)
        elif position.type == mt5.ORDER_TYPE_SELL:
            new_sl = position.price_open - (position.price_open * 0.0001)
            step_sl = current_price + (position.price_open * 0.0002)
            final_sl = min(new_sl, step_sl)
            if final_sl < position.sl or position.sl == 0.0: executor.modify_position(position.ticket, sl=final_sl, tp=position.tp)

def start_bot():
    global last_history_check
    logger.info(f"=== TREDING AI V17 (DIRECT HISTORY FETCH) ===")
    
    mt5_feeder = MT5Feeder()
    if not mt5_feeder.initialize(): return
    news_feeder = NewsFeeder() 
    tech_brain = TechnicalBrain()
    sent_brain = SentimentBrain()
    cond_brain = ConditionBrain()
    orchestrator = Orchestrator()
    risk_governor = RiskGovernor()
    executor = MT5Executor(symbol=settings.SYMBOL)

    last_news = 0
    cached_sentiment = {}

    # Set waktu awal cek history biar gak narik data purba
    last_history_check = datetime.now() - timedelta(minutes=1)

    while True:
        try:
            # 1. Cek Kontrol Dashboard
            control = load_control()
            if not control["trading_enabled"]:
                save_status({"status": "PAUSED", "mode": "PAUSED", "account": {}, "positions": [], "market": {}})
                time.sleep(2); continue

            # 2. Ambil Data
            mtf_data = mt5_feeder.get_mtf_data()
            tick = mt5_feeder.get_tick_info()
            if not mtf_data or not tick: continue

            # 3. Analisa
            if time.time() - last_news > 300:
                if settings.USE_GEMINI_FOR_SENTIMENT: cached_sentiment = sent_brain.analyze()
                last_news = time.time()

            tech_res = tech_brain.analyze_mtf(mtf_data)
            cond_res = cond_brain.analyze(df=None) 
            acc_info = mt5.account_info()
            
            # --- 4. UPDATE DASHBOARD ---
            account_data = {
                "balance": acc_info.balance,
                "equity": acc_info.equity,
                "margin_free": acc_info.margin_free,
                "profit": acc_info.profit
            }
            
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

            market_data = {
                "symbol": settings.SYMBOL,
                "price": tick['bid'],
                "trend_h1": tech_res.get('H1', {}).get('trend', 'N/A'),
                "adx": f"{tech_res.get('H1', {}).get('adx', 0):.2f}",
                "pattern": tech_res.get('patterns', 'None')
            }

            full_status = {
                "account": account_data,
                "positions": pos_list,
                "market": market_data,
                "risk_profile": {"mode": settings.TRADING_MODE},
                "mode": "ACTIVE",
                "timestamp": time.time()
            }
            save_status(full_status)

            # --- 5. LOGIKA TRADE HISTORY (DIRECT MT5 FETCH) ---
            # Kita minta data deal dari "last_history_check" sampai "sekarang"
            now = datetime.now()
            deals = mt5.history_deals_get(last_history_check, now)
            
            if deals:
                for deal in deals:
                    # Kita cuma peduli deal ENTRY_OUT (Exit Position) atau ENTRY_INOUT
                    # Entry IN (0) = Buka Posisi (Gak perlu dicatat sebagai history profit)
                    # Entry OUT (1) = Tutup Posisi (Ini yang profit/loss)
                    if deal.entry == mt5.DEAL_ENTRY_OUT and deal.symbol == settings.SYMBOL:
                        logger.info(f"🏁 DEAL DETECTED: Ticket {deal.ticket} | Profit: ${deal.profit}")
                        
                        log_data = {
                            "ticket": deal.position_id, # Link ke posisi aslinya
                            "symbol": deal.symbol,
                            "type": "BUY" if deal.type == 1 else "SELL", # Type deal exit biasanya kebalikan
                            "volume": deal.volume,
                            "profit": deal.profit,
                            "reason": "Closed (MT5 Detect)"
                        }
                        
                        # 1. Catat ke File History (Buat Tab History)
                        log_trade_history(log_data)
                        
                        # 2. Panggil AI Buat Evaluasi (Buat Tab AI Brain)
                        market_snapshot = f"Trend {market_data['trend_h1']}, Pattern {market_data['pattern']}"
                        orchestrator.record_trade_result(log_data, market_snapshot)

            # Update waktu terakhir cek (Majukan dikit biar gak double record)
            last_history_check = now

            # --- 6. EKSEKUSI AI ---
            is_interesting = False
            if tech_res.get('patterns') != "None": is_interesting = True
            if tech_res.get('H1', {}).get('trend') in ["BULLISH_STRONG", "BEARISH_STRONG"]: is_interesting = True
            if raw_positions: is_interesting = True

            if is_interesting:
                if raw_positions:
                    for pos in raw_positions:
                        current_p = tick['bid'] if pos.type == 0 else tick['ask']
                        manage_trailing_stop(executor, pos, current_p)
                        
                        pos_dict = {"ticket": pos.ticket, "type": "BUY" if pos.type==0 else "SELL", "open_price": pos.price_open, "profit": pos.profit, "volume": pos.volume}
                        decision = orchestrator.analyze_open_position(pos_dict, tech_res, cached_sentiment)
                        if decision == "CLOSE_NOW": executor.close_position(pos.ticket, pos.volume, pos.type, "AI Exit")

                risk_eval = risk_governor.evaluate(settings.SYMBOL, 50, 0.0)
                if risk_eval.allowed and len(raw_positions) < settings.MAX_OPEN_TRADES:
                    acc_simple = {"balance": acc_info.balance, "equity": acc_info.equity}
                    decision = orchestrator.decide(tech_res, cached_sentiment, cond_res, acc_simple)
                    action = decision.get("action", "HOLD")
                    
                    if action in ["BUY", "SELL"]:
                        lot = round(risk_eval.lot * decision.get("lot_factor", 1.0), 2)
                        if action == "BUY": executor.buy_market(lot, decision.get('sl',0), decision.get('tp',0), decision.get('reason'))
                        elif action == "SELL": executor.sell_market(lot, decision.get('sl',0), decision.get('tp',0), decision.get('reason'))
            
            time.sleep(settings.LOOP_SLEEP_SECONDS)

        except Exception as e:
            logger.exception(f"Loop Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    start_bot()