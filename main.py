# =============================================
# main.py — ГЛАВНЫЙ ФАЙЛ, ЗАПУСКАЙ ЭТОТ
# =============================================

# Подключаем нужные библиотеки
import asyncio                          # Позволяет программе делать несколько дел "одновременно"
import os                               # Работа с файлами и переменными окружения
from dotenv import load_dotenv          # Читает наш .env файл с секретными данными
from telethon import TelegramClient, events  # Главная библиотека для работы с Telegram

from config import SOURCE_CHANNELS      # Наш список каналов из config.py
from forwarder import forward_message   # Наша функция пересылки из forwarder.py

# ── Загружаем секретные данные из файла .env ──
load_dotenv()

API_ID               = int(os.getenv("API_ID"))           # Числовой ID приложения
API_HASH             = os.getenv("API_HASH")              # Секретный ключ приложения
PHONE_NUMBER         = os.getenv("PHONE_NUMBER")          # Номер телефона аккаунта
AGGREGATOR_CHANNEL_ID = int(os.getenv("AGGREGATOR_CHANNEL_ID"))  # ID канала-агрегатора

# ── Создаём клиент Telegram ──
# "aggregator_session" — имя файла, в который сохранится сессия после первого входа.
# После первого запуска появится файл aggregator_session.session — не удаляй его!
client = TelegramClient("aggregator_session", API_ID, API_HASH)


# ── Главная функция ──
async def main():
    # Запускаем клиент и логинимся
    # При первом запуске попросит ввести номер телефона и код из Telegram
    await client.start(phone=PHONE_NUMBER)
    print("✅ Бот запущен и слушает каналы...")
    print(f"📋 Каналы-источники: {SOURCE_CHANNELS}")
    print(f"📨 Агрегатор: {AGGREGATOR_CHANNEL_ID}")
    print("Нажми Ctrl+C чтобы остановить\n")

    # ── Подписываемся на новые сообщения ──
    # Декоратор @client.on(...) говорит: "когда придёт новое сообщение из этих каналов — вызови функцию handler"
    @client.on(events.NewMessage(chats=SOURCE_CHANNELS))
    async def handler(event):
        """Эта функция вызывается автоматически при каждом новом сообщении"""
        await forward_message(client, event, AGGREGATOR_CHANNEL_ID)

    # ── Держим бота запущенным ──
    # Программа будет работать пока не нажмёшь Ctrl+C
    await client.run_until_disconnected()


# ── Точка входа ──
# Этот блок запускается когда ты пишешь: python main.py
if __name__ == "__main__":
    asyncio.run(main())
