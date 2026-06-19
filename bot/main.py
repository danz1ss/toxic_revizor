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
from bot.memory import MemoryManager
from bot.middlewares import ThrottlingMiddleware


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
    logger.info("  [BOT] Токсичный Ревизор — запуск!")
    logger.info("  LLM Provider: %s", config.llm_provider)
    logger.info("=" * 50)

    # Create LLM client
    llm_client = create_llm_client(config)

    # Setup proxy if provided
    session = None
    if config.proxy_url:
        from aiogram.client.session.aiohttp import AiohttpSession
        session = AiohttpSession(proxy=config.proxy_url)
        logger.info(f"  Proxy configured: {config.proxy_url}")

    # Create bot and dispatcher
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=None),
        session=session,
    )
    dp = Dispatcher()

    # Register router
    dp.include_router(router)

    # Initialize MemoryManager
    memory = MemoryManager()
    
    # Register middlewares
    dp.message.middleware(ThrottlingMiddleware(limit_seconds=10))

    # Inject dependencies into handler context
    dp["llm_client"] = llm_client
    dp["memory"] = memory

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
