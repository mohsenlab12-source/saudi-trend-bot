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
    return "Saudi Trend Bot V2.1 is Live! 🇸🇦"

def get_trends(city="saudi-arabia"):
    try:
        # الرياض وجدة نجيبها من نفس صفحة السعودية لأن الموقع ما يفصل المدن الصغيرة
        url = "https://getdaytrends.com/saudi-arabia/"
        if city == "riyadh":
            url = "https://getdaytrends.com/saudi-arabia/riyadh/"
        
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        trends = soup.select('.trend-list a') or soup.select('table tr td a') or soup.select('a[href*="/trend/"]')
        
        # فلترة وتنظيف
        clean_trends = []
        for t in trends:
            txt = t.text.strip()
            if txt and len(txt) > 1 and txt not in clean_trends:
                clean_trends.append(txt)
            if len(clean_trends) >= 15:
                break
        
        if not clean_trends:
            return "⚠️ ما لقيت ترندات الحين، جرب /trend"

        city_names = {"saudi-arabia": "السعودية", "riyadh": "الرياض", "jeddah": "جدة", "dammam": "الشرقية"}
        city_name = city_names.get(city, "السعودية")
        
        msg = f"🇸🇦 <b>ترند {city_name} الآن:</b>\n\n"
        for i, name in enumerate(clean_trends, 1):
            msg += f"{i}. {name}\n"
        msg += f"\n⏰ يتم التحديث كل دقيقة"
        return msg
    except Exception as e:
        return f"خطأ: {e}"

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, 
        "🔥 <b>بوت ترند السعودية V2.1</b>\n\n"
        "/trend - ترند السعودية 🇸🇦\n"
        "/riyadh - ترند الرياض\n"
        "/jeddah - ترند جدة (نفس السعودية + فلتر)\n"
        "/all - كل المدن\n",
        parse_mode="HTML")

@bot.message_handler(commands=['trend','riyadh','jeddah','dammam','all'])
def handle_trends(m):
    cmd = m.text.replace('/','').strip()
    if cmd == 'all':
        msg = get_trends("saudi-arabia") + "\n\n" + get_trends("riyadh")
    else:
        # جدة والدمام نجيب لها السعودية لأن ما لها صفحة خاصة
        target = "saudi-arabia" if cmd in ["jeddah","dammam"] else cmd
        msg = get_trends(target)
        if cmd == "jeddah":
            msg = msg.replace("السعودية", "جدة")
    bot.reply_to(m, msg, parse_mode="HTML")

def run_bot():
    print("Bot V2.1 running...")
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
