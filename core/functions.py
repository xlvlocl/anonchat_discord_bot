from ..init import MongoClient, config, disnake, time
from ..core.database_config import post_locale, post_stats

cluster = MongoClient(config.config["database"])
anon = "AnonChatDev" if config.dev else "AnonChat"

collection = cluster[anon].anon
searchX = cluster[anon].search
statsX = cluster[anon].stats
captcha = cluster[anon].captcha
guildX = cluster[anon].guilds
economy = cluster[anon].economy
local = cluster[anon].anon_local
quest = cluster[anon].quest


def embed_generator(**kwargs):
    """
    :param kwargs: title, description, author_name, icon_url, color: [red, green, None]
    :return: disnake.Embed
    """
    keys = kwargs.keys()
    if 'color' in keys:
        if kwargs['color'] is None:
            embed = disnake.Embed(color=disnake.Color.darker_grey())
        elif kwargs['color'] == "red":
            embed = disnake.Embed(color=disnake.Color.red())
        else:
            embed = disnake.Embed(color=disnake.Color.green())
    else:
        embed = disnake.Embed(color=disnake.Color.darker_grey())

    embed.title = kwargs["title"] if 'title' in keys else ""
    embed.description = kwargs["description"] if 'description' in keys else ""
    embed.set_author(name=kwargs["author_name"] if 'author_name' in keys else "", icon_url=kwargs["icon_url"] if 'icon_url' in keys else "")
    return embed


def check_ban():
    def decorator(func):
        async def wrapper(inter, bot, *args, **kwargs):
            try:
                try:
                    ban = statsX.find_one({'_id': inter.author.id})['banned']
                except:
                    ban = 0
                if int(ban) == 1:
                    emb = embed_generator(author_name="Вы не можете использовать бота.", icon_url=bot.user.avatar)
                    try:
                        await inter.send(embed=emb, ephemeral=True)
                    except:
                        await inter.edit_original_message(embed=emb, ephemeral=True)
                    return
                else:
                    pass
            except:
                pass
            return await func(inter, bot, *args, **kwargs)

        return wrapper

    return decorator


@check_ban()
async def stop(inter, bot, locale: bool = False):
    try:
        findd = collection.find_one({'_id': inter.author.id})['comp']
    except:
        findd = 0
    if findd != 0:
        lol = {"_id": inter.author.id}
        collection.delete_one(lol)
        searchX.delete_one(lol)
        try:
            quest.update_one({"_id": inter.author.id}, {"$set": {'at_this_chat': 0}})
            quest.update_one({"_id": inter.author.id}, {"$set": {'question': 0}})
        except:
            pass

        lol = {"_id": findd}
        collection.delete_one(lol)
        searchX.delete_one(lol)
        try:
            quest.update_one({"_id": findd}, {"$set": {'at_this_chat': 0}})
            quest.update_one({"_id": findd}, {"$set": {'question': 0}})
        except:
            pass

        member = await bot.getch_user(int(findd))
        if member is None:
            try:
                guild = collection.find_one({'_id': int(findd)})['guild']
                g = await bot.fetch_guild(guild)
                member = await g.fetch_member(int(findd))
            except:
                member = None

        buttons = disnake.ui.View()
        buttons.add_item(
            disnake.ui.Button(label='', emoji='👍', style=disnake.ButtonStyle.gray, custom_id="like")
            )
        buttons.add_item(
            disnake.ui.Button(
                label='', emoji='👎', style=disnake.ButtonStyle.gray, custom_id="dlike"
                )
            )
        buttons.add_item(
            disnake.ui.Button(
                label='', emoji='⚠', style=disnake.ButtonStyle.gray, custom_id="report"
                )
            )

        try:
            emb = embed_generator(
                description="Ваш собеседник остановил чат, увы и ах...",
                author_name="Конец чата", icon_url=bot.user.avatar
                )

            m = await member.send(embed=emb, view=buttons)
            statsX.update_one({"_id": member.id}, {"$set": {'stop_m': m.id}})
        except:
            pass
        try:
            emb1 = embed_generator(
                description="Вы остановили чат, класс...",
                author_name="Конец чата", icon_url=bot.user.avatar
                )

            m1 = await inter.author.send(embed=emb1, view=buttons)
            statsX.update_one({"_id": inter.author.id}, {"$set": {'stop_m': m1.id}})
        except:
            pass

        emb = embed_generator(
            description="Вы остановили чат и вышли из поиска.",
            author_name="Конец чата", icon_url=bot.user.avatar
            )

        await inter.send(embed=emb, ephemeral=True)
    else:
        try:
            searc = searchX.find_one({'_id': inter.author.id})
        except:
            searc = 0

        if locale:
            post_locale(guild_id=inter.guild.id)
            searcc = local.find_one({'_id': inter.guild.id})['list']
            searc2 = []
            for i in searcc:
                searc2.append(i['_id'])
        else:
            searc2 = []

        if searc or (inter.author.id in searc2):
            lol = {"_id": inter.author.id}
            collection.delete_one(lol)
            searchX.delete_one(lol)
            if locale:
                local.update_one({"_id": inter.guild.id}, {"$set": {'list': []}})

            emb1 = embed_generator(
                description="Вы вышли из режима поиска",
                author_name="Поиск окончен", icon_url=bot.user.avatar
                )
            await inter.send(embed=emb1, ephemeral=True)
        else:
            emb1 = embed_generator(
                description="Чтобы войти в режим поиска напишите команду </start:1238618601393754284>\n",
                author_name="Вы не находитесь в режиме поиска", icon_url=bot.user.avatar
                )
            await inter.send(embed=emb1, ephemeral=True)


