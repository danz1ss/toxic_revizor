"""
Токсичный Ревизор — Точка входа

Саркастичный бот-чекер домашки по математике.
Отправь ему фото решения, и он найдёт ошибку
и прокомментирует её в стиле токсичного стендапера.
"""

from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot.config import Config
from bot.handlers import router
from bot.llm_client import create_llm_client


def setup_logging(level: str) -> None:
    """Configure structured logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    # Suppress noisy third-party loggers
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)


async def main() -> None:
    """Application entry point."""
    # Load and validate config
    config = Config()
    config.validate()

    setup_logging(config.log_level)
    logger = logging.getLogger(__name__)

    logger.info("=" * 50)
    logger.info("  🤖 Токсичный Ревизор — запуск!")
    logger.info("  LLM Provider: %s", config.llm_provider)
    logger.info("=" * 50)

    # Create LLM client
    llm_client = create_llm_client(config)

    # Create bot and dispatcher
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=None),
    )
    dp = Dispatcher()

    # Register router
    dp.include_router(router)

    # Inject llm_client into handler context
    dp["llm_client"] = llm_client

    # Start polling
    logger.info("Bot is starting polling...")
    try:
        await dp.start_polling(bot, allowed_updates=["message"])
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
