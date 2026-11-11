import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()

Thread(target=run_server, daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبا!\n✅ بوت ترند السعودية شغال 24/7\nارسل /trend")

async def trend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 ترند السعودية:\n#السعودية\n#الرياض\n#جدة")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("trend", trend))
app.run_polling()
