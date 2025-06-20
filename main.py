import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import openai

# --- Налаштування ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "humera_ua")
openai.api_key = OPENAI_API_KEY

# --- Авторизація ---
async def is_authorized(update: Update):
    username = update.effective_user.username
    if username != OWNER_USERNAME:
        await update.message.reply_text("❌ Доступ обмежено.")
        return False
    return True

# --- Команди ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    await update.message.reply_text("👋 Вітаю! Я GPT-бот для ф'ючерсної торгівлі.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    await update.message.reply_text(
        "📘 Список команд:\n"
        "/start - запуск\n"
        "/help - допомога\n"
        "/btc - ціна BTC\n"
        "/eth - ціна ETH\n"
        "/recommend btc - аналіз монети"
    )

async def btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    await update.message.reply_text("📈 BTC/USDT\nЦіна: $XXX (тестова відповідь)")

async def eth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    await update.message.reply_text("📈 ETH/USDT\nЦіна: $XXX (тестова відповідь)")

async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    if len(context.args) == 0:
        await update.message.reply_text("Вкажи монету. Наприклад: /recommend btc")
        return
    symbol = context.args[0].upper()
    prompt = f"Проаналізуй ринок {symbol} для ф'ючерсної торгівлі."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"⚠ GPT помилка: {e}"

    await update.message.reply_text(
        f"📉 GPT-аналітика для {symbol}:\n{reply}"
    )

# --- Запуск ---
def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("btc", btc))
    app.add_handler(CommandHandler("eth", eth))
    app.add_handler(CommandHandler("recommend", recommend))

    app.run_polling()  # без asyncio.run

if __name__ == "_main_":
    main()
