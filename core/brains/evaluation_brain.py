import json
import os
from datetime import datetime
from loguru import logger
from core.config import settings
from ai_api.gemini_client import GeminiClient

class EvaluationBrain:
    """
    EVALUATION BRAIN V3: THE POST-MORTEM ANALYST
    Tugas: 
    1. Menganalisis setiap trade yang selesai (Win/Loss).
    2. Menghindari alasan 'Market Noise' default.
    3. Menyimpan pelajaran ke 'journal.json' untuk ditampilkan di Dashboard.
    """
    def __init__(self):
        # Inisialisasi koneksi AI (Support MegaLLM & Gemini)
        self.brain = GeminiClient()
        self.journal_file = "data/journal.json"
        self._ensure_dir()
        logger.info("🧠 EvaluationBrain: Active (Post-Mortem Analyst)")

    def _ensure_dir(self):
        if not os.path.exists("data"): os.makedirs("data")

    def log_observation(self, text, sentiment="NEUTRAL"):
        """Mencatat observasi umum (opsional)"""
        pass

    def reflect_on_trade(self, trade_data, market_snapshot):
        """
        Analisa mendalam kenapa trade ini Profit atau Loss.
        """
        try:
            # 1. Tentukan Hasil Akhir
            pnl = trade_data.get('profit', 0.0)
            result = "WIN" if pnl > 0 else "LOSS"
            ticket = trade_data.get('ticket')
            
            # 2. Siapkan Data untuk AI
            # Kita kasih konteks biar AI gak ngasal
            prompt = f"""
            ACT AS A TRADING MENTOR. ANALYZE THIS CLOSED TRADE.
            
            RESULT: {result} (PnL: ${pnl})
            TYPE: {trade_data.get('type')}
            MARKET CONTEXT: {market_snapshot}
            
            TASK:
            Provide a SHARP, 5-10 word reason for this result.
            - If WIN: Was it trend following? Good trailing stop?
            - If LOSS: Was it a reversal? News spike? Choppy market?
            
            OUTPUT (JUST THE REASON TEXT, NO JSON):
            """
            
            # 3. Minta Pendapat AI (Prioritas: Model Evaluator di .env)
            # Biasanya pakai Llama-3.3-70b atau Gemini Flash yang cepat
            lesson = self.brain.ask_specific_model(settings.MODEL_EVALUATOR, prompt)
            
            # 4. Fallback Logic (Jika AI Bisu/Error)
            if not lesson or len(lesson) < 3 or "error" in lesson.lower():
                # Kita analisa manual sederhana
                if result == "WIN":
                    if pnl > 5.0: lesson = "Strong trend capture."
                    else: lesson = "Scalped small profit."
                else:
                    lesson = "Stop Loss hit by volatility."
            
            # Bersihkan teks (hapus tanda kutip dll)
            lesson = lesson.replace('"', '').replace("'", "").replace("```", "").strip()

            # 5. Susun Data Jurnal
            entry = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "ticket": ticket,
                "type": trade_data.get('type'),
                "result": result,
                "pnl": pnl,
                "lesson": lesson, # Ini hasil analisa AI
                "market_context": market_snapshot
            }
            
            self._save_to_journal(entry)
            logger.info(f"📝 JOURNAL: {result} | {lesson}")

        except Exception as e:
            logger.error(f"Evaluation Error: {e}")

    def _save_to_journal(self, entry):
        """Simpan ke file JSON dengan aman"""
        journal = []
        if os.path.exists(self.journal_file):
            try:
                with open(self.journal_file, 'r') as f:
                    content = f.read()
                    if content: journal = json.load(f)
            except: pass
        
        # Tambahkan entry baru di paling atas (index 0)
        journal.insert(0, entry)
        
        # Simpan max 100 jurnal terakhir biar file gak bengkak
        with open(self.journal_file, 'w') as f:
            json.dump(journal[:100], f, indent=2)