import os
from typing import Optional

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)


class Settings:
    """
    Semua konfigurasi global bot.
    Ubah di sini kalau mau tuning.
    """

    # --- MODE BOT ---
    # DRY_RUN = True -> tidak kirim order ke MT5, cuma log
    # DRY_RUN = False -> beneran kirim order (hati-hati)
    DRY_RUN: bool = os.getenv("DRY_RUN", "true").lower() == "true"

    # --- SYMBOL & TIMEFRAME ---
    # Kita fokus XAUUSD (Gold) dulu
    SYMBOL: str = os.getenv("SYMBOL", "XAUUSD")
    TIMEFRAME_MINUTES: int = int(os.getenv("TIMEFRAME_MINUTES", "15"))

    # --- MT5 CONFIG ---
    MT5_LOGIN: Optional[int] = (
        int(os.getenv("MT5_LOGIN")) if os.getenv("MT5_LOGIN") else None
    )
    MT5_PASSWORD: Optional[str] = os.getenv("MT5_PASSWORD")
    MT5_SERVER: Optional[str] = os.getenv("MT5_SERVER")
    MT5_PATH: Optional[str] = os.getenv("MT5_PATH")  # path terminal MT5 kalau perlu

    # --- RISK CONFIG ---
    ACCOUNT_CURRENCY: str = os.getenv("ACCOUNT_CURRENCY", "USD")
    RISK_PER_TRADE_PCT: float = float(os.getenv("RISK_PER_TRADE_PCT", "1.0"))
    MAX_DAILY_DRAWDOWN_PCT: float = float(os.getenv("MAX_DAILY_DRAWDOWN_PCT", "3.0"))
    MAX_OPEN_TRADES: int = int(os.getenv("MAX_OPEN_TRADES", "3"))

    # --- AI CONFIG ---
    USE_GEMINI_FOR_SENTIMENT: bool = (
        os.getenv("USE_GEMINI_FOR_SENTIMENT", "true").lower() == "true"
    )

    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")

    # Model yang mau dipakai
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # --- LOOP CONFIG ---
    LOOP_SLEEP_SECONDS: int = int(os.getenv("LOOP_SLEEP_SECONDS", "60"))
    MIN_BARS_REQUIRED: int = int(os.getenv("MIN_BARS_REQUIRED", "200"))


settings = Settings()
