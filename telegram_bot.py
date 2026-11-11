import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🔥 بوت ترند السعودية 🔥

أهلاً بك!

الأوامر:
 /start - رسالة الترحيب
 /trend - جلب ترند السعودية الحالي

البوت شغال 24/7 🚀
"""
    await update.message.reply_text(text)

    # بعد الترحيب جيب الترند تلقائياً
    await trend(update, context)

async def trend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trends = """
🇸🇦 ترند السعودية الآن:

1. #همه_قد_الكلمه
2. ضمان الحجز
3. #شكرا_ابطال_الدفاع_الجوي
4. #مسابقات همه
5. #اليوم_العالمي_للعزاب
6. #مرسول_يدلع_العزاب
7. الدفاع الجوي
8. صحراء الدهناء
9. الضمان الذهبي
10. جامعة القصيم
11. محمد عمر
12. النسخه العالميه
13. علي الخارطه
14. بدول مجلس التعاون
15. الاجازات المرضيه
16. زيدان
17. اليوم الاربعاء
18. خليج العقيه
19. اليوم العالمي
20. عروس الجنوب

Source: GetDayTrends
https://getdaytrends.com/saudi-arabia/
"""
    await update.message.reply_text(trends)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trend", trend))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
