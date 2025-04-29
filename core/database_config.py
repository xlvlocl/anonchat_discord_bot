from ..init import MongoClient, config

cluster = MongoClient(config.config["database"])
anon = "AnonChatDev" if config.dev else "AnonChat"

collection = cluster[anon].anon
search = cluster[anon].search
statsX = cluster[anon].stats
captcha = cluster[anon].captcha
guildX = cluster[anon].guilds
economy = cluster[anon].economy
local = cluster[anon].anon_local


def post_stats(**kwargs):
    post = {
        "_id": kwargs["id"],
        "messages": 0,
        "chats": 0,
        "rep": 0,
        "warns": 0,
        "last_comp": 0,
        "bot_chat_id": 0,
        "banned": 0,
        "stop_m": 0,
        "aboutme": "Не указано",
        "age": 0,
        "name": "Не указано",
        "gender": "Не указан",
        "mode": 0,
        }
    if 0 == statsX.count_documents({"_id": kwargs["id"]}):
        statsX.insert_one(post)
    else:
        return 0


def post_locale(**kwargs):
    post = {
        "_id": kwargs["guild_id"],
        "list": [],
        }
    if 0 == local.count_documents({"_id": kwargs["guild_id"]}):
        local.insert_one(post)
    else:
        return 0
