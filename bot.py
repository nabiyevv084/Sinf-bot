import logging
import json
import os
from datetime import datetime, date
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

BOT_TOKEN = "8655610690:AAE6tn9Gpn3Yzk_O8pnoJZytq43o_bNE42k"
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
    if not msg or msg.chat.id != GURUH_ID:
        return
    user = msg.from_user
    ism = f"{user.first_name or ''} {user.last_name or ''}".strip()
    data = load_data()
    if bugun() not in data:
        data[bugun()] = {}
    uid = str(user.id)
    if uid not in data[bugun()]:
        data[bugun()][uid] = {"ism": ism, "vaqt": datetime.now().strftime("%H:%M"), "son": 0}
    data[bugun()][uid]["son"] += 1
    data[bugun()][uid]["oxirgi"] = datetime.now().strftime("%H:%M")
    save_data(data)

async def hisobot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    bugungi = data.get(bugun(), {})
    if not bugungi:
        await update.message.reply_text("Bugun hech kim yozmagan!")
        return
    matn = f"📊 {bugun()} — Faollik:\n\n"
    for i, k in enumerate(sorted(bugungi.values(), key=lambda x: x['son'], reverse=True), 1):
        matn += f"{i}. {k['ism']} — {k['vaqt']}dan {k['oxirgi']}gacha — {k['son']} xabar\n"
    matn += f"\nJami: {len(bugungi)} kishi yozdi"
    await update.message.reply_text(matn)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, xabar_qayd))
app.add_handler(CommandHandler("hisobot", hisobot))
print("Bot ishga tushdi!")
app.run_polling()
