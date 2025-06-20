import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import ccxt
import pandas as pd
import talib
import asyncio

# --- Налаштування ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Список дозволених користувачів
AUTHORIZED_USERS = ["username1", "username2"]  # Імена користувачів Telegram
AUTHORIZED_GROUPS = [-1001234567890]  # Ідентифікатори груп

# Ініціалізація біржі
exchange = ccxt.binance()

# --- Авторизація ---
async def is_authorized(update: Update):
    user_id = update.effective_user.id
    username = update.effective_user.username
    chat_id = update.effective_chat.id

    if username not in AUTHORIZED_USERS and chat_id not in AUTHORIZED_GROUPS:
        await update.message.reply_text("❌ Доступ обмежено.")
        return False
    return True

# --- Функції для аналітики ---
async def get_historical_data(symbol, timeframe='1d', limit=100):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

async def calculate_indicators(symbol):
    df = await get_historical_data(symbol)
    rsi = talib.RSI(df['close'], timeperiod=14).iloc[-1]
    macd, macdsignal, macdhist = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    macd_value, macdsignal_value = macd.iloc[-1], macdsignal.iloc[-1]
    upper, middle, lower = talib.BBANDS(df['close'], timeperiod=20)
    bollinger_upper, bollinger_lower = upper.iloc[-1], lower.iloc[-1]
    close_price = df['close'].iloc[-1]
    return rsi, macd_value, macdsignal_value, bollinger_upper, bollinger_lower, close_price

async def analyze_market(symbol):
    rsi, macd_value, macdsignal_value, bollinger_upper, bollinger_lower, close_price = await calculate_indicators(symbol)
    
    # Логіка сигналів
    buy_signal = (rsi < 30) and (macd_value > macdsignal_value) and (close_price < bollinger_lower)
    sell_signal = (rsi > 70) and (macd_value < macdsignal_value) and (close_price > bollinger_upper)
    
    return buy_signal, sell_signal

# --- Команди ---
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update): return
    if len(context.args) == 0:
        await update.message.reply_text("Вкажи символ монети. Наприклад: /signal btcusdt")
        return
    symbol = context.args[0].upper()
    try:
        buy_signal, sell_signal = await analyze_market(symbol)
        if buy_signal:
            await update.message.reply_text(f"📈 Сигнал купівлі для {symbol}!")
        elif sell_signal:
            await update.message.reply_text(f"📉 Сигнал продажу для {symbol}!")
        else:
            await update.message.reply_text(f"🤔 Немає чітких сигналів для {symbol} на даний момент.")
    except Exception as e:
        await update.message.reply_text(f"Помилка аналізу для {symbol}: {e}")

# --- Запуск ---
def main():
    logging.basicConfig(level=logging.INFO)
    app
