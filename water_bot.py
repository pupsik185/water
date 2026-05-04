import logging
import os
import psycopg2
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

logging.basicConfig(level=logging.INFO)

# --- Подключение к PostgreSQL ---
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cursor = conn.cursor()

# --- Таблица ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    name TEXT,
    goal INTEGER DEFAULT 0,
    current INTEGER DEFAULT 0
)
""")

# --- функции ---
def add_user(user_id, name):
    cursor.execute(
        "INSERT INTO users (user_id, name) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING",
        (user_id, name)
    )


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    add_user(user.id, user.first_name)

    update.message.reply_text(
        "Привет! Установи цель: /goal 1000"
    )


def set_goal(update: Update, context: CallbackContext):
    user = update.effective_user
    add_user(user.id, user.first_name)

    try:
        goal = int(context.args[0])

        cursor.execute(
            "UPDATE users SET goal=%s, current=0 WHERE user_id=%s",
            (goal, user.id)
        )

        update.message.reply_text(f"Цель установлена: {goal} мл")

    except:
        update.message.reply_text("Используй: /goal 1000")


def drink(update: Update, context: CallbackContext):
    user = update.effective_user
    add_user(user.id, user.first_name)

    try:
        amount = int(context.args[0])

        cursor.execute(
            "UPDATE users SET current = current + %s WHERE user_id=%s",
            (amount, user.id)
        )

        cursor.execute(
            "SELECT name, current, goal FROM users WHERE user_id=%s",
            (user.id,)
        )
        name, current, goal = cursor.fetchone()

        message = f"{name} выпил еще {amount} мл воды! {current}/{goal} мл"

        # --- рассылаем всем ---
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()

        for (uid,) in users:
            try:
                context.bot.send_message(chat_id=uid, text=message)
            except:
                pass

    except:
        update.message.reply_text("Используй: /drink 100")


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("goal", set_goal))
    dp.add_handler(CommandHandler("drink", drink))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()