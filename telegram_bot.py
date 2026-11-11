import os, threading, requests
from bs4 import BeautifulSoup
import telebot
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home(): return "Bot V3 Live 🇸🇦"

def get_trends(city="saudi-arabia"):
    try:
        url = "https://getdaytrends.com/saudi-arabia/riyadh/" if city=="riyadh" else "https://getdaytrends.com/saudi-arabia/"
        r = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        trends = soup.select('.trend-list a') or soup.select('table tr td a')
        clean = []
        for t in trends:
            txt = t.text.strip()
            if txt and txt not in clean: clean.append(txt)
            if len(clean)>=15: break
        
        city_name = {"saudi-arabia":"السعودية","riyadh":"الرياض","jeddah":"جدة"}[city]
        # استخدام ايموجي ارقام عشان ما ينعكس التنسيق
        nums = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟","1️⃣1️⃣","1️⃣2️⃣","1️⃣3️⃣","1️⃣4️⃣","1️⃣5️⃣"]
        msg = f"🇸🇦 <b>ترند {city_name} الآن</b>\n"
        msg += "━━━━━━━━━━━━━━\n"
        for i, name in enumerate(clean):
            msg += f"{nums[i]} {name}\n"
        msg += "━━━━━━━━━━━━━━\n"
        msg += f"⏰ تحديث لحظي"
        return msg
    except Exception as e:
        return f"خطأ: {e}"

@bot.message_handler(commands=['start','trend','jeddah','riyadh','all'])
def handle(m):
    cmd = m.text.replace('/','').split()[0]
    if cmd == 'start':
        bot.reply_to(m, "🔥 <b>بوت ترند السعودية</b>\n\n/trend - السعودية\n/riyadh - الرياض\n/jeddah - جدة\n/all - الكل", parse_mode="HTML")
        return
    target = "riyadh" if cmd=="riyadh" else "saudi-arabia"
    msg = get_trends(target)
    if cmd=="jeddah": msg = msg.replace("السعودية","جدة")
    if cmd=="all": msg = get_trends("saudi-arabia") + "\n\n" + get_trends("riyadh")
    bot.reply_to(m, msg, parse_mode="HTML")

def run_bot(): bot.infinity_polling()
if __name__=="__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
