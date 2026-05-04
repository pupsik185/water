import asyncio
from telethon import TelegramClient, functions, types

# --- ШАГ 4: ВСТАВЬ СВОИ ДАННЫЕ СЮДА ---
API_ID = 0  # Замени на свое число api_id
API_HASH = ''  # Замени на свою строку api_hash
# ---------------------------------------

async def main():
    # Создаем клиента и авторизуемся
    client = TelegramClient('my_session', API_ID, API_HASH)
    await client.start()
    
    me = await client.get_me()
    print(f"Авторизован: {me.first_name} (id={me.id})")
    print("-" * 30)

    try:
        # Запрашиваем данные у пользователя
        gift_id_input = input("Введи ID подарка (число): ").strip()
        message_text = input("Введи подпись к подарку (или оставь пустым): ").strip()
        recipient_username = input("Введи @username или ID получателя: ").strip()

        # Подготовка данных
        gift_id = int(gift_id_input)
        
        # Получаем объект получателя
        entity = await client.get_input_entity(recipient_username)

        # Отправка подарка через API Telegram
        # Мы используем функцию SendGift
        result = await client(functions.payments.SendStarsGiftRequest(
            peer=entity,
            gift_id=gift_id,
            message=message_text if message_text else None
        ))

        print("✅ Подарок успешно отправлен!")
        
    except ValueError:
        print("❌ Ошибка: ID подарка должен быть числом.")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
