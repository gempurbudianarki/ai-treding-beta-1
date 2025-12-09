import json
import os
from datetime import datetime
from loguru import logger
from ai_api.gemini_client import GeminiClient
from core.config import settings

JOURNAL_FILE = "data/journal.json"

class EvaluationBrain:
    def __init__(self):
        self.brain = GeminiClient()
        self._ensure_db()
        logger.info(f"🧠 EvaluationBrain: Active (Real-Time Mentor)")

    def _ensure_db(self):
        if not os.path.exists("data"): os.makedirs("data")
        if not os.path.exists(JOURNAL_FILE):
            with open(JOURNAL_FILE, 'w') as f: json.dump([], f)

    def _load_journal(self):
        try:
            if os.path.exists(JOURNAL_FILE):
                with open(JOURNAL_FILE, 'r') as f: return json.load(f)
        except: pass
        return []

    def _save_journal(self, data):
        try:
            with open(JOURNAL_FILE, 'w') as f: json.dump(data, f, indent=2)
        except Exception as e: logger.error(f"Journal Save Error: {e}")

    def _generate_lesson(self, prompt_text):
        """Helper buat manggil AI"""
        try:
            resp = self.brain.ask_specific_model(settings.GEMINI_MODEL, prompt_text)
            if not resp: return "Market noise."
            cleaned = resp.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned).get("lesson", "Keep watching.")
        except: return "Analysis pending."

    def log_observation(self, message: str, type_msg: str):
        """
        Mencatat observasi real-time ke jurnal (Bukan cuma pas close).
        """
        entry = {
            "id": int(datetime.now().timestamp()),
            "date": datetime.now().strftime("%H:%M:%S"),
            "symbol": settings.SYMBOL,
            "result": type_msg, # INFO / ALERT / WIN / LOSS
            "pnl": 0,
            "lesson": message, # Pesan langsung
            "market_context": "Real-time Monitoring"
        }
        history = self._load_journal()
        history.append(entry)
        self._save_journal(history[-50:])

    def reflect_on_trade(self, trade_data: dict, market_snapshot: str):
        """Analisa Pasca-Trade (Post-Mortem)"""
        pnl = float(trade_data.get('profit', 0))
        result = "WIN" if pnl > 0 else "LOSS"
        
        prompt = f"""
        ACT AS A TRADING COACH.
        TRADE RESULT: {result} (${pnl}).
        CONTEXT: {market_snapshot}
        TASK: One sentence lesson for future.
        JSON: {{"lesson": "..."}}
        """
        lesson = self._generate_lesson(prompt)
        
        entry = {
            "id": int(datetime.now().timestamp()),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "symbol": settings.SYMBOL,
            "result": result,
            "pnl": pnl,
            "lesson": lesson,
            "market_context": market_snapshot
        }
        history = self._load_journal()
        history.append(entry)
        self._save_journal(history[-50:])
        logger.info(f"📝 JOURNAL: {result} | {lesson}")

    def get_relevant_lessons(self) -> str:
        history = self._load_journal()
        if not history: return "Start fresh. Be disciplined."
        
        # Ambil 3 pelajaran penting terakhir
        important = [h for h in history if h['result'] in ['WIN', 'LOSS']][-3:]
        summary = "🧠 MEMORY:\n"
        for item in important:
            summary += f"- {item['lesson']} ({item['result']})\n"
        return summary