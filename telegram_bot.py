import os, threading, time, json, requests
from bs4 import BeautifulSoup
import telebot
from flask import Flask
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "")  # اختياري للقناة
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

# ملفات التخزين
ALERTS_FILE = "alerts.json"
AUTO_FILE = "auto.json"

def load_json(file, default):
    try:
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except: pass
    return default

def save_json(file, data):
    try:
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except: pass

alerts = load_json(ALERTS_FILE, {})  # {user_id: [keywords]}
auto_users = load_json(AUTO_FILE, [])  # [user_id]

@app.route('/')
def home():
    return f"Business Trend Bot LIVE! Users: {len(alerts)} | Auto: {len(auto_users)}"

def get_trends_list(city="saudi-arabia"):
    try:
        urls = {
            "saudi-arabia": "https://getdaytrends.com/saudi-arabia/",
            "riyadh": "https://getdaytrends.com/saudi-arabia/riyadh/",
            "jeddah": "https://getdaytrends.com/saudi-arabia/jeddah/",
            "makkah": "https://getdaytrends.com/saudi-arabia/mecca/",
            "dammam": "https://getdaytrends.com/saudi-arabia/dammam/"
        }
        url = urls.get(city, urls["saudi-arabia"])
        r = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        trends = soup.select('.trend-list a') or soup.select('table tr td a')
        clean=[]
        for t in trends:
            txt=t.text.strip()
            if txt and txt not in clean:
                clean.append(txt)
            if len(clean)>=15: break
        return clean
    except: return []

def format_trends(clean, city_name):
    if not clean: return "لا يوجد ترند حاليا"
    msg=f"\u200e🇸🇦 Trend {city_name} - {datetime.now().strftime('%I:%M %p')}\n━━━━━━━━━━━━━━\n"
    for i,name in enumerate(clean,1):
        msg+=f"\u200e{i}. {name}\n"
    msg+="━━━━━━━━━━━━━━\n"
    msg+=f"\u200e💡 نصيحة: استخدم الترند لتسويق منتجك!"
    return msg

# --- أوامر البوت ---
@bot.message_handler(commands=['start'])
def start(m):
    txt = (
        "🔥 <b>بوت ترند بزنس - النسخة الاحترافية</b>\n\n"
        "📈 <b>أوامر الترند:</b>\n"
        "/trend - السعودية\n"
        "/riyadh - الرياض\n"
        "/jeddah - جدة\n"
        "/makkah - مكة\n"
        "/dammam - الدمام\n"
        "/all - كل المدن\n\n"
        "🚨 <b>أوامر البزنس (اللي يدفع عليها العميل):</b>\n"
        "/alert كلمة - تنبيه عند ظهور كلمة في الترند\n"
        "مثال: <code>/alert عثمان</code>\n"
        "/myalerts - كلماتي المراقبة\n"
        "/delalert كلمة - حذف تنبيه\n\n"
        "🤖 <b>أوامر الأوتوماتيك:</b>\n"
        "/autopost - تفعيل النشر التلقائي كل ساعة\n"
        "/report - تقرير يومي عن البراند\n"
        "/stats - إحصائيات حسابك\n"
    )
    bot.reply_to(m, txt, parse_mode="HTML")

@bot.message_handler(commands=['trend','riyadh','jeddah','makkah','dammam','all'])
def trends_cmd(m):
    cmd = m.text.split()[0].replace('/','')
    cities = {
        'trend': ('saudi-arabia','Saudi Arabia'),
        'riyadh': ('riyadh','Riyadh'),
        'jeddah': ('jeddah','Jeddah'),
        'makkah': ('makkah','Makkah'),
        'dammam': ('dammam','Dammam')
    }
    if cmd == 'all':
        full=""
        for k,(code,name) in cities.items():
            if k=='trend': continue
            lst=get_trends_list(code)
            full+=format_trends(lst, name)+"\n\n"
        bot.reply_to(m, full[:4000])
        return
    code,name = cities.get(cmd, ('saudi-arabia','Saudi Arabia'))
    lst=get_trends_list(code)
    bot.reply_to(m, format_trends(lst, name))

