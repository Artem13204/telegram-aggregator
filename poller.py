# =============================================
# poller.py — ПОЛЛИНГ НОВЫХ СООБЩЕНИЙ
# Вместо ожидания апдейтов от Telegram — сами ходим и проверяем
# =============================================

import asyncio
import datetime, time
import logging
from telethon import TelegramClient
from telethon.errors import FloodWaitError

logger = logging.getLogger(__name__)

# Минимальная пауза между запросами к TG, чтоб не словить FloodWait
TG_REQUEST_DELAY = 1.5


async def safe_get_messages(client, entity, limit=2):
    """Получить сообщения с обработкой FloodWait и ретраем"""
    for attempt in range(3):
        try:
            return await client.get_messages(entity, limit=limit)
        except FloodWaitError as e:
            if e.seconds <= 15 and attempt < 2:
                logger.debug(f"⏳ FloodWait {e.seconds}с — ждём и повторяем")
                await asyncio.sleep(e.seconds + 1)
            else:
                logger.warning(f"⏳ FloodWait {e.seconds}с — слишком долго, пропускаем")
                return None
        except Exception as e:
            logger.warning(f"⚠️ Ошибка get_messages {entity}: {e}")
            return None
    return None


async def safe_forward(client, entity, msg_id, from_peer):
    """Переслать сообщение с ретраем при мелком FloodWait"""
    for attempt in range(2):
        try:
            await client.forward_messages(
                entity=entity,
                messages=msg_id,
                from_peer=from_peer,
            )
            return True
        except FloodWaitError as e:
            if e.seconds <= 15 and attempt == 0:
                await asyncio.sleep(e.seconds + 1)
            else:
                logger.warning(f"⏳ FloodWait {e.seconds}с при отправке — пропускаем")
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка forward: {e}")
            return False
    return False


async def init_channel_state(client, sources):
    """Запоминаем последний ID каждого канала — пропускаем старые сообщения"""
    last_ids = {}

    for idx, username in enumerate(sources):
        # Пауза между запросами, чтоб не спамить Telegram
        if idx > 0:
            await asyncio.sleep(TG_REQUEST_DELAY)

        messages = await safe_get_messages(client, username, limit=1)
        if messages:
            last_ids[username] = messages[0].id

    return last_ids


async def poll_group(client: TelegramClient, sources: list, aggregator_id: int, group_name: str, interval: int = 45):
    """
    Проверяет новые сообщения в каналах каждые `interval` секунд.
    Между проверками каналов — пауза 1.5с, чтоб не было FloodWait.
    """
    # Инициализация
    last_ids = await init_channel_state(client, sources)
    logger.info(f"📡 Поллинг [{group_name}]: {len(last_ids)}/{len(sources)} каналов готовы")

    while True:
        await asyncio.sleep(interval)

        for username in sources:
            await asyncio.sleep(TG_REQUEST_DELAY)

            messages = await safe_get_messages(client, username, limit=2)
            if not messages:
                continue

            # Сортируем от старых к новым
            messages = list(reversed(messages))

            for msg in messages:
                last_id = last_ids.get(username)

                if last_id is None or msg.id > last_id:
                    last_ids[username] = msg.id

                    now_ts = time.time()
                    msg_ts = msg.date.timestamp()
                    delay = now_ts - msg_ts

                    ok = await safe_forward(client, aggregator_id, msg.id, username)

                    if ok:
                        delay_str = f"{delay:.0f}с"
                        if delay > 60:
                            delay_str = f"{delay/60:.1f}мин"
                        logger.info(f"✅ [{delay_str}] [{username}] → [{group_name}]: {str(msg.text or '[медиа]')[:60]}")