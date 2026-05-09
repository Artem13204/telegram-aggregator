# =============================================
# main.py — ГЛАВНЫЙ ФАЙЛ, ЗАПУСКАЙ ЭТОТ
# =============================================

# Подключаем нужные библиотеки
import asyncio                          # Позволяет программе делать несколько дел "одновременно"
import os                               # Работа с файлами и переменными окружения
from dotenv import load_dotenv          # Читает наш .env файл с секретными данными
from telethon import TelegramClient, events  # Главная библиотека для работы с Telegram

from config import CHANNEL_GROUPS       # Наши группы каналов из config.py
from forwarder import forward_message   # Наша функция пересылки из forwarder.py

# ── Загружаем секретные данные из файла .env ──
load_dotenv()

API_ID       = int(os.getenv("API_ID"))    # Числовой ID приложения
API_HASH     = os.getenv("API_HASH")       # Секретный ключ приложения
PHONE_NUMBER = os.getenv("PHONE_NUMBER")   # Номер телефона аккаунта

# ── Главная функция ──
async def main():
    # Создаём клиент ВНУТРИ async функции — это важно для Python 3.12+
    client = TelegramClient("aggregator_session", API_ID, API_HASH)

    # Запускаем клиент и логинимся
    await client.start(phone=PHONE_NUMBER)
    print("✅ Бот запущен и слушает каналы...")

    # ── Регистрируем обработчик для каждой группы ──
    # Проходим по каждой группе из config.py и вешаем свой обработчик
    for group in CHANNEL_GROUPS:
        sources       = group["sources"]
        aggregator_id = group["aggregator_id"]
        group_name    = group["name"]

        print(f"📋 Группа [{group_name}]: {len(sources)} каналов → агрегатор {aggregator_id}")

        # Создаём отдельный обработчик для этой группы.
        # Важно: используем default argument (g=group) чтобы каждый
        # обработчик "запомнил" свою группу, а не использовал последнюю из цикла.
        @client.on(events.NewMessage(chats=sources))
        async def handler(event, g=group):
            await forward_message(client, event, g["aggregator_id"])

    print("Нажми Ctrl+C чтобы остановить\n")

    # ── Держим бота запущенным ──
    # Программа будет работать пока не нажмёшь Ctrl+C
    await client.run_until_disconnected()


# ── Точка входа ──
# Этот блок запускается когда ты пишешь: python main.py
if __name__ == "__main__":
    asyncio.run(main())
