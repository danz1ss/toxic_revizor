"""
Токсичный Ревизор — Управление состоянием (Память)
"""

import logging
from typing import Dict, List, TypedDict

logger = logging.getLogger(__name__)

class MessageDict(TypedDict):
    role: str
    content: str

class MemoryManager:
    """Простой In-Memory менеджер истории диалогов."""

    def __init__(self, max_history: int = 6):
        # max_history должно быть четным, чтобы хранить пары запрос-ответ.
        self._history: Dict[int, List[MessageDict]] = {}
        self.max_history = max_history

    def get_history(self, user_id: int) -> List[MessageDict]:
        """Получить историю сообщений пользователя."""
        return self._history.get(user_id, [])

    def add_message(self, user_id: int, role: str, content: str) -> None:
        """Добавить сообщение в историю (role: 'user' или 'assistant')."""
        if user_id not in self._history:
            self._history[user_id] = []
        
        self._history[user_id].append({"role": role, "content": content})
        
        # Оставляем только последние max_history сообщений
        if len(self._history[user_id]) > self.max_history:
            self._history[user_id] = self._history[user_id][-self.max_history:]

    def clear(self, user_id: int) -> None:
        """Очистить историю пользователя."""
        if user_id in self._history:
            del self._history[user_id]
