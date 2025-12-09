from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Treding AI Gempur"
    VERSION: str = "20.0.0 (SWING SNIPER)"

    # MT5
    MT5_PATH: str = Field(default=r"C:\Program Files\MetaTrader 5\terminal64.exe")
    MT5_LOGIN: Optional[int] = Field(default=None)
    MT5_PASSWORD: Optional[str] = Field(default=None)
    MT5_SERVER: Optional[str] = Field(default="MetaQuotes-Demo")

    # TRADING
    SYMBOL: str = Field(default="XAUUSDm")
    # Ganti Default jadi 15
    TIMEFRAME_MINUTES: int = Field(default=15)
    DRY_RUN: bool = Field(default=True)
    # Ganti Default jadi SWING_M15
    TRADING_MODE: str = Field(default="SWING_M15")

    # AI BRAIN
    USE_GEMINI_FOR_SENTIMENT: bool = Field(default=True) 
    DEEPSEEK_API_KEY: Optional[str] = Field(default=None)
    DEEPSEEK_BASE_URL: str = Field(default="https://api.megallm.io/v1")
    DEEPSEEK_MODEL: str = Field(default="gpt-4o-mini")
    
    # Duo Models
    MODEL_DEEPSEEK: str = Field(default="deepseek-ai/deepseek-v3.1")
    MODEL_QWEN: str = Field(default="qwen/qwen3-next-80b-a3b-instruct")
    MODEL_EVALUATOR: str = Field(default="gemini-2.0-flash")

    GEMINI_API_KEY: Optional[str] = Field(default=None)
    GEMINI_MODEL: str = Field(default="gemini-2.0-flash")
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview")

    # RISK
    RISK_PER_TRADE_PCT: float = 1.0
    MAX_DAILY_DRAWDOWN_PCT: float = 3.0
    MAX_OPEN_TRADES: int = 5
    TECH_CONF_THRESHOLD: float = 0.20
    
    # Ganti Default jadi 20 detik (Swing gak perlu 1 detik)
    LOOP_SLEEP_SECONDS: int = Field(default=20) 
    MIN_BARS_REQUIRED: int = 200

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = False

settings = Settings()