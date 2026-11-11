import requests
from bs4 import BeautifulSoup
import telebot

BOT_TOKEN = 8722087403:AAFBImlnIxE5p_MjJrVxj5UHIzVFqG5lZ8g

bot = telebot.TeleBot(BOT_TOKEN)

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
        return f"ما قدرت أجيب الترند الحين: {e}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 أهلاً بك!\n\n/start - ترحيب\n/trend - ترند السعودية")

@bot.message_handler(commands=['trend'])
def trend(message):
    bot.reply_to(message, get_trends())

@bot.message_handler(func=lambda m: True)
def any_msg(message):
    if "ترند" in message.text:
        bot.reply_to(message, get_trends())
    else:
        bot.reply_to(message, "اكتب /trend")

print("Bot is running...")
bot.infinity_polling()