@check_ban()
async def search_user(inter, bot, frombtn: bool = False, locale: bool = False):
    if locale:
        post_locale(guild_id=inter.guild.id)
        searcc = local.find_one({'_id': inter.guild.id})['list']
        find2 = []
        for i in searcc:
            find2.append(i['_id'])
    else:
        find2 = []

    find = searchX.find_one({'_id': inter.author.id})
    if (inter.author.id in find2) or find is not None:
        emb = embed_generator(
            description="Вы можете отключить его в любой момент!",
            author_name="Вы уже находитесь в режиме поиска", icon_url=bot.user.avatar
            )
        return await inter.send(embed=emb, ephemeral=True)

    comp = collection.find_one({'_id': inter.author.id})

    if comp is not None:
        emb = embed_generator(
            description="Чтобы сменить собеседника нажмите на кнопку \"Стоп\" для остановки чата и начните новый поиск!" if frombtn else "Чтобы сменить собеседника введите команду </stop:1180457805069692929> для остановки чата и начните новый поиск!",
            author_name="Вы уже состоите в анонимном чате", icon_url=bot.user.avatar
            )
        return await inter.send(embed=emb, ephemeral=True)

    if locale:
        rows = local.find_one({'_id': inter.guild.id})['list']
    else:
        rows = searchX.find()
    succes = False
    for row in rows:
        member = await bot.getch_user(row["_id"])
        if member is None:
            try:
                guild = row['guild']
                g = await bot.fetch_guild(guild)
                member = await g.fetch_member(int(row["_id"]))
            except:
                continue
        try:
            last_check = collection.find_one({'_id': row["_id"]})['comp']
        except:
            last_check = 0

        if last_check != 0:
            searchX.delete_one({"_id": row["_id"]})
            if locale:
                local.update_one({"_id": inter.guild.id}, {"$set": {'list': []}})
            continue

        try:
            rep = statsX.find_one({'_id': row["_id"]})["rep"]
        except:
            rep = 0
        if rep >= 0:
            emoji = "👍"
        else:
            emoji = "👎"
        buttons = disnake.ui.View()
        try:
            stats = statsX.find_one({'_id': inter.author.id})['block']
        except:
            stats = 0

        if stats == 1:
            buttons.add_item(
                disnake.ui.Button(
                    label='Включить префиксы', emoji="<:emoji_39:963680447609573396>",
                    style=disnake.ButtonStyle.gray, custom_id=f"unblock"
                    )
                )
        else:
            buttons.add_item(
                disnake.ui.Button(
                    label="Отключить префиксы", emoji="<:emoji_38:963679797991575572>",
                    style=disnake.ButtonStyle.gray, custom_id=f"block"
                    )
                )

        try:
            stats = statsX.find_one({'_id': row["_id"]})['block']
        except:
            stats = 0
        buttons_x = disnake.ui.View()
        if stats == 1:
            buttons_x.add_item(
                disnake.ui.Button(
                    label='Включить префиксы', emoji="<:emoji_39:963680447609573396>",
                    style=disnake.ButtonStyle.gray, custom_id=f"unblock"
                    )
                )
        else:
            buttons_x.add_item(
                disnake.ui.Button(
                    label="Отключить префиксы", emoji="<:emoji_38:963679797991575572>",
                    style=disnake.ButtonStyle.gray, custom_id=f"block"
                    )
                )

        emb = embed_generator(
            description=f"Можете начинать общаться!\nРепутация вашего собеседника: {rep}{emoji}",
            author_name="Собеседник найден", icon_url=bot.user.avatar
            )
        if 0 == statsX.count_documents({"_id": inter.author.id}):
            rep1 = 0
        else:
            try:
                rep1 = statsX.find_one({'_id': inter.author.id})["rep"]
            except:
                rep1 = 0

        if rep1 >= 0:
            emoji1 = "👍"
        else:
            emoji1 = "👎"

        if locale:
            search1 = False
        else:
            search1 = searchX.find_one({'_id': row["_id"]})
        if search1:
            start_time = searchX.find_one({"_id": row["_id"]})['wait_time']

            elapsed_time = int(time.time()) - start_time

            searchX.update_one({"_id": "super"}, {"$push": {"timings": int(elapsed_time)}})

            days = elapsed_time // (24 * 3600)
            elapsed_time %= (24 * 3600)
            hours = elapsed_time // 3600
            elapsed_time %= 3600
            minutes = elapsed_time // 60
            seconds = elapsed_time % 60

            formatted_time = ""
            formatted_time += str(int(days)) + "д " if days > 0 else ""
            formatted_time += str(int(hours)) + "ч " if hours > 0 else ""
            formatted_time += str(int(minutes)) + "мин " if minutes > 0 else ""
            formatted_time += str(int(seconds)) + "сек" if seconds > 0 else ""

            emb11 = embed_generator(
                description=f"Можете начинать общаться!\nРепутация вашего собеседника: **{rep1}**{emoji1}\n\n"
                            f"Вы ожидали собеседника: `{formatted_time}`",
                author_name="Собеседник найден", icon_url=bot.user.avatar
                )
        else:
            emb11 = embed_generator(
                description=f"Можете начинать общаться!\nРепутация вашего собеседника: {rep1}{emoji1}\n",
                author_name="Собеседник найден", icon_url=bot.user.avatar
                )
        try:
            a = economy.find_one({'_id': member.id})["emoji"]
        except:
            a = None
        try:
            if a is not None:
                msg = await inter.author.send(embed=emb, view=buttons)
            else:
                msg = await inter.author.send(embed=emb)
        except:
            lol = {"_id": inter.author.id}
            searchX.delete_one(lol)
            if locale:
                local.update_one({"_id": inter.guild.id}, {"$set": {'list': []}})
        else:
            try:
                a = economy.find_one({'_id': inter.author.id})["emoji"]
            except:
                a = None
            try:
                if a is not None:
                    msg1 = await member.send(embed=emb11, view=buttons_x)
                else:
                    msg1 = await member.send(embed=emb11)
            except:
                emb2 = embed_generator(
                    description="У вашего собеседника закрыты личные сообщения, поэтому бот не сможет вас соединить... Поиск продолжается!",
                    author_name="Закрытая личка", icon_url=bot.user.avatar
                    )
                lol = {"_id": member.id}
                searchX.delete_one(lol)
                if locale:
                    local.update_one({"_id": inter.guild.id}, {"$set": {'list': []}})
                await inter.author.send(embed=emb2)
                continue
            else:
                lol = {"_id": member.id}
                searchX.delete_one(lol)
                if locale:
                    local.update_one({"_id": inter.guild.id}, {"$set": {'list': []}})

                lol = {"_id": inter.author.id}
                searchX.delete_one(lol)
                if locale:
                    local.update_one({"_id": inter.guild.id}, {"$set": {'list': []}})

                post1 = {
                    "_id": inter.author.id,
                    "guild": inter.guild.id if inter.guild is not None else 0,
                    "comp": member.id,
                    "channel": msg.channel.id,
                    "history": [],
                    "afk": time.time(),
                    "warned": 0
                    }
                collection.insert_one(post1)

                try:
                    guild = await bot.fetch_guild(row["guild"])
                    g = guild.id
                except:
                    g = 0

                post2 = {
                    "_id": member.id,
                    "guild": g,
                    "comp": inter.author.id,
                    "channel": msg1.channel.id,
                    "history": [],
                    "afk": time.time(),
                    "warned": 0
                    }

                collection.insert_one(post2)

                post_stats(id=inter.author.id)
                statsX.update_one({"_id": inter.author.id}, {"$set": {'bot_chat_id': msg.channel.id}})
                statsX.update_one({"_id": inter.author.id}, {"$set": {'last_comp': member.id}})

                try:
                    chats = statsX.find_one({'_id': inter.author.id})['chats']
                except:
                    chats = 0
                statsX.update_one({"_id": inter.author.id}, {"$set": {'chats': chats + 1}})

                post_stats(id=member.id)
                statsX.update_one({"_id": member.id}, {"$set": {'bot_chat_id': msg1.channel.id}})
                statsX.update_one({"_id": member.id}, {"$set": {'last_comp': inter.author.id}})

                try:
                    chats1 = statsX.find_one({'_id': member.id})['chats']
                except:
                    chats1 = 0
                statsX.update_one({"_id": member.id}, {"$set": {'chats': chats1 + 1}})

                try:
                    gg = collection.find_one({'_id': member.id})['guild']
                    chats = guildX.find_one({'_id': gg})['chats']
                    guildX.update_one({"_id": gg}, {"$set": {"chats": chats + 1}})
                except:
                    pass

                try:
                    gg = collection.find_one({'_id': inter.author.id})['guild']
                    chats = guildX.find_one({'_id': gg})['chats']
                    guildX.update_one({"_id": gg}, {"$set": {"chats": chats + 1}})
                except:
                    pass

                succes = True

                buttons = disnake.ui.View()
                buttons.add_item(
                    disnake.ui.Button(
                        label='', emoji='👍', style=disnake.ButtonStyle.gray, custom_id="like",
                        disabled=True
                        )
                    )
                buttons.add_item(
                    disnake.ui.Button(
                        label='', emoji='👎', style=disnake.ButtonStyle.gray,
                        custom_id="dlike", disabled=True
                        )
                    )
                buttons.add_item(
                    disnake.ui.Button(
                        label='', emoji='⚠', style=disnake.ButtonStyle.gray,
                        custom_id="report", disabled=True
                        )
                    )

                try:
                    channel1 = await bot.fetch_channel(
                        statsX.find_one({'_id': member.id})['bot_chat_id']
                        )
                except:
                    channel1 = None
                if channel1 is None:
                    pass
                else:
                    try:
                        m1_id = statsX.find_one({'_id': member.id})['stop_m']
                        msg1 = await channel1.fetch_message(m1_id)
                        await msg1.edit(view=buttons)
                    except:
                        pass
                try:
                    channel2 = await bot.fetch_channel(
                        statsX.find_one({'_id': inter.author.id})['bot_chat_id']
                        )
                except:
                    channel2 = None

                if channel2 is None:
                    pass
                else:
                    try:
                        m2_id = statsX.find_one({'_id': inter.author.id})['stop_m']
                        msg2 = await channel2.fetch_message(m2_id)
                        await msg2.edit(view=buttons)
                    except:
                        pass

                break

    if succes:
        if not frombtn:
            return await inter.delete_original_message()
        else:
            return
    post2 = {
        "_id": inter.author.id,
        "guild": inter.guild.id if inter.guild is not None else 0,
        "wait_time": int(time.time())
        }
    if locale:
        local.update_one({"_id": inter.guild.id}, {"$push": {'list': post2}})
    else:
        searchX.insert_one(post2)

    if not locale:
        list_of_times = searchX.find_one({"_id": "super"})["timings"]
        length = len(list_of_times)
        total = 0
        for i in list_of_times:
            total += int(i)

        srednee = total / length

        days = srednee // (24 * 3600)
        srednee %= (24 * 3600)
        hours = srednee // 3600
        srednee %= 3600
        minutes = srednee // 60
        seconds = srednee % 60

        formatted_time = ""
        formatted_time += str(int(days)) + "д " if days > 0 else ""
        formatted_time += str(int(hours)) + "ч " if hours > 0 else ""
        formatted_time += str(int(minutes)) + "мин " if minutes > 0 else ""
        formatted_time += str(int(seconds)) + "сек" if seconds > 0 else ""

        desc = ("*К сожалению, собеседника найти не удалось.*"
                "\n*Однако, вы можете остаться в режиме поиска и ждать лучших времён!*\n\n"
                f"Среднее время ожидания собеседника: `{formatted_time}`")
    else:
        desc = ("*К сожалению, собеседника найти не удалось.*\n"
                "*Однако, вы можете остаться в режиме поиска и ждать лучших времён!*")

    emb = embed_generator(
        description=desc,
        author_name="Никого нету", icon_url=bot.user.avatar,
        )

    await inter.send(embed=emb, ephemeral=True)
