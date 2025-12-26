from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """
    Konfigurasi Utama Bot V3.1 (Sniper Ready).
    Sinkron dengan main_loop.py dan env.
    """
    
    # === 1. BASIC INFO ===
    PROJECT_NAME: str = "Treding AI Gempur"
    VERSION: str = "3.1.0 (Sniper Edition)"

    # === 2. MT5 CONFIG ===
    # Pastikan path ini benar di laptop lo
    MT5_PATH: str = Field(default=r"C:\Program Files\MetaTrader 5\terminal64.exe")
    MT5_LOGIN: Optional[int] = Field(default=None)
    MT5_PASSWORD: Optional[str] = Field(default=None)
    MT5_SERVER: Optional[str] = Field(default="MetaQuotes-Demo")

    # === 3. TRADING CONFIG ===
    SYMBOL: str = Field(default="XAUUSD")
    TIMEFRAME_MINUTES: int = Field(default=15)
    DRY_RUN: bool = Field(default=True) # Set False kalau mau real trade
    TRADING_MODE: str = Field(default="SNIPER") # Mode baru

    # === 4. AI BRAIN (DEEPSEEK + GEMINI) ===
    USE_GEMINI_FOR_SENTIMENT: bool = Field(default=True)
    
    # Primary: DeepSeek (The Sniper Brain)
    DEEPSEEK_API_KEY: Optional[str] = Field(default=None)
    DEEPSEEK_MODEL: str = Field(default="deepseek-chat")
    # PENTING: Tambahan Base URL agar tidak crash
    DEEPSEEK_BASE_URL: str = Field(default="https://api.deepseek.com")
    
    # Backup: Gemini (The Evaluator)
    GEMINI_API_KEY: Optional[str] = Field(default=None)
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    # Optional Legacy
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_MODEL: str = "gpt-4-turbo-preview"

    # === 5. RISK MANAGEMENT & LOOP ===
    RISK_PER_TRADE_PCT: float = 1.0
    MAX_DAILY_DRAWDOWN_PCT: float = 3.0
    MAX_OPEN_TRADES: int = 3 # Sniper jarang trade, 3 cukup
    
    # Threshold & Loop
    TECH_CONF_THRESHOLD: float = 0.20
    LOOP_SLEEP_SECONDS: int = 15 # Dipercepat sedikit biar gak telat candle close
    MIN_BARS_REQUIRED: int = 500 # Validasi data

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = False

settings = Settings()