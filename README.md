# 🤖 Токсичный Ревизор

> Саркастичный Telegram-бот, который проверяет домашку по математике и жёстко, но смешно комментирует ошибки.

Отправь фото тетради → получи математически точный, но токсичный разбор.

---

## 🚀 Быстрый старт

### 1. Создай Telegram-бота

Открой [@BotFather](https://t.me/BotFather) в Telegram и создай нового бота командой `/newbot`.
Сохрани полученный **токен**.

### 2. Получи API-ключ LLM

**Вариант A — Google Gemini (бесплатно, рекомендуется):**
- Перейди на [Google AI Studio](https://aistudio.google.com/apikey)
- Создай API-ключ

**Вариант B — OpenAI:**
- Перейди на [OpenAI Platform](https://platform.openai.com/api-keys)
- Создай API-ключ (платный)

### 3. Настрой окружение

```bash
# Скопируй шаблон конфига
cp .env.example .env

# Отредактируй .env — вставь свои ключи
```

### 4. Запуск

#### Вариант A: Docker (рекомендуется)

```bash
docker compose up -d
```

#### Вариант B: Локально (Python 3.11+)

```bash
# Создай виртуальное окружение
python -m venv .venv

# Активируй его
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Установи зависимости
pip install -r requirements.txt

# Запуск
python -m bot.main
```

---

## 📸 Как пользоваться

1. Открой своего бота в Telegram
2. Нажми `/start`
3. Отправь фото решения задачи
4. Получи разбор 🔥

Бот также принимает **текстовые сообщения** с решениями.

---

## 🏗️ Структура проекта

```
Project 1/
├── bot/
│   ├── __init__.py       # Пакет
│   ├── main.py           # Точка входа, запуск бота
│   ├── config.py         # Конфигурация из .env
│   ├── handlers.py       # Обработчики сообщений Telegram
│   ├── llm_client.py     # Клиент LLM API (Gemini / OpenAI)
│   └── prompts.py        # Системные промпты и тексты
├── Dockerfile            # Docker-образ
├── docker-compose.yml    # Docker Compose конфиг
├── requirements.txt      # Python-зависимости
├── .env.example          # Шаблон конфигурации
├── .gitignore
└── README.md
```

---

## ⚙️ Конфигурация

| Переменная | Описание | По умолчанию |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Токен бота от @BotFather | *обязательно* |
| `LLM_PROVIDER` | `gemini` или `openai` | `gemini` |
| `GEMINI_API_KEY` | API-ключ Google Gemini | — |
| `GEMINI_MODEL` | Модель Gemini | `gemini-2.0-flash` |
| `OPENAI_API_KEY` | API-ключ OpenAI | — |
| `OPENAI_MODEL` | Модель OpenAI | `gpt-4o-mini` |
| `MAX_IMAGE_SIZE` | Макс. размер фото (px) | `1600` |
| `LLM_TEMPERATURE` | Креативность (0.0–2.0) | `1.0` |
| `LLM_MAX_TOKENS` | Макс. длина ответа | `1500` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |

---

## 🎭 Настройка тона

Отредактируй `SYSTEM_PROMPT` в файле `bot/prompts.py`, чтобы изменить:
- Уровень токсичности
- Стиль юмора
- Формат ответов
- Используемый сленг

---

## 📜 Лицензия

MIT
