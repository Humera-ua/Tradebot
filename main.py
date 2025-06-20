import os
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
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
    keyboard = [[KeyboardButton("/btc"), KeyboardButton("/eth")],
                [KeyboardButton("/recommend btc"), KeyboardButton("/recommend eth")]]
    await update.message.reply_text("👋 Вітаю! Я бот для ф'ючерсної GPT-аналітики.", 
                                    reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    await update.message.reply_text(
        """📘 Список команд:
/start — запуск
/help — допомога
/btc — ціна BTC
/eth — ціна ETH
/recommend btc — аналіз BTC
/recommend eth — аналіз ETH"""
    )

async def btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    # Тестова відповідь без API біржі
    price = 65230.55
    reply = f"""📈 *BTC/USDT*
Ціна: ${price} USD
➡️ Для аналізу натисни /recommend btc"""
    await update.message.reply_text(reply, parse_mode='Markdown')

async def eth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    price = 3444.55
    reply = f"""📈 *ETH/USDT*
Ціна: ${price} USD
➡️ Для аналізу натисни /recommend eth"""
    await update.message.reply_text(reply, parse_mode='Markdown')

async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    if len(context.args) == 0:
        await update.message.reply_text("❗️ Вкажи монету. Наприклад: /recommend btc")
        return
    coin = context.args[0].upper()
    prompt = f"Аналіз ринку {coin} для ф'ючерсної торгівлі. Визнач напрям і ключові рівні."

    try:
        completion = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        response = completion.choices[0].message.content
    except Exception as e:
        response = f"⚠️ GPT помилка: {e}"

    await update.message.reply_text(
        f"""📉 GPT-аналітика для {coin}:
        
💬 {response}

✅ Сигнал підтверджено — вхід можливий.
🎯 Використовуйте TP та SL. Дотримуйтесь ризик-менеджменту.
""", parse_mode='Markdown')

# --- Запуск ---
def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("btc", btc))
    app.add_handler(CommandHandler("eth", eth))
    app.add_handler(CommandHandler("recommend", recommend))

    app.run_polling()

if __name__ == "__main__":
    main()
