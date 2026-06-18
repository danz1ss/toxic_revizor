"""
Токсичный Ревизор — Клиент для LLM API

Поддерживает Google Gemini и OpenAI GPT-4o.
Оба провайдера принимают изображения напрямую (vision),
поэтому отдельный OCR не нужен.
"""

from __future__ import annotations

import base64
import io
import logging
import re
from abc import ABC, abstractmethod

from PIL import Image

from bot.config import Config
from bot.prompts import SYSTEM_PROMPT, TEXT_TASK_PROMPT

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────
# Image pre-processing
# ─────────────────────────────────────────────────────

def prepare_image(image_bytes: bytes, max_size: int = 1600) -> tuple[bytes, str]:
    """
    Resize image if needed and convert to JPEG for efficient API transfer.
    Returns (jpeg_bytes, mime_type).
    """
    img = Image.open(io.BytesIO(image_bytes))

    # Convert RGBA/palette to RGB
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")

    # Resize if too large
    w, h = img.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        img = img.resize(new_size, Image.LANCZOS)
        logger.debug("Image resized from %sx%s to %sx%s", w, h, *new_size)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue(), "image/jpeg"

def clean_response(text: str) -> str:
    """Remove <thought>...</thought> blocks from the response."""
    return re.sub(r'<thought>.*?</thought>', '', text, flags=re.DOTALL).strip()

# ─────────────────────────────────────────────────────
# Abstract base
# ─────────────────────────────────────────────────────

class BaseLLMClient(ABC):
    """Abstract LLM client interface."""

    @abstractmethod
    async def analyze_image(self, image_bytes: bytes) -> str:
        """Analyze a photo of homework and return sarcastic review."""
        ...

    @abstractmethod
    async def analyze_text(self, text: str) -> str:
        """Analyze text-based homework and return sarcastic review."""
        ...


# ─────────────────────────────────────────────────────
# Google Gemini
# ─────────────────────────────────────────────────────

class GeminiClient(BaseLLMClient):
    """Google Gemini API client with vision support."""

    def __init__(self, config: Config) -> None:
        from google import genai

        self._client = genai.Client(api_key=config.gemini_api_key)
        self._model = config.gemini_model
        self._temperature = config.temperature
        self._max_tokens = config.max_tokens
        self._max_image_size = config.max_image_size

    async def analyze_image(self, image_bytes: bytes) -> str:
        from google.genai import types

        jpeg_bytes, mime = prepare_image(image_bytes, self._max_image_size)

        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            inline_data=types.Blob(mime_type=mime, data=jpeg_bytes)
                        ),
                        types.Part(
                            text="Проверь это решение. Найди ошибки и прокомментируй."
                        ),
                    ],
                ),
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=self._temperature,
                max_output_tokens=self._max_tokens,
            ),
        )
        return clean_response(response.text) if response.text else "🤖 Что-то пошло не так, ответ пустой."

    async def analyze_text(self, text: str) -> str:
        from google.genai import types

        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part(text=f"{TEXT_TASK_PROMPT}\n\n---\n\n{text}"),
                    ],
                ),
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=self._temperature,
                max_output_tokens=self._max_tokens,
            ),
        )
        return clean_response(response.text) if response.text else "🤖 Что-то пошло не так, ответ пустой."


# ─────────────────────────────────────────────────────
# OpenAI GPT-4o
# ─────────────────────────────────────────────────────

class OpenAIClient(BaseLLMClient):
    """OpenAI API client with vision support (GPT-4o / GPT-4o-mini)."""

    def __init__(self, config: Config) -> None:
        from openai import AsyncOpenAI

        kwargs = {"api_key": config.openai_api_key}
        if config.openai_base_url:
            kwargs["base_url"] = config.openai_base_url
        self._client = AsyncOpenAI(**kwargs)
        self._model = config.openai_model
        self._temperature = config.temperature
        self._max_tokens = config.max_tokens
        self._max_image_size = config.max_image_size

    async def analyze_image(self, image_bytes: bytes) -> str:
        jpeg_bytes, mime = prepare_image(image_bytes, self._max_image_size)
        b64 = base64.b64encode(jpeg_bytes).decode()

        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime};base64,{b64}",
                                "detail": "high",
                            },
                        },
                        {
                            "type": "text",
                            "text": "Проверь это решение. Найди ошибки и прокомментируй.",
                        },
                    ],
                },
            ],
        )
        ans = response.choices[0].message.content
        return clean_response(ans) if ans else "🤖 Что-то пошло не так."

    async def analyze_text(self, text: str) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{TEXT_TASK_PROMPT}\n\n---\n\n{text}"},
            ],
        )
        ans = response.choices[0].message.content
        return clean_response(ans) if ans else "🤖 Что-то пошло не так."


# ─────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────

def create_llm_client(config: Config) -> BaseLLMClient:
    """Create the appropriate LLM client based on config."""
    if config.llm_provider == "gemini":
        logger.info("Using Google Gemini (%s)", config.gemini_model)
        return GeminiClient(config)
    elif config.llm_provider == "openai":
        logger.info("Using OpenAI (%s)", config.openai_model)
        return OpenAIClient(config)
    else:
        raise ValueError(f"Unknown LLM provider: {config.llm_provider}")