@bot.message_handler(commands=['alert'])
def add_alert(m):
    parts = m.text.split(maxsplit=1)
    if len(parts)<2:
        bot.reply_to(m, "❌ اكتب الكلمة: /alert عثمان")
        return
    keyword = parts[1].strip().lower()
    uid = str(m.from_user.id)
    if uid not in alerts: alerts[uid]=[]
    if keyword not in alerts[uid]:
        alerts[uid].append(keyword)
        save_json(ALERTS_FILE, alerts)
    bot.reply_to(m, f"✅ تم! راح أنبهك أول ما كلمة '{parts[1]}' تصير ترند\n\nنشط /myalerts لعرض الكل")

@bot.message_handler(commands=['myalerts'])
def list_alerts(m):
    uid=str(m.from_user.id)
    kw=alerts.get(uid,[])
    if not kw:
        bot.reply_to(m, "ما عندك تنبيهات. أضف بـ /alert كلمة")
        return
    bot.reply_to(m, "🚨 كلماتك المراقبة:\n" + "\n".join([f"- {k}" for k in kw]))

@bot.message_handler(commands=['delalert'])
def del_alert(m):
    parts=m.text.split(maxsplit=1)
    if len(parts)<2: return
    uid=str(m.from_user.id)
    kw=parts[1].lower()
    if uid in alerts and kw in alerts[uid]:
        alerts[uid].remove(kw)
        save_json(ALERTS_FILE, alerts)
        bot.reply_to(m, f"🗑️ حذفنا تنبيه {parts[1]}")

@bot.message_handler(commands=['autopost'])
def autopost(m):
    uid=str(m.from_user.id)
    if uid in auto_users:
        auto_users.remove(uid)
        bot.reply_to(m, "⏸️ تم إيقاف النشر التلقائي")
    else:
        auto_users.append(uid)
        bot.reply_to(m, "✅ تم تفعيل النشر التلقائي! راح أرسل لك الترند كل ساعة")
    save_json(AUTO_FILE, auto_users)

@bot.message_handler(commands=['report','stats'])
def report(m):
    uid=str(m.from_user.id)
    lst=get_trends_list("saudi-arabia")
    total_trends=len(lst)
    my_kw=len(alerts.get(uid,[]))
    txt=f"📊 تقريرك اليومي\n━━━━━━━━━━━━━━\nعدد الترندات الآن: {total_trends}\nكلماتك المراقبة: {my_kw}\nالنشر التلقائي: {'مفعل ✅' if uid in auto_users else 'متوقف ⏸️'}\n\n💰 فرصة: استغل الترند رقم 1 للتسويق اليوم!"
    bot.reply_to(m, txt)

# --- نظام مراقبة وتنبيه تلقائي في الخلفية ---
def alert_checker():
    while True:
        try:
            time.sleep(60*15)  # كل 15 دقيقة
            if not alerts: continue
            all_trends = get_trends_list("saudi-arabia") + get_trends_list("riyadh") + get_trends_list("jeddah")
            all_text = " ".join(all_trends).lower()
            for uid, keywords in alerts.items():
                for kw in keywords:
                    if kw in all_text:
                        try:
                            # نلاقي رقم الترند
                            for i,t in enumerate(all_trends,1):
                                if kw in t.lower():
                                    bot.send_message(int(uid), f"🚨 تنبيه بزنس!\n\nكلمة '{kw}' صارت ترند رقم {i}\n🔥 {t}\n\n💡 نصيحة: انشر الآن واستغل الترند!")
                                    break
                        except: pass
        except Exception as e:
            print(f"Alert error: {e}")
            time.sleep(60)

def autopost_checker():
    while True:
        try:
            time.sleep(60*60)  # كل ساعة
            if not auto_users: continue
            lst=get_trends_list("saudi-arabia")
            msg=format_trends(lst, "Saudi Arabia - Auto")
            for uid in auto_users:
                try:
                    bot.send_message(int(uid), msg)
                except: pass
            if CHANNEL_ID:
                try:
                    bot.send_message(CHANNEL_ID, msg)
                except: pass
        except: time.sleep(60)

def run_bot():
    while True:
        try:
            print("Deleting webhook...")
            bot.delete_webhook(drop_pending_updates=True)
            time.sleep(3)
            print("Polling...")
            bot.infinity_polling(timeout=60, skip_pending=True)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    threading.Thread(target=alert_checker, daemon=True).start()
    threading.Thread(target=autopost_checker, daemon=True).start()
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0", port=port)
