from typing import Optional

from loguru import logger
from openai import OpenAI

from config.settings import settings


class GPTClient:
    """
    Wrapper sederhana untuk OpenAI GPT.
    Kalau API key tidak ada, dia fallback ke mode dummy (balikkan jawaban default).
    """

    def __init__(self) -> None:
        self.api_key: Optional[str] = settings.OPENAI_API_KEY
        self.model: str = settings.OPENAI_MODEL
        self.client: Optional[OpenAI] = None

        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("GPTClient initialized with OpenAI model: {}", self.model)
        else:
            logger.warning("OPENAI_API_KEY tidak ditemukan. GPTClient akan jalan di mode dummy.")

    def analyze_text(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generic text analysis.
        """
        if not self.client:
            logger.debug("GPTClient dummy mode - no API key. Returning fallback response.")
            return "neutral"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            logger.error("Error calling GPT API: {}", e)
            return "error"


gpt_client = GPTClient()
