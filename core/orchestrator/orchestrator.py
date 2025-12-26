import json
import os
from datetime import datetime
from typing import Dict, Any
from loguru import logger
from core.utils.control_loader import load_control
from core.config import settings
from ai_api.gemini_client import GeminiClient
from core.brains.evaluation_brain import EvaluationBrain 

class Orchestrator:
    """
    ORCHESTRATOR V4.0: DISCIPLINED COMMANDER (FULL VERSION)
    
    Fitur Utama:
    1. Integrasi 'ConditionBrain' untuk Time Filter (Jam Kerja).
    2. Konsultasi AI 2 Tahap: Strategist (Qwen) -> Risk Governor (DeepSeek).
    3. Logging Percakapan AI ke Dashboard.
    4. Pengelolaan Keputusan HOLD/EXECUTE yang ketat.
    """
    
    def __init__(self):
        self.mode = settings.TRADING_MODE
        self.ai_enabled = settings.USE_GEMINI_FOR_SENTIMENT
        
        # Inisialisasi AI Client (Jika diaktifkan)
        self.brain = GeminiClient() if self.ai_enabled else None
        self.evaluator = EvaluationBrain()
        
        # Lokasi File Log Chat untuk Dashboard
        self.log_file = "data/ai_chat_log.json"
        self._ensure_log_dir()
        
        logger.info(f"⚔️ ORCHESTRATOR INITIALIZED | Mode: {self.mode}")

    def _ensure_log_dir(self):
        """Memastikan folder data tersedia"""
        if not os.path.exists("data"): 
            os.makedirs("data")

    def _save_chat(self, speaker: str, message: str, action: str):
        """
        Menyimpan log chat AI ke JSON agar bisa dibaca oleh Dashboard.
        Format: Time | Speaker | Message | Action
        """
        try:
            entry = {
                "time": datetime.now().strftime("%H:%M:%S"), 
                "speaker": speaker, 
                "message": str(message), 
                "action": action
            }
            logs = []
            
            # Baca log lama jika ada
            if os.path.exists(self.log_file):
                try:
                    with open(self.log_file, 'r') as f: 
                        content = f.read()
                        if content: logs = json.loads(content) or []
                except: logs = []
            
            # Tambahkan entri baru
            logs.append(entry)
            
            # Simpan hanya 50 percakapan terakhir (Rolling Buffer)
            with open(self.log_file, 'w') as f: 
                json.dump(logs[-50:], f, indent=2)
                
        except Exception as e:
            logger.error(f"Chat Log Error: {e}")

    def _parse_decision(self, response_text: str) -> Dict[str, Any]:
        """
        Membersihkan output dari LLM (biasanya ada markdown ```json ... ```)
        menjadi Dictionary Python yang valid.
        """
        try:
            if not response_text: return {}
            # Bersihkan Markdown
            text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from AI Response")
            return {}
        except Exception as e:
            logger.error(f"Parse Error: {e}")
            return {}

    def decide(self, technical, sentiment, condition, account_info):
        """
        FUNGSI UTAMA PENGAMBILAN KEPUTUSAN (THE BRAIN).
        Alur Logika:
        1. Cek Switch Manual di Dashboard (Jika STOP, maka berhenti).
        2. Cek Kondisi Market & Waktu (ConditionBrain).
        3. Jika Lolos, Konsultasi ke AI (Strategist & Risk).
        """
        
        # 1. CEK KONTROL MANUAL (DASHBOARD SWITCH)
        control = load_control()
        if not control["trading_enabled"]: 
            return {"action": "HOLD", "reason": "Paused by User (Dashboard)"}
        
        # 2. CEK KONDISI MARKET & WAKTU (INTEGRASI BARU)
        # Data 'condition' berasal dari ConditionBrain.analyze()
        if not condition.get("allowed", True):
            reason = condition.get("reason", "Condition Restricted")
            # Jika kondisi tidak mengizinkan (misal jam tidur), return HOLD
            return {"action": "HOLD", "reason": reason}

        # 3. KONSULTASI AI (Hanya jika jam kerja aktif & market sehat)
        if self.ai_enabled: 
            return self._consult_duo_entry(technical, sentiment, account_info)
        
        # Fallback jika AI dimatikan tapi bot tetap jalan
        return {"action": "HOLD", "reason": "AI Disabled in Settings"}

    def _consult_duo_entry(self, technical: Dict, sentiment: Dict, account_info: Dict) -> Dict:
        """
        Proses Konsultasi AI:
        Tahap 1: Strategist (Qwen) -> Mencari peluang entry agresif.
        Tahap 2: Risk Governor (DeepSeek) -> Memvalidasi keamanan entry.
        """
        if not self.brain: return {}

        # Ekstrak Data Teknikal
        h1 = technical.get('H1', {})
        m15 = technical.get('M15', {})
        price = technical.get('current_price')
        pattern = technical.get('patterns', 'None')
        
        # EFISIENSI: Jika TechnicalBrain tidak menemukan pola (None),
        # Jangan buang-buang kuota API untuk bertanya ke AI.
        if pattern == "None":
            return {"action": "HOLD", "reason": "No Technical Pattern"}

        # Siapkan Konteks Pasar untuk AI
        market_context = f"""
        ASSET: {settings.SYMBOL} | PRICE: {price}
        SIGNAL: {pattern} (Source: TechnicalBrain Analysis)
        
        TREND H1: {h1.get('trend', 'UNKNOWN')}
        MOMENTUM M15: {m15.get('momentum', 'NEUTRAL')}
        RSI M15: {m15.get('rsi', 50)}
        NEWS SENTIMENT: {sentiment.get('sentiment', 'Neutral')}
        """

        # --- TAHAP 1: STRATEGIST (QWEN) ---
        prompt_strat = f"""
        ROLE: You are a RUTHLESS SCALPER (XAUUSD Specialist).
        
        MARKET DATA:
        {market_context}
        
        RULES:
        1. FOLLOW TREND H1 STRICTLY. (If Bullish -> Buy Only, If Bearish -> Sell Only).
        2. Signal '{pattern}' detected. Confirm if momentum supports it.
        3. IGNORE weak signals against the trend.
        4. SET TIGHT STOP LOSS (Max 30-50 pips).
        5. TARGET Risk-Reward > 1:1.5.
        
        OUTPUT (JSON ONLY):
        {{"action": "BUY/SELL/HOLD", "tp": price_target, "sl": price_stop, "reason": "Brief tactical reason"}}
        """
        
        # Tanya Qwen
        resp_strat = self.brain.ask_specific_model(settings.MODEL_QWEN, prompt_strat)
        data_strat = self._parse_decision(resp_strat)
        strat_action = data_strat.get("action", "HOLD").upper()
        
        # Log Jawaban Strategist
        self._save_chat("Strategist (Qwen)", data_strat.get("reason", "Thinking..."), strat_action)

        # Jika Strategist ragu (HOLD), langsung berhenti
        if strat_action == "HOLD": 
            return {"action": "HOLD", "reason": "Strategist Veto (No Entry)"}

        # --- TAHAP 2: RISK GOVERNOR (DEEPSEEK) ---
        prompt_risk = f"""
        ROLE: You are a SENIOR RISK MANAGER. Verify this trade proposal.
        
        PROPOSAL: {strat_action} @ {price}
        TP: {data_strat.get('tp')} | SL: {data_strat.get('sl')}
        
        MARKET CONTEXT:
        {market_context}
        
        VERIFICATION CHECKLIST:
        1. Is the trade aligned with H1 Trend? (Crucial)
        2. Is the SL logical (not too wide/narrow)?
        3. Is RSI currently extreme? (Overbought > 70 for Buy / Oversold < 30 for Sell)? If yes, REJECT immediately.
        
        OUTPUT (JSON ONLY):
        {{"action": "APPROVE/REJECT", "reason": "Critique or Approval"}}
        """
        
        # Tanya DeepSeek
        resp_risk = self.brain.ask_specific_model(settings.MODEL_DEEPSEEK, prompt_risk)
        data_risk = self._parse_decision(resp_risk)
        risk_decision = data_risk.get("action", "REJECT").upper()
        
        # Log Jawaban Risk Manager
        self._save_chat("Risk Governor", data_risk.get("reason", "Analyzing Risk..."), risk_decision)

        # KEPUTUSAN FINAL
        # Trade dieksekusi HANYA JIKA Risk Manager menyetujui ("APPROVE")
        if "APPROVE" in risk_decision:
            self._save_chat("SYSTEM", "✅ TRADE APPROVED", "EXECUTE")
            return {
                "action": strat_action,
                "tp": float(data_strat.get("tp", 0.0)),
                "sl": float(data_strat.get("sl", 0.0)),
                "lot_factor": 1.0,
                "reason": f"Consensus: {data_risk.get('reason')}"
            }
        else:
            self._save_chat("SYSTEM", "🛡️ VETO BY RISK MANAGER", "HOLD")
            return {"action": "HOLD", "reason": "Risk Manager Rejected Trade"}

    def analyze_open_position(self, position_data, technical, sentiment):
        """
        Analisa Posisi Berjalan (Exit Strategy).
        Bisa dikembangkan nanti untuk Cut Loss Cerdas via AI.
        Saat ini default HOLD (biarkan Trailing Stop yang bekerja).
        """
        return "HOLD"
    
    def record_trade_result(self, trade_data, market_snapshot):
        """Mencatat hasil trading ke Jurnal Evaluasi"""
        self.evaluator.reflect_on_trade(trade_data, market_snapshot)