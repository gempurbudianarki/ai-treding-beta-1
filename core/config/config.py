from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """
    Konfigurasi Utama Bot.
    Sinkron dengan main_loop.py dan env.
    """
    
    # === 1. BASIC INFO ===
    PROJECT_NAME: str = "Treding AI Gempur"
    VERSION: str = "3.0.0 (DeepSeek Edition)"

    # === 2. MT5 CONFIG ===
    MT5_PATH: str = Field(default=r"C:\Program Files\MetaTrader 5\terminal64.exe")
    MT5_LOGIN: Optional[int] = Field(default=None)
    MT5_PASSWORD: Optional[str] = Field(default=None)
    MT5_SERVER: Optional[str] = Field(default="MetaQuotes-Demo")

    # === 3. TRADING CONFIG ===
    SYMBOL: str = Field(default="XAUUSD")
    TIMEFRAME_MINUTES: int = Field(default=15)
    DRY_RUN: bool = Field(default=True)
    TRADING_MODE: str = Field(default="SAFE")

    # === 4. AI BRAIN (DEEPSEEK + GEMINI) ===
    USE_GEMINI_FOR_SENTIMENT: bool = Field(default=True) # Flag umum untuk AI
    
    # Primary: DeepSeek
    DEEPSEEK_API_KEY: Optional[str] = Field(default=None)
    DEEPSEEK_MODEL: str = Field(default="deepseek-chat")
    
    # Backup: Gemini
    GEMINI_API_KEY: Optional[str] = Field(default=None)
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    # Optional Legacy
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_MODEL: str = "gpt-4-turbo-preview"

    # === 5. RISK MANAGEMENT & LOOP ===
    RISK_PER_TRADE_PCT: float = 1.0
    MAX_DAILY_DRAWDOWN_PCT: float = 3.0
    MAX_OPEN_TRADES: int = 3
    
    TECH_CONF_THRESHOLD: float = 0.20
    LOOP_SLEEP_SECONDS: int = 20
    MIN_BARS_REQUIRED: int = 200

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = False

settings = Settings()