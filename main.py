# =============================================
# main.py — ГЛАВНЫЙ ФАЙЛ, ЗАПУСКАЙ ЭТОТ
# =============================================

import asyncio
import os
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

from config import CHANNEL_GROUPS
from forwarder import forward_message

# Настройка логов
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

API_ID       = int(os.getenv("API_ID"))
API_HASH     = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")


async def main():
    # Создаем клиент с повышенной стабильностью
    client = TelegramClient("aggregator_session", API_ID, API_HASH)

    # Настройки для уменьшения задержек
    client.flood_sleep_threshold = 0   # Не ждать автоматически при flood wait
    client.retry_delay = 1             # Переподключаться через 1 секунду
    client.auto_reconnect = True       # Автопереподключение при разрыве

    await client.start(phone=PHONE_NUMBER)

    # Проверяем соединение
    me = await client.get_me()
    logger.info(f"✅ Авторизован как: {me.phone or me.username}")

    # Регистрируем обработчики для каждой группы
    for group in CHANNEL_GROUPS:
        sources       = group["sources"]
        aggregator_id = group["aggregator_id"]
        group_name    = group["name"]

        logger.info(f"📋 Группа [{group_name}]: {len(sources)} каналов → агрегатор {aggregator_id}")

        @client.on(events.NewMessage(chats=sources))
        async def handler(event, g=group):
            try:
                await forward_message(client, event, g["aggregator_id"])
            except FloodWaitError as e:
                logger.warning(f"⏳ Flood wait {e.seconds}с — пропускаем")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                logger.error(f"❌ Ошибка: {e}")

    logger.info("🚀 Бот запущен и слушает каналы...\n")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
