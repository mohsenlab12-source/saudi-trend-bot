import os, threading, time, requests
from bs4 import BeautifulSoup
import telebot
from flask import Flask

BOT_TOKEN = os.environ.get("BOT_TOKEN")
print(f"BOT_TOKEN exists: {bool(BOT_TOKEN)}")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/')
def home():
    return "Saudi Trend Bot is LIVE! 🇸🇦"

def get_trends(city="saudi-arabia"):
    try:
        url = "https://getdaytrends.com/saudi-arabia/riyadh/" if city=="riyadh" else "https://getdaytrends.com/saudi-arabia/"
        r = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        trends = soup.select('.trend-list a') or soup.select('table tr td a')
        clean=[]
        for t in trends:
            txt=t.text.strip()
            if txt and txt not in clean:
                clean.append(txt)
            if len(clean)>=15:
                break
        if not clean:
            return "No trends now, try again"
        city_name={"saudi-arabia":"Saudi Arabia","riyadh":"Riyadh","jeddah":"Jeddah"}.get(city,"Saudi")
        msg=f"\u200e🇸🇦 Trend {city_name}\n━━━━━━━━━━━━━━\n"
        for i,name in enumerate(clean,1):
            msg+=f"\u200e{i}. {name}\n"
        msg+="━━━━━━━━━━━━━━"
        return msg
    except Exception as e:
        return f"Error: {e}"

@bot.message_handler(commands=['start','trend','jeddah','riyadh','all'])
def handle(m):
    cmd=m.text.replace('/','').split()[0]
    print(f"Command: {cmd}")
    if cmd=='start':
        bot.reply_to(m, "🔥 Saudi Trend Bot\n/trend - Saudi\n/riyadh - Riyadh\n/jeddah - Jeddah\n/all - All")
        return
    target="riyadh" if cmd=="riyadh" else "saudi-arabia"
    text=get_trends(target)
    if cmd=="jeddah":
        text=text.replace("Saudi Arabia","Jeddah")
    if cmd=="all":
        text=get_trends("saudi-arabia")+"\n\n"+get_trends("riyadh")
    bot.reply_to(m, text)

def run_bot():
    while True:
        try:
            print("Deleting webhook & starting polling...")
            bot.delete_webhook(drop_pending_updates=True)
            time.sleep(3)
            print("Polling started...")
            bot.infinity_polling(timeout=60, skip_pending=True)
        except Exception as e:
            print(f"Polling error: {e} - retry in 5s")
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port=int(os.environ.get("PORT",10000))
    print(f"Flask running on {port}")
    app.run(host="0.0.0.0", port=port)
