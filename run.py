#!/usr/bin/env python3
"""
🚀 Telegram Aggregator — ЗАПУСК НА СЕРВЕРЕ

Инструкция:
1. Я запускаю бота
2. Он просит код
3. Ты смотришь в Telegram второго аккаунта (самые свежие сообщения)
4. Присылаешь мне 5 цифр
5. Я ввожу код
6. Если есть 2FA-пароль — присылаешь и его
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, SessionPasswordNeededError

from config import CHANNEL_GROUPS
from forwarder import forward_message

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
    client = TelegramClient("aggregator_session", API_ID, API_HASH)
    client.flood_sleep_threshold = 0
    client.retry_delay = 1
    client.auto_reconnect = True

    await client.connect()
    
    if not await client.is_user_authorized():
        print(f"\n📞 Отправляю код на {PHONE_NUMBER}...")
        await client.send_code_request(PHONE_NUMBER)
        code = input("🔑 Введи код: ").strip()
        try:
            await client.sign_in(phone=PHONE_NUMBER, code=code)
        except SessionPasswordNeededError:
            pwd = input("🔒 Нужен 2FA-пароль: ").strip()
            await client.sign_in(password=pwd)
    
    await client.start(phone=PHONE_NUMBER)
    
    me = await client.get_me()
    logger.info(f"✅ Авторизован как: {me.phone or me.username}")

    for group in CHANNEL_GROUPS:
        sources       = group["sources"]
        aggregator_id = group["aggregator_id"]
        group_name    = group["name"]
        logger.info(f"📋 Группа [{group_name}]: {len(sources)} каналов → агрегатор {aggregator_id}")

        # Регистрируем обработчик с try/except для каждого канала отдельно
        @client.on(events.NewMessage(chats=sources))
        async def handler(event, g=group):
            try:
                source_chat = await event.get_chat()
                source_name = getattr(source_chat, "title", "Неизвестный")
                logger.info(f"📩 Получено из [{source_name}] -> группа [{g['name']}]")
                await forward_message(client, event, g["aggregator_id"])
            except FloodWaitError as e:
                logger.warning(f"⏳ Flood wait {e.seconds}с — пропускаем")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                logger.error(f"❌ Ошибка в группе [{g['name']}]: {e}")

    logger.info("🚀 Бот запущен и слушает каналы...\n")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())