import asyncio
from telethon import TelegramClient, functions, types

# --- ШАГ 4: ВПИШИ СВОИ ДАННЫЕ СЮДА ---
API_ID = 0  # Замени на свой api_id (число)
API_HASH = ""  # Замени на свой api_hash (строка в кавычках)
# -------------------------------------

async def main():
    async with TelegramClient('my_session', API_ID, API_HASH) as client:
        print("Авторизация успешна!")
        
        try:
            # Запрашиваем данные у пользователя
            gift_id = input("Введи ID подарка: ").strip()
            message = input("Введи подпись к подарку (или оставь пустым): ").strip()
            recipient = input("Введи @username или ID получателя: ").strip()

            # Подготовка сообщения (если есть)
            entities = [] 
            if message:
                msg_content = message
            else:
                msg_content = ""

            # Отправка подарка
            # Используем актуальный метод API для отправки подарков за звезды
            result = await client(functions.payments.SendStarsGiftRequest(
                peer=recipient,
                gift_id=int(gift_id),
                message=types.TextWithEntities(
                    text=msg_content,
                    entities=entities
                )
            ))

            print("✅ Подарок успешно отправлен!")
            
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")

if __name__ == "__main__":
    if API_ID == 0 or API_HASH == "":
        print("Ошибка: Ты забыл ввести API_ID и API_HASH внутри файла!")
    else:
        asyncio.run(main())
