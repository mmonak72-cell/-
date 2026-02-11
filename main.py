import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")  # токен бота хранится в переменной окружения

KEYS_FILE = "keys.json"  # файл для хранения ключей

# --- Загрузка ключей ---
def load_keys():
    try:
        with open(KEYS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"unused": [], "used": []}

# --- Сохранение ключей ---
def save_keys(data):
    with open(KEYS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Команда /addkeys ---
async def addkeys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь список ключей одним сообщением")
    context.user_data["waiting_keys"] = True

# --- Обработка текста с ключами ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_keys"):
        return

    text = update.message.text
    new_keys = text.split()  # разделяем текст на ключи по пробелам

    data = load_keys()
    data["unused"].extend(new_keys)

    save_keys(data)

    context.user_data["waiting_keys"] = False

    await update.message.reply_text(f"Добавлено ключей: {len(new_keys)}")

# --- Команда /getkey ---
async def getkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_keys()

    if not data["unused"]:
        await update.message.reply_text("Ключи закончились")
        return

    key = data["unused"].pop(0)
    data["used"].append(key)

    save_keys(data)

    await update.message.reply_text(f"Твой ключ:\n{key}")

# --- Запуск бота ---
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("addkeys", addkeys))
app.add_handler(CommandHandler("getkey", getkey))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()
