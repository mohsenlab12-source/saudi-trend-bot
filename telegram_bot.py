import os
import threading
import requests
from bs4 import BeautifulSoup
import telebot
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Saudi Trend Bot V2 is Live! 🇸🇦"

def get_trends(city="saudi-arabia"):
    cities = {
        "saudi-arabia": "السعودية",
        "riyadh": "الرياض",
        "jeddah": "جدة",
        "dammam": "الشرقية"
    }
    try:
        url = f"https://getdaytrends.com/{city}/"
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        trends = soup.select('.trend-list a') or soup.select('td a')
        
        city_name = cities.get(city, city)
        msg = f"🇸🇦 <b>ترند {city_name} الآن:</b>\n\n"
        for i, t in enumerate(trends[:15], 1):
            name = t.text.strip()
            # يخلي الهاشتاق رابط
            msg += f"{i}. {name}\n"
        msg += f"\n⏰ {city_name} - يتم التحديث كل دقيقة"
        return msg
    except Exception as e:
        return f"ما قدرت أجيب ترند {city}: {e}"

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, 
        "🔥 <b>بوت ترند السعودية V2</b>\n\n"
        "/trend - ترند السعودية 🇸🇦\n"
        "/riyadh - ترند الرياض\n"
        "/jeddah - ترند جدة\n"
        "/dammam - ترند الشرقية\n"
        "/all - كل المدن مرة وحدة\n\n"
        "اكتب كلمة <b>ترند</b> في أي وقت!",
        parse_mode="HTML"
    )

@bot.message_handler(commands=['trend'])
def trend_sa(m): bot.reply_to(m, get_trends("saudi-arabia"), parse_mode="HTML")

@bot.message_handler(commands=['riyadh'])
def trend_ry(m): bot.reply_to(m, get_trends("riyadh"), parse_mode="HTML")

@bot.message_handler(commands=['jeddah'])
def trend_jd(m): bot.reply_to(m, get_trends("jeddah"), parse_mode="HTML")

@bot.message_handler(commands=['dammam'])
def trend_dm(m): bot.reply_to(m, get_trends("dammam"), parse_mode="HTML")

@bot.message_handler(commands=['all'])
def trend_all(m):
    msg = get_trends("saudi-arabia") + "\n\n" + "—"*15 + "\n\n"
    msg += get_trends("riyadh")
    bot.reply_to(m, msg, parse_mode="HTML")

@bot.message_handler(func=lambda m: "ترند" in m.text)
def any_trend(m):
    bot.reply_to(m, get_trends("saudi-arabia"), parse_mode="HTML")

def run_bot():
    print("Bot V2 is running...")
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
