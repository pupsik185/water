import os
import asyncio
import asyncpg
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

# Получаем токены из переменных окружения Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# Инициализируем бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Глобальная переменная для пула соединений с БД
db_pool = None

async def init_db():
    """Функция для инициализации БД и создания таблицы, если её нет"""
    global db_pool
    # Railway иногда выдает URL, начинающийся с postgres://, а asyncpg требует postgresql://
    db_url = DATABASE_URL.replace("postgres://", "postgresql://")
    
    db_pool = await asyncpg.create_pool(db_url)
    async with db_pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                name VARCHAR(255),
                goal INT DEFAULT 2000,
                current_intake INT DEFAULT 0
            )
        ''')

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Регистрация пользователя в базе"""
    user_id = message.from_user.id
    # Берем имя или юзернейм
    name = message.from_user.first_name or message.from_user.username or "Пользователь"
    
    async with db_pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO users (user_id, name) VALUES ($1, $2)
            ON CONFLICT (user_id) DO NOTHING
        ''', user_id, name)
        
    text = (
        "Привет! Я бот для трекинга воды 💧\n\n"
        "Доступные команды:\n"
        "<b>/setgoal 2000</b> — установить свою цель на день (в мл)\n"
        "<b>/add 200</b> — записать выпитую воду\n"
        "<b>/status</b> — посмотреть свой текущий прогресс\n"
        "<b>/reset</b> — обнулить счетчик (например, утром)"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("setgoal"))
async def cmd_setgoal(message: Message, command: CommandObject):
    """Установка цели"""
    if not command.args or not command.args.isdigit():
        return await message.answer("Пожалуйста, укажите число. Пример: /setgoal 2000")
    
    goal = int(command.args)
    async with db_pool.acquire() as conn:
        await conn.execute('UPDATE users SET goal = $1 WHERE user_id = $2', goal, message.from_user.id)
        
    await message.answer(f"✅ Твоя цель обновлена: {goal} мл.")

@dp.message(Command("add"))
async def cmd_add(message: Message, command: CommandObject):
    """Добавление воды и рассылка всем пользователям"""
    if not command.args or not command.args.isdigit():
        return await message.answer("Пожалуйста, укажите количество в миллилитрах. Пример: /add 200")
    
    amount = int(command.args)
    user_id = message.from_user.id
    
    async with db_pool.acquire() as conn:
        # Обновляем количество выпитой воды
        await conn.execute('''
            UPDATE users 
            SET current_intake = current_intake + $1 
            WHERE user_id = $2
        ''', amount, user_id)
        
        # Получаем обновленные данные пользователя
        user_row = await conn.fetchrow('SELECT name, current_intake, goal FROM users WHERE user_id = $1', user_id)
        
        # Получаем ID всех пользователей бота для рассылки
        all_users = await conn.fetch('SELECT user_id FROM users')
        
    if not user_row:
        return await message.answer("Сначала напишите /start для регистрации.")
        
    name = user_row['name']
    current = user_row['current_intake']
    goal = user_row['goal']
    
    # Формируем текст уведомления
    notification_text = f"💧 {name} выпил(а) еще {amount} милилтров воды! {current}/ {goal} мл."
    
    # Рассылаем всем пользователям (включая того, кто выпил)
    for u in all_users:
        try:
            await bot.send_message(u['user_id'], notification_text)
        except Exception:
            # Игнорируем ошибки (например, если кто-то заблокировал бота)
            pass

@dp.message(Command("status"))
async def cmd_status(message: Message):
    """Просмотр личной статистики"""
    async with db_pool.acquire() as conn:
        user_row = await conn.fetchrow('SELECT current_intake, goal FROM users WHERE user_id = $1', message.from_user.id)
        
    if user_row:
        current = user_row['current_intake']
        goal = user_row['goal']
        await message.answer(f"📊 Твой статус: {current} / {goal} мл.")
    else:
        await message.answer("Сначала напишите /start")

@dp.message(Command("reset"))
async def cmd_reset(message: Message):
    """Сброс счетчика воды"""
    async with db_pool.acquire() as conn:
        await conn.execute('UPDATE users SET current_intake = 0 WHERE user_id = $1', message.from_user.id)
    await message.answer("🔄 Счетчик сброшен на 0. Начинаем новый день!")

async def main():
    # Подключаемся к БД
    await init_db()
    
    # Запускаем бота
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
