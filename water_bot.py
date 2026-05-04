import os
from telethon import TelegramClient, events, functions, types

# Вставляй свои данные сюда
API_ID = 0  # Твой api_id
API_HASH = ""  # Твой api_hash

client = TelegramClient('my_session', API_ID, API_HASH)

print("Бот запускается...")

@client.on(events.NewMessage(pattern=r'(?i)^подарок (\d+) (@?\w+) ?(.*)?', chats='me'))
async def handler(event):
    # Команда работает только если ты пишешь сам себе в "Избранное"
    gift_id = event.pattern_match.group(1)
    recipient = event.pattern_match.group(2)
    message_text = event.pattern_match.group(3) or ""

    await event.reply(f"⏳ Пробую отправить подарок {gift_id} для {recipient}...")

    try:
        await client(functions.payments.SendStarsGiftRequest(
            peer=recipient,
            gift_id=int(gift_id),
            message=types.TextWithEntities(text=message_text, entities=[])
        ))
        await event.reply("✅ Подарок успешно отправлен!")
    except Exception as e:
        await event.reply(f"❌ Ошибка: {str(e)}")

async def main():
    await client.start()
    print("Бот онлайн! Напиши в 'Избранное': подарок [ID] [Юзернейм] [Текст]")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
