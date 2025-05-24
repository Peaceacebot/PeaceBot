import logging
import ccxt
import requests
import pandas as pd
import numpy as np
import os
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

# Ambil token dan chat ID dari environment variable
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID", "")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_data():
    binance = ccxt.binance()
    bars = binance.fetch_ohlcv('XAU/USDT', timeframe='15m', limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['close'] = pd.to_numeric(df['close'])
    return df

def analyze(df):
    rsi = RSIIndicator(df['close'], window=14).rsi()
    macd = MACD(df['close']).macd_diff()
    ema_fast = EMAIndicator(df['close'], window=12).ema_indicator()
    ema_slow = EMAIndicator(df['close'], window=26).ema_indicator()

    signal = ""
    if rsi.iloc[-1] < 30 and macd.iloc[-1] > 0 and ema_fast.iloc[-1] > ema_slow.iloc[-1]:
        signal = "BUY"
    elif rsi.iloc[-1] > 70 and macd.iloc[-1] < 0 and ema_fast.iloc[-1] < ema_slow.iloc[-1]:
        signal = "SELL"
    return signal

def send_signal(signal):
    if signal:
        text = f"**PeaceBot Sinyal Baru - XAU/USD**\nSinyal: {signal}\nIndikator: RSI, MACD, EMA"
        requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage", params={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "Markdown"
        })

def auto_signal():
    try:
        df = fetch_data()
        signal = analyze(df)
        send_signal(signal)
    except Exception as e:
        logger.error(f"Gagal mengambil sinyal: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Selamat datang di PeaceBot! Saya akan memberi sinyal beli/jual untuk XAU/USD.")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("PeaceBot menggunakan indikator RSI, MACD, dan EMA crossover untuk mengirim sinyal jual/beli otomatis setiap 15 menit.")

async def sinyal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    df = fetch_data()
    signal = analyze(df)
    if signal:
        await update.message.reply_text(f"Sinyal terkini untuk XAU/USD: {signal}")
    else:
        await update.message.reply_text("Belum ada sinyal baru saat ini.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("sinyal", sinyal))

    scheduler = BackgroundScheduler()
    scheduler.add_job(auto_signal, 'interval', minutes=15)
    scheduler.start()

    app.run_polling()

if __name__ == "__main__":
    main()
