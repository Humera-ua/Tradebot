# Futures GPT Bot 🤖📈

Цей Telegram-бот надає сигнали, аналітику та ціну по ф'ючерсним монетам (BTC, ETH, SOL тощо) з GPT-аналітикою та CoinGecko API.

## 🔧 Встановлення

1. Склонуйте репозиторій або зробіть fork
2. Створіть `.env` файл на основі `.env.example`
3. Залийте на [Render.com](https://render.com)

## 🛠️ Команди

- `/start` — запуск та меню
- `/price BTC` — поточна ціна
- `/recommend ETH` — GPT-аналітика

## 📦 Залежності
- Python 3.11
- python-telegram-bot
- openai
- requests

## 🧠 GPT
Використовує `gpt-4` для створення торгових підказок.
