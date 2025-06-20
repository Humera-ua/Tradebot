
import os
import logging
import openai
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- Налаштування ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "humera_ua")

openai.api_key = OPENAI_API_KEY

# --- Авторизація ---
async def is_authorized(update: Update) -> bool:
    username = update.effective_user.username
    if username != OWNER_USERNAME:
        await update.message.reply_text("❌ Доступ обмежено.")
        return False
    return True

# --- Команди Telegram ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
    keyboard = [
        [KeyboardButton("/btc"), KeyboardButton("/recommend btc")],
        [KeyboardButton("/eth"), KeyboardButton("/recommend eth")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 Вітаю! Я GPT-бот для ф'ючерсної торгівлі.", reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
    await update.message.reply_text(
        """Список команд:
        /start - запуск
        /help - допомога
        /btc - ціна BTC
        /recommend btc - аналіз монети
        /eth
        /recommend eth"""
    )
async def btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
    try:
        import requests
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        price = response.json()["bitcoin"]["usd"]
        reply = (
            f"📈 *BTC/USDT*\n"
            f"💰 Поточна ціна: {price:.2f} USDT\n"
            f"Щоб отримати аналітику - тисни кнопку"
        await update.message.reply_text(reply, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Помилка отримання ціни BTC: {e}")

async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update):
        return
    if len(context.args) == 0:
        await update.message.reply_text("❗ Вкажи монету. Наприклад: /recommend btc")
        return
    coin = context.args[0].upper()
    prompt = f"Проаналізуй монету {coin} для ф'ючерсної торгівлі. Дай короткий коментар з точки зору трейдингу."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        gpt_reply = response.choices[0].message["content"]
        await update.message.reply_text(f"📉 GPT-аналітика для {coin}:

{gpt_reply}")
    except Exception as e:
        await update.message.reply_text(f"GPT помилка: {e}")

# --- Запуск ---
def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("btc", btc))
    app.add_handler(CommandHandler("recommend", recommend))

    app.run_polling()

if __name__ == "__main__":
    main()
