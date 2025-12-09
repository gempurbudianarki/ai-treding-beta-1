import json
import os
import concurrent.futures
from datetime import datetime
import pytz
from typing import Dict, Any, Optional
from loguru import logger
from core.utils.control_loader import load_control
from core.config import settings
from ai_api.gemini_client import GeminiClient
from core.brains.evaluation_brain import EvaluationBrain 

class Orchestrator:
    """
    THE BRAIN V21: FLEXIBLE SWING (REVERSAL ENABLED)
    Fitur:
    - Boleh Lawan Arus (Counter-Trend) kalau kena Order Block.
    - Tetap disiplin Risk Management.
    """
    
    def __init__(self):
        self.mode = settings.TRADING_MODE
        self.ai_enabled = settings.USE_GEMINI_FOR_SENTIMENT
        self.brain = GeminiClient() if self.ai_enabled else None
        self.evaluator = EvaluationBrain()
        self.log_file = "data/ai_chat_log.json"
        self._ensure_log_dir()
        logger.info(f"⚔️ ORCHESTRATOR V21: FLEXIBLE SWING READY")

    def _ensure_log_dir(self):
        if not os.path.exists("data"): os.makedirs("data")

    def _save_chat(self, speaker: str, message: str, action: str):
        try:
            entry = {"time": datetime.now().strftime("%H:%M:%S"), "speaker": speaker, "message": message, "action": action}
            logs = []
            if os.path.exists(self.log_file):
                try:
                    with open(self.log_file, 'r') as f:
                        content = f.read()
                        if content: logs = json.loads(content) or []
                except: logs = []
            logs.append(entry)
            with open(self.log_file, 'w') as f: json.dump(logs[-50:], f, indent=2)
        except: pass

    def _parse_decision(self, response_text: str) -> Dict:
        try:
            if not response_text: return {}
            text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except: return {}

    def _consult_duo_entry(self, technical: Dict, sentiment: Dict, account_info: Dict) -> Dict:
        if not self.brain: return {}

        h1 = technical.get('H1', {})
        m15 = technical.get('M15', {})
        price = technical.get('current_price')
        
        # SMC Data
        bull_ob = technical.get('bullish_ob', 0)
        bear_ob = technical.get('bearish_ob', 0)
        
        # Jarak ke OB
        dist_bull = abs(price - bull_ob) if bull_ob > 0 else 9999
        dist_bear = abs(price - bear_ob) if bear_ob > 0 else 9999
        
        market_data = f"""
        Asset: {settings.SYMBOL} | Price: {price} | Timeframe: M15
        
        === TREND CONTEXT ===
        H1 Trend: {h1.get('trend')} (ADX: {h1.get('adx'):.1f})
        M15 Trend: {m15.get('trend')} (RSI: {m15.get('rsi'):.1f})
        
        === SMART MONEY LEVELS ===
        Bullish OB (Buy Zone): {bull_ob} (Dist: {dist_bull:.2f})
        Bearish OB (Sell Zone): {bear_ob} (Dist: {dist_bear:.2f})
        
        === SENTIMENT ===
        News: {sentiment.get('sentiment', 'Neutral')}
        """

        # --- QWEN (THE FLEXIBLE STRATEGIST) ---
        # Prompt Baru: Izinkan Counter-Trend di Zona Kuat
        prompt_qwen = f"""
        ACT AS A PRO SWING TRADER.
        
        DATA:
        {market_data}
        
        STRATEGY RULES:
        1. **TREND FOLLOW**: Best trade is WITH H1 Trend.
        2. **REVERSAL ALLOWED**: If Price is at a major ORDER BLOCK (OB), you CAN trade against H1 Trend.
           - Example: H1 Bearish, but Price at Bullish OB -> **BUY ALLOWED**.
        3. **RSI CHECK**: If buying against trend, RSI must be < 40 (Oversold).
        
        DECISION (JSON):
        {{"action": "BUY/SELL/HOLD", "tp": 0.0, "sl": 0.0, "reason": "Explanation"}}
        """
        
        resp_qw = self.brain.ask_specific_model(settings.MODEL_QWEN, prompt_qwen)
        data_qw = self._parse_decision(resp_qw)
        qw_action = data_qw.get("action", "HOLD").upper()
        
        self._save_chat("Qwen (Swing)", data_qw.get("reason"), qw_action)

        if qw_action == "HOLD":
            return {"action": "HOLD", "reason": f"Qwen: {data_qw.get('reason')}"}

        # --- DEEPSEEK (THE RISK MANAGER) ---
        prompt_ds = f"""
        ACT AS A RISK MANAGER.
        Qwen wants to {qw_action}.
        
        CONTEXT:
        {market_data}
        
        TASK:
        Validate Trade.
        - If Trend Following: AGREE.
        - If Counter-Trend (Reversal): AGREE ONLY IF Price is at Order Block/Support.
        - If Buying at Resistance / Selling at Support -> VETO.
        
        DECISION (JSON):
        {{"action": "BUY/SELL/HOLD", "reason": "..."}}
        """
        
        resp_ds = self.brain.ask_specific_model(settings.MODEL_DEEPSEEK, prompt_ds)
        data_ds = self._parse_decision(resp_ds)
        ds_action = data_ds.get("action", "HOLD").upper()
        
        self._save_chat("DeepSeek (Risk)", data_ds.get("reason"), ds_action)

        if qw_action == ds_action:
            self._save_chat("SYSTEM", "🔥 TRADE APPROVED", "EXECUTE")
            self.evaluator.log_observation(f"Trade {qw_action}", "INFO")
            return {
                "action": qw_action,
                "tp": float(data_qw.get("tp", 0.0)),
                "sl": float(data_qw.get("sl", 0.0)),
                "lot_factor": 1.0,
                "reason": f"Consensus: {data_ds.get('reason')}"
            }
        else:
            self._save_chat("SYSTEM", f"🛡️ VETO by DeepSeek", "HOLD")
            return {"action": "HOLD", "reason": "DeepSeek Veto"}

    def decide(self, technical, sentiment, condition, account_info):
        control = load_control()
        if not control["trading_enabled"]: return {"action": "HOLD", "reason": "DISABLED"}
        if self.ai_enabled: return self._consult_duo_entry(technical, sentiment, account_info)
        return {"action": "HOLD", "reason": "AI Offline"}

    def analyze_open_position(self, position_data, technical, sentiment):
        if not self.brain: return "HOLD"
        
        prompt = f"""
        MANAGE SWING POS:
        {position_data['type']} | P/L: ${position_data['profit']}
        Price: {technical.get('current_price')}
        
        DECISION:
        - HOLD as long as structure holds.
        - CLOSE_NOW if Trend Reverses or Key Level breaks against us.
        
        JSON: {{"decision": "CLOSE_NOW/HOLD", "reason": "..."}}
        """
        resp = self.brain.ask_specific_model(settings.MODEL_QWEN, prompt)
        data = self._parse_decision(resp)
        decision = data.get("decision", "HOLD").upper()
        
        if decision == "CLOSE_NOW":
            self._save_chat("Qwen (Exit)", data.get("reason"), "CLOSE")
            
        return decision
    
    def record_trade_result(self, trade_data, market_snapshot):
        self.evaluator.reflect_on_trade(trade_data, market_snapshot)