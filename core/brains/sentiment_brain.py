import os
from loguru import logger
from ai_api.gemini_client import GeminiClient
from core.feeder.news_feeder import NewsFeeder
from core.config import settings


class SentimentBrain:
    """
    Ambil news → analisa sentiment → return dict
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", None)
        self.gemini = GeminiClient()
        self.news = NewsFeeder()
        logger.info("SentimentBrain v2 initialized")

    def analyze(self):
        """
        Fetch & analyze news
        """
        symbol = settings.SYMBOL  # === FIX DI SINI ===

        # --- Ambil berita ---
        headlines = self.news.get_recent_headlines(symbol=symbol, limit=6)

        if not headlines:
            return {
                "sentiment": "neutral",
                "confidence": 0.1,
                "reason": "no_news"
            }

        text = "\n".join(headlines)

        logger.debug("SentimentBrain: analyzing sentiment via Gemini...")

        # --- Analisa menggunakan AI ---
        try:
            result = self.gemini.analyze_text(
                f"Analyze financial sentiment from these headlines:\n{text}"
            )

            res = result.lower()

            if any(w in res for w in ["bull", "up", "buy", "rally"]):
                return {
                    "sentiment": "bullish",
                    "confidence": 0.7,
                    "reason": "ai_bullish",
                    "headlines": len(headlines)
                }

            elif any(w in res for w in ["bear", "down", "sell", "drop"]):
                return {
                    "sentiment": "bearish",
                    "confidence": 0.7,
                    "reason": "ai_bearish",
                    "headlines": len(headlines)
                }

            else:
                return {
                    "sentiment": "neutral",
                    "confidence": 0.4,
                    "reason": "ai_neutral",
                    "headlines": len(headlines)
                }

        except Exception as e:
            logger.error(f"SentimentBrain Error: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.1,
                "reason": "exception"
            }
