import os
import threading
import requests
from bs4 import BeautifulSoup
import telebot
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise Exception("حط BOT_TOKEN في Environment Variables في Render")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!"

def get_trends():
    try:
        url = "https://getdaytrends.com/saudi-arabia/"
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        trends = soup.select('.trend-list a') or soup.select('td a')
        msg = "🇸🇦 ترند السعودية الآن:\n\n"
        for i, t in enumerate(trends[:15], 1):
            msg += f"{i}. {t.text.strip()}\n"
        return msg
    except Exception as e:
        return f"ما قدرت أجيب الترند: {e}"

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🔥 أهلاً بك!\n/start - ترحيب\n/trend - ترند السعودية")

@bot.message_handler(commands=['trend'])
def trend(m):
    bot.reply_to(m, get_trends())

@bot.message_handler(func=lambda m: True)
def any_msg(m):
    if "ترند" in m.text:
        bot.reply_to(m, get_trends())
    else:
        bot.reply_to(m, "اكتب /trend")

def run_bot():
    print("Bot is running...")
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
