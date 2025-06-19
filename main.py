import os
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import openai
import requests

# --- Налаштування ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "humera_ua")
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"

openai.api_key = OPENAI_API_KEY

SUPPORTED_COINS = ["BTC", "ETH", "SOL", "AVAX", "MATIC", "XRP", "DOGE", "OP", "INJ"]

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
    keyboard = [
        [KeyboardButton("/price BTC"), KeyboardButton("/price ETH")],
        [KeyboardButton("/recommend BTC"), KeyboardButton("/recommend SOL")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 Вітаю! Обери команду:", reply_markup=reply_markup)

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    if len(context.args) == 0:
        await update.message.reply_text("Вкажи монету. Наприклад: /price BTC")
        return
    coin = context.args[0].upper()
    if coin not in SUPPORTED_COINS:
        await update.message.reply_text("Монета не підтримується.")
        return
    try:
        r = requests.get(COINGECKO_URL, params={"ids": coin.lower(), "vs_currencies": "usd"})
        data = r.json()
        price = data[coin.lower()]["usd"]
        await update.message.reply_text(f"📈 {coin}/USDT\n💰 Поточна ціна: ${price}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Помилка при отриманні ціни {coin}/USDT: {str(e)}")

async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    if len(context.args) == 0:
        await update.message.reply_text("Вкажи монету. Наприклад: /recommend BTC")
        return
    coin = context.args[0].upper()
    prompt = f"Проаналізуй монету {coin} для ф'ючерсної торгівлі. Дай короткий коментар щодо тренду, точки входу, TP і SL."

    try:
        completion = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        response = completion.choices[0].message.content
        await update.message.reply_text(f"📉 GPT-аналітика для {coin}:\n\n{response}")
    except Exception as e:
        await update.message.reply_text(f"GPT помилка: {str(e)}")

# --- Запуск ---
def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("recommend", recommend))

    app.run_polling()

if __name__ == "__main__":
    main()
