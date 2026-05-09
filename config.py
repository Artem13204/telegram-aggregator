# =============================================
# config.py — НАСТРОЙКИ БОТА
# Здесь ты описываешь группы каналов.
# Каждая группа — это список источников + свой канал-агрегатор.
# =============================================

CHANNEL_GROUPS = [
    {
        # Название группы — только для удобства, в Telegram не отображается
        "name": "Крипта:арбитражники и флиперы",

        "sources": [
        "@hoterrekt",
        "@ArturLudit",
        "@crypto_fl1p",
        "@hotered",
        "@temkabossa1",
        "@t2mcrypto",
        "@CryptoMriya",
        "@saunacrypto",
        "@BurgerMoneyMaker",   
        "@freecallsbabki",
        "@muhaebet",
        "@loz1eFliper",
        "@vorxicincrypto",
        "@oncrypto3",
        "@shflipper",
        "@Den4ikStradaet",
        "@cryptozoro04",
        "@velouur_crypto",
        "@artypost",
        "@firgeit12",
        "@fxckcrpt",
        "@skrypto37",
        "@bermizdelaet",
        "@AbuzikLudit",
        "@twix1444",
        "@dalshe_menshe_crypto",
        "@Finder_Main",
        "@diarypesto",
        "@diary_toyoshik",
        "@kazukiprime",
        "@zamokludit",
        "@MamontynokREKT",
        "@sanchez_works",
        "@AbuzikLudit",
        "@cryptosvin",
        ],

        # ID канала-агрегатора куда пересылать сообщения из этой группы
        # Как узнать ID: перешли сообщение из канала боту @userinfobot
        "aggregator_id": -1003858725183,
    },

    {
        "name": "Вайбкодеры",

        "sources": [
        "@deployladeploy",
        "@timurtaepov",
        "@insuline_eth",
        "@firsovventure",
        "@ventureStuff",
        "@alongapps",
        "@pyro17web3",
        "@aialfred",
        "@digitalbios",
        "@serafimlivestream",
        "@antiaiaiclub",
        "@theshadeth",
        "@maxshitpostit",
        "@sdgsdfhdfdfh",
        "@mister_sosister"
        ],

        "aggregator_id": -1003905453657,
    },

    # Хочешь добавить ещё одну группу? Скопируй блок выше и вставь сюда ↓
]
