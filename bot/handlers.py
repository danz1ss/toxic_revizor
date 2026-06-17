"""
Токсичный Ревизор — Обработчики сообщений Telegram

Принимает фото домашки, текстовые сообщения и команды.
"""

from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.prompts import ERROR_MESSAGES, PROCESSING_PHRASES

if TYPE_CHECKING:
    from bot.llm_client import BaseLLMClient

logger = logging.getLogger(__name__)

router = Router(name="homework")


# ─────────────────────────────────────────────────────
# /start
# ─────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Welcome message."""
    await message.answer(
        "👋 Йоу! Я — *Токсичный Ревизор* 🤖\n\n"
        "Скинь мне фото своей домашки по математике, "
        "и я скажу тебе всё, что думаю о твоём решении.\n\n"
        "⚠️ *Предупреждение:* Я не буду нежным.\n\n"
        "📸 Просто отправь фото тетради — и поехали!\n"
        "📝 Или напиши текст задачи/решения.\n\n"
        "Команды:\n"
        "/start — это сообщение\n"
        "/help — как пользоваться",
        parse_mode="Markdown",
    )


# ─────────────────────────────────────────────────────
# /help
# ─────────────────────────────────────────────────────

@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Help message."""
    await message.answer(
        "📖 *Как пользоваться Токсичным Ревизором:*\n\n"
        "1️⃣ Сфотографируй решение задачи в тетради\n"
        "2️⃣ Отправь фото сюда\n"
        "3️⃣ Получи разбор с дозой здорового сарказма\n\n"
        "💡 *Советы для лучшего результата:*\n"
        "• Фотографируй при хорошем освещении\n"
        "• Старайся, чтобы текст был чётким\n"
        "• Одна задача = одно фото\n\n"
        "📝 Также можешь просто написать решение текстом.\n\n"
        "🔧 Бот поддерживает: алгебру, геометрию, "
        "арифметику, тригонометрию, начала анализа.",
        parse_mode="Markdown",
    )


# ─────────────────────────────────────────────────────
# Photo handler
# ─────────────────────────────────────────────────────

@router.message(F.photo)
async def handle_photo(message: Message, llm_client: BaseLLMClient) -> None:
    """Process a photo of homework."""
    # Send a fun "processing" message
    processing_msg = await message.answer(random.choice(PROCESSING_PHRASES))

    try:
        # Get the highest resolution photo
        photo = message.photo[-1]  # Last element = highest resolution
        file = await message.bot.get_file(photo.file_id)
        file_bytes: bytearray = await message.bot.download_file(file.file_path)
        image_data = bytes(file_bytes.read() if hasattr(file_bytes, 'read') else file_bytes)

        logger.info(
            "Processing photo from user %s (size: %s bytes)",
            message.from_user.id if message.from_user else "unknown",
            len(image_data),
        )

        # Analyze with LLM
        result = await llm_client.analyze_image(image_data)

        # Delete "processing" message and send result
        await processing_msg.delete()
        await message.reply(result, parse_mode="Markdown")

    except Exception:
        logger.exception("Error processing photo")
        await processing_msg.delete()
        await message.reply(ERROR_MESSAGES["api_error"])


# ─────────────────────────────────────────────────────
# Document/file handler (for high-res images sent as files)
# ─────────────────────────────────────────────────────

@router.message(F.document.mime_type.startswith("image/"))
async def handle_document_image(message: Message, llm_client: BaseLLMClient) -> None:
    """Process images sent as documents (uncompressed)."""
    processing_msg = await message.answer(random.choice(PROCESSING_PHRASES))

    try:
        doc = message.document
        if doc.file_size and doc.file_size > 20 * 1024 * 1024:  # 20 MB limit
            await processing_msg.delete()
            await message.reply(ERROR_MESSAGES["image_too_large"])
            return

        file = await message.bot.get_file(doc.file_id)
        file_bytes = await message.bot.download_file(file.file_path)
        image_data = bytes(file_bytes.read() if hasattr(file_bytes, 'read') else file_bytes)

        logger.info(
            "Processing document image from user %s (size: %s bytes)",
            message.from_user.id if message.from_user else "unknown",
            len(image_data),
        )

        result = await llm_client.analyze_image(image_data)

        await processing_msg.delete()
        await message.reply(result, parse_mode="Markdown")

    except Exception:
        logger.exception("Error processing document image")
        await processing_msg.delete()
        await message.reply(ERROR_MESSAGES["api_error"])


# ─────────────────────────────────────────────────────
# Text message handler
# ─────────────────────────────────────────────────────

@router.message(F.text)
async def handle_text(message: Message, llm_client: BaseLLMClient) -> None:
    """Process text messages — could be typed-out solutions."""
    text = message.text.strip()
    if not text:
        return

    # Ignore very short messages (likely accidental)
    if len(text) < 5:
        await message.reply(
            "🤨 Это что, шифровка? Напиши нормально или скинь фотку решения."
        )
        return

    processing_msg = await message.answer(random.choice(PROCESSING_PHRASES))

    try:
        logger.info(
            "Processing text from user %s (%d chars)",
            message.from_user.id if message.from_user else "unknown",
            len(text),
        )

        result = await llm_client.analyze_text(text)

        await processing_msg.delete()
        await message.reply(result, parse_mode="Markdown")

    except Exception:
        logger.exception("Error processing text")
        await processing_msg.delete()
        await message.reply(ERROR_MESSAGES["api_error"])
