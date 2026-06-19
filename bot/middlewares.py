"""
Токсичный Ревизор — Middlewares
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

logger = logging.getLogger(__name__)

class ThrottlingMiddleware(BaseMiddleware):
    """Ограничивает частоту сообщений от одного пользователя."""

    def __init__(self, limit_seconds: int = 10):
        super().__init__()
        self.limit = timedelta(seconds=limit_seconds)
        self.user_timestamps: Dict[int, datetime] = {}
        self.notified: Dict[int, bool] = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not event.from_user:
            return await handler(event, data)

        user_id = event.from_user.id
        now = datetime.now()

        last_time = self.user_timestamps.get(user_id)
        
        if last_time and (now - last_time) < self.limit:
            # Юзер спамит
            logger.info("User %s is rate-limited.", user_id)
            if not self.notified.get(user_id, False):
                self.notified[user_id] = True
                await event.reply("🛑 Не спамь! Мои гениальные нейроны перегружены. Подожди 10 секунд.")
            return
            
        # Записываем новое время
        self.user_timestamps[user_id] = now
        self.notified[user_id] = False
        return await handler(event, data)
