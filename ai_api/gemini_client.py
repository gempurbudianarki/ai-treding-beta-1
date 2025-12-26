import warnings
# --- SILENCE GOOGLE WARNINGS (MUTE BIAR BERSIH) ---
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
warnings.filterwarnings("ignore", category=UserWarning, module="google.generativeai")

import google.generativeai as genai
from openai import OpenAI
from loguru import logger
from core.config import settings

class GeminiClient:
    """
    MULTI-MODEL BRAIN (MegaLLM Council Edition)
    FIX: Added Warning Suppression
    """
    def __init__(self):
        # 1. SETUP MegaLLM (Primary)
        self.mega_key = settings.DEEPSEEK_API_KEY
        self.mega_base = settings.DEEPSEEK_BASE_URL
        self.mega_client = None
        self.mega_ready = False

        if self.mega_key:
            try:
                self.mega_client = OpenAI(
                    api_key=self.mega_key,
                    base_url=self.mega_base
                )
                self.mega_ready = True
                logger.info(f"✅ MegaLLM Client Ready (Access to 70+ Models)")
            except Exception as e:
                logger.error(f"❌ MegaLLM Init Failed: {e}")

        # 2. SETUP Gemini (Backup)
        self.gemini_key = settings.GEMINI_API_KEY
        self.gemini_model = settings.GEMINI_MODEL
        self.gemini_ready = False
        
        if self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                self.gemini_ai = genai.GenerativeModel(self.gemini_model)
                self.gemini_ready = True
                logger.info(f"✅ Backup Brain Ready: {self.gemini_model}")
            except Exception as e:
                logger.error(f"❌ Gemini Init Failed: {e}")

    def ask_specific_model(self, model_name: str, prompt: str) -> str:
        """
        Request spesifik ke satu model via MegaLLM.
        """
        if not self.mega_ready or not self.mega_client:
            return ""

        try:
            response = self.mega_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are an elite scalper. JSON Output Only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
                stream=False
            )
            return self._clean_json(response.choices[0].message.content)
        except Exception as e:
            logger.warning(f"⚠️ Model {model_name} Failed: {e}")
            return ""

    def analyze_text(self, text: str) -> str:
        """Default fallback ke DeepSeek"""
        return self.ask_specific_model(settings.DEEPSEEK_MODEL, text)

    def _clean_json(self, text: str) -> str:
        if not text: return "{}"
        cleaned = text.replace("```json", "").replace("```", "").strip()
        return cleaned