
import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
import statistics

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# RapidAPI key dan endpoint untuk TradingView (XAU/USD)
RAPIDAPI_KEY = "YOUR_RAPIDAPI_KEY"
headers = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "tradingview-com.p.rapidapi.com"
}

def get_price():
    url = "https://tradingview-com.p.rapidapi.com/markets/forex/quotes"
    querystring = {"symbols":"FOREX%3AXAUUSD"}
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    return data["quotes"][0]["price"]

def calculate_signal(prices):
    rsi = calculate_rsi(prices)
    if rsi < 30:
        return "BUY", rsi
    elif rsi > 70:
        return "SELL", rsi
    else:
        return "WAIT", rsi

def calculate_rsi(prices, period=14):
    deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
    gains = [delta for delta in deltas if delta > 0]
    losses = [-delta for delta in deltas if delta < 0]
    average_gain = sum(gains[-period:]) / period if gains else 0
    average_loss = sum(losses[-period:]) / period if losses else 1
    rs = average_gain / average_loss
    return 100 - (100 / (1 + rs))

async def sinyal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        prices = [get_price() for _ in range(20)]
        signal, rsi = calculate_signal(prices)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"PeaceBot Signal:\nHarga XAU/USD: {prices[-1]:.2f}\nRSI: {rsi:.2f}\nSinyal: {signal}")
    except Exception as e:
        logging.error(f"Gagal mengambil sinyal: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Terjadi kesalahan saat mengambil sinyal.")

def run_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: app.bot.send_message(chat_id=CHAT_ID, text="PeaceBot aktif..."), 'interval', minutes=120)
    scheduler.start()

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("sinyal", sinyal))
    run_scheduler(app)
    app.run_polling()
