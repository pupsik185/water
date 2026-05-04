import logging
from telethon import TelegramClient, events, functions

# --- ВСТАВЬ СВОИ ДАННЫЕ СЮДА ---
API_ID = 0  # Твой api_id
API_HASH = ''  # Твой api_hash
# ------------------------------

# Настройка логирования, чтобы видеть ошибки в консоли
logging.basicConfig(level=logging.INFO)

client = TelegramClient('gift_bot_session', API_ID, API_HASH)

print("Бот запускается... Напиши в Telegram команду .gift для проверки.")

@client.on(events.NewMessage(pattern=r'\.gift (\d+) @?(\w+) ?(.*)', outgoing=True))
async def handler(event):
    # Разбираем параметры команды
    gift_id = int(event.pattern_match.group(1))
    recipient = event.pattern_match.group(2)
    message_text = event.pattern_match.group(3)

    await event.edit("⏳ Обработка отправки подарка...")

    try:
        # Отправка подарка
        await client(functions.payments.SendStarsGiftRequest(
            peer=recipient,
            gift_id=gift_id,
            message=message_text if message_text else None
        ))
        
        await event.edit(f"✅ Подарок {gift_id} успешно отправлен пользователю @{recipient}!")
    
    except Exception as e:
        await event.edit(f"❌ Ошибка при отправке: {e}")

# Запуск
client.start()
client.run_until_disconnected()
