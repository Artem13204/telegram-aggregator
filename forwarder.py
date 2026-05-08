# =============================================
# forwarder.py — ЛОГИКА ПЕРЕСЫЛКИ СООБЩЕНИЙ
# =============================================

from telethon.tl.types import Message   # Тип "сообщение" из Telethon


async def forward_message(client, event, aggregator_channel_id: int):
    """
    Пересылает одно сообщение из канала-источника в канал-агрегатор.

    client               — наш Telegram клиент (через него отправляем)
    event                — событие "новое сообщение" (содержит само сообщение)
    aggregator_channel_id — ID канала, куда пересылаем
    """

    # Достаём само сообщение из события
    message: Message = event.message

    # Узнаём название канала-источника
    # event.chat — информация о чате, откуда пришло сообщение
    source_chat = await event.get_chat()
    source_name = getattr(source_chat, "title", "Неизвестный канал")

    try:
        # ── Пересылаем сообщение ──
        # forward_messages — стандартный форвард, как если бы ты нажал "Переслать" в Telegram.
        # Сохраняет медиа, текст, форматирование и показывает источник.
        await client.forward_messages(
            entity=aggregator_channel_id,   # Куда пересылаем
            messages=message.id,            # ID сообщения которое пересылаем
            from_peer=event.chat_id,        # Из какого чата берём
        )

        # Выводим в консоль что всё прошло хорошо (для отладки)
        print(f"✅ Переслано из [{source_name}]: {str(message.text or '[медиа]')[:60]}")

    except Exception as e:
        # Если что-то пошло не так — показываем ошибку, но НЕ падаем.
        # Программа продолжит работать и обработает следующие сообщения.
        print(f"❌ Ошибка при пересылке из [{source_name}]: {e}")
