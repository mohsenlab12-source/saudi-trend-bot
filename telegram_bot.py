import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("هلا والله! بوت ترند السعودية شغال 24/7 ✅\nارسل /trend")

async def trend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 ترند السعودية:\n#السعودية\n#الرياض\n#جدة")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("trend", trend))
app.run_polling()
