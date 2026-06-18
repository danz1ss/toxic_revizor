"""
Токсичный Ревизор — Конфигурация приложения
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    """Immutable application configuration loaded from environment."""

    # Telegram
    bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))

    # LLM provider: "gemini" | "openai"
    llm_provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "gemini").lower())

    # Gemini
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))

    # OpenAI
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", ""))

    # Image processing
    max_image_size: int = field(
        default_factory=lambda: int(os.getenv("MAX_IMAGE_SIZE", "1600"))
    )

    # Generation params
    temperature: float = field(
        default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "1.0"))
    )
    max_tokens: int = field(
        default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "1500"))
    )

    # Logging
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # Proxy
    proxy_url: str = field(default_factory=lambda: os.getenv("PROXY_URL", ""))

    def validate(self) -> None:
        """Raise ValueError if critical settings are missing."""
        if not self.bot_token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN не задан! Получи его у @BotFather в Telegram."
            )

        if self.llm_provider == "gemini" and not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY не задан! Получи бесплатный ключ: "
                "https://aistudio.google.com/apikey"
            )

        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY не задан! Получи ключ: "
                "https://platform.openai.com/api-keys"
            )

        if self.llm_provider not in ("gemini", "openai"):
            raise ValueError(
                f"LLM_PROVIDER='{self.llm_provider}' не поддерживается. "
                "Используй 'gemini' или 'openai'."
            )
