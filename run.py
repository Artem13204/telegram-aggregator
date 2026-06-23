#!/usr/bin/env python3
"""
🚀 Telegram Aggregator — ЗАПУСК НА СЕРВЕРЕ
Версия с поллингом: бот сам ходит за новыми сообщениями каждые 60 секунд
"""

import asyncio
import os
import sys
import logging
from dotenv import load_dotenv
from telethon import TelegramClient

from config import CHANNEL_GROUPS
from poller import poll_group

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("logs/aggregator.log"),
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)
logger = logging.getLogger(__name__)

load_dotenv()

API_ID       = int(os.getenv("API_ID"))
API_HASH     = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")


async def main():
    client = TelegramClient("aggregator_session", API_ID, API_HASH)
    client.flood_sleep_threshold = 10
    client.retry_delay = 5
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

    # ── Запускаем поллинг для каждой группы ──
    for group in CHANNEL_GROUPS:
        if not group["sources"]:
            logger.warning(f"⚠️ Пропускаем группу [{group['name']}] — 0 каналов")
            continue

        logger.info(f"📋 Группа [{group['name']}]: {len(group['sources'])} каналов → {group['aggregator_id']}")
        asyncio.create_task(
            poll_group(
                client=client,
                sources=group["sources"],
                aggregator_id=group["aggregator_id"],
                group_name=group["name"],
                interval=45  # проверяем каждые 45 секунд
            )
        )

    logger.info("🚀 Бот запущен в режиме поллинга (интервал: 45с)...\n")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())