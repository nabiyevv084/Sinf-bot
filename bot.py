import logging
import json
import os
from datetime import datetime, date
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import yt_dlp

BOT_TOKEN = AAH6QNsnqi-DENksC_7fvpC6CB7wHJN2jYA
GURUH_ID = -1001757184098
DATA_FILE = "faollik.json"

logging.basicConfig(level=logging.INFO)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def bugun():
    return date.today().isoformat()

async def xabar_qayd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return
    user = msg.from_user
    ism = f"{user.first_name or ''} {user.last_name or ''}".strip()

    # Guruh faolligini qayd qilish
    if msg.chat.id == GURUH_ID:
        data = load_data()
        if bugun() not in data:
            data[bugun()] = {}
        uid = str(user.id)
        if uid not in data[bugun()]:
            data[bugun()][uid] = {"ism": ism, "vaqt": datetime.now().strftime("%H:%M"), "son": 0}
        data[bugun()][uid]["son"] += 1
        data[bugun()][uid]["oxirgi"] = datetime.now().strftime("%H:%M")
        save_data(data)

    # Video yuklash
    text = msg.text or ""
    if any(x in text for x in ["instagram.com", "tiktok.com", "youtu.be", "youtube.com"]):
        await msg.reply_text("⏳ Video yuklanmoqda, kuting...")
        try:
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': 'video.%(ext)s',
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text.strip(), download=True)
                filename = ydl.prepare_filename(info)
            with open(filename, 'rb') as f:
                await msg.reply_video(f)
            os.remove(filename)
        except Exception as e:
            await msg.reply_text("❌ Video yuklab bo'lmadi. Link to'g'rimi?")

async def hisobot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    bugungi = data.get(bugun(), {})
    if not bugungi:
        await update.message.reply_text("Bugun hech kim yozmadi!")
        return
    matn = f"📊 {bugun()} — Faollik:\n\n"
    for i, k in enumerate(sorted(bugungi.values(), key=lambda x: x['son'], reverse=True), 1):
        matn += f"{i}. {k['ism']} — {k['vaqt']}dan {k['oxirgi']}gacha — {k['son']} xabar\n"
    matn += f"\nJami: {len(bugungi)} kishi yozdi"
    await update.message.reply_text(matn)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    matn = """👋 Assalomu alaykum!

🤖 Bu bot 2 ta funksiya qiladi:

📊 Sinf faolligi:
/hisobot — bugungi faollikni ko'rish

🎥 Video yuklash:
Instagram, TikTok, YouTube linkini yuboring — video yuklab beradi!"""
    await update.message.reply_text(matn)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("hisobot", hisobot))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, xabar_qayd))
print("Bot ishga tushdi!")
app.run_polling()
