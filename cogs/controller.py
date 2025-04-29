from ..init import random, re, time, disnake, commands, MongoClient, config, embed_generator


# noinspection PyUnusedLocal
class Controller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cluster = MongoClient(config.config["database"])
        anon = "AnonChatDev" if config.dev else "AnonChat"
        self.collection = self.cluster[anon].anon
        self.search = self.cluster[anon].search
        self.stats = self.cluster[anon].stats
        self.guild = self.cluster[anon].guilds
        self.economy = self.cluster[anon].economy
        self.rofl = self.cluster[anon].rofl
        self.quest = self.cluster[anon].quest

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.type != disnake.ChannelType.private:
            if message.author.bot:
                return
            if message.channel.id == config.config["channel2"]:
                if message.reference is not None:
                    msg = self.rofl.find_one({'_id': message.reference.message_id})
                    if msg is not None:
                        channel = msg['channel_id']
                        msg_ls = msg['msg_ls']
                        ch = await self.bot.fetch_channel(channel)
                        m = await ch.fetch_message(msg_ls)
                        try:
                            await m.reply(message.content[23::])
                            await message.add_reaction("✅")
                        except:
                            await message.add_reaction("❌")
                        return
                    return
                return
            return

        if message.author.bot:
            return
        try:
            comp = self.collection.find_one({'_id': message.author.id})['comp']
            member = await self.bot.getch_user(comp)
            if member is None:
                try:
                    guild = self.collection.find_one({'_id': comp})['guild']
                    g = await self.bot.fetch_guild(guild)
                    member = await g.fetch_member(int(comp))
                except:
                    comp = 0
                    member = None
        except:
            comp = 0
            member = None

            g = await self.bot.fetch_guild(config.config["guild"])
            ch = await g.fetch_channel(config.config["channel2"])
            webhook = await ch.create_webhook(
                name=f"{message.author.name}",
                avatar=message.author.avatar if message.author.avatar is not None else
                message.author.default_avatar
                )

            if message.attachments:
                files = [await attch.to_file() for attch in message.attachments]
                msg = await webhook.send(
                    message.content, files=files, wait=True,
                    allowed_mentions=disnake.AllowedMentions(
                        roles=False, users=True,
                        everyone=False
                        )
                    )
            else:
                msg = await webhook.send(
                    message.content, wait=True,
                    allowed_mentions=disnake.AllowedMentions(
                        roles=False, users=True,
                        everyone=False
                        )
                    )
            await webhook.delete()
            post = {
                "_id": msg.id,
                "msg_ls": message.id,
                "channel_id": message.channel.id,
                "author_id": message.author.id
                }
            self.rofl.insert_one(post)

        if comp != 0 and member is not None:
            try:
                emoji = self.economy.find_one({'_id': message.author.id})['emoji']
            except:
                emoji = None
            msg_test = message.content.replace(" ", "").replace("\n", "")
            discord_invite_filter = re.compile(
                r"(...)?(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)/?[a-zA-Z\d]+/?"
                )
            check = re.search(discord_invite_filter, msg_test)
            if check:
                self.stats.update_one({"_id": message.author.id}, {"$set": {"banned": 1}})
                emb = disnake.Embed(
                    description="Вы были заблокированны за отправку приглашения на другой сервер.\n"
                                "Если вы хотите обжаловать блокировку, обратитесь за помощью на [сервер поддержки](https://discord.gg/YBzKe7vCYY) AnonChat бота.",
                    color=disnake.Color.red()
                    )
                emb.set_author(name="Вы были заблокированы в AnonChat", icon_url=self.bot.user.avatar)
                await message.author.send(embed=emb)

                lol = {"_id": message.author.id}
                self.collection.delete_one(lol)
                self.search.delete_one(lol)

                lol = {"_id": comp}
                self.collection.delete_one(lol)
                self.search.delete_one(lol)

                emb = embed_generator(
                    description="Ваш собеседник получил блокировку в AnonChat, так как пытался "
                                "отправить приглашение на сервер.",
                    author_name="Конец чата", icon_url=self.bot.user.avatar
                    )

                try:
                    m = await member.send(embed=emb)
                    self.stats.update_one({"_id": member.id}, {"$set": {'stop_m': m.id}})
                except:
                    pass

                emb1 = embed_generator(
                    description="Чат остановлен, так как вы заблокированы\n",
                    author_name="Конец чата", icon_url=self.bot.user.avatar
                    )

                try:
                    m1 = await message.author.send(embed=emb1)
                    self.stats.update_one({"_id": message.author.id}, {"$set": {'stop_m': m1.id}})
                except:
                    pass
                channel = self.bot.get_guild(config.config["guild"]).get_channel(config.config["channel3"])
                emb = disnake.Embed(
                    description=f'{message.author} / {message.author.id} заблокирован за отправку приглашения, вот его сообщение - `{message.content}`',
                    color=disnake.Color.red()
                    )
                emb.set_author(name="Блокировка", icon_url=self.bot.user.avatar)
                return await channel.send(embed=emb)

            try:
                block = self.stats.find_one({'_id': comp})['block']
            except:
                block = 0

            if emoji == 1:
                emoji = random.choice(
                    [
                        '🔥',
                        '❤',
                        '🗿',
                        '👀',
                        '⚠',
                        '👻'
                        ]
                    )
            msg_c = f"{emoji}・{message.content}" if emoji is not None and emoji != 0 and block == 0 and len(
                message.content
                ) > 0 else message.content

            try:
                ref = message.reference.message_id
            except:
                ref = None
            try:
                comp = self.collection.find_one({'_id': message.author.id})['comp']
                history = self.collection.find_one({'_id': comp})['history']
            except:
                comp = None
                history = []

            id_c = self.collection.find_one({'_id': comp})['channel']
            channel = await self.bot.fetch_channel(id_c)
            msg_id = None
            if ref:
                for i in history:
                    if i[1] == ref:
                        msg_id = i[0]
                        break
                    else:
                        continue

            if message.attachments:
                files = [await attch.to_file() for attch in message.attachments]
                try:
                    if msg_id:
                        msgg = await channel.fetch_message(msg_id)
                        msg = await msgg.reply(msg_c, files=files)
                    else:
                        msg = await member.send(msg_c, files=files)
                except:
                    msg = None
            else:
                try:
                    if msg_id:
                        msgg = await channel.fetch_message(msg_id)
                        msg = await msgg.reply(msg_c)
                    else:
                        msg = await member.send(msg_c)
                except:
                    msg = None

            if msg is None:
                pass
            else:
                self.collection.update_one(
                    {"_id": message.author.id}, {"$push": {'history': [message.id, msg.id]}}
                    )
                self.collection.update_one(
                    {"_id": message.author.id}, {"$set": {'afk': int(time.time())}}
                    )
                self.collection.update_one({"_id": message.author.id}, {"$set": {'warned': 0}})

                self.collection.update_one({"_id": comp}, {"$set": {'afk': int(time.time())}})
                self.collection.update_one({"_id": comp}, {"$set": {'warned': 0}})
                self.stats.update_one({"_id": message.author.id}, {"$inc": {'messages': 1}})
                try:
                    gg = self.collection.find_one({'_id': message.author.id})['guild']
                    self.guild.update_one({"_id": gg}, {"$inc": {"messages": 1}})
                except:
                    pass

                quest = self.quest.find_one({'_id': message.author.id})
                if quest is not None:
                    if quest['question'] == 0:
                        return
                    if quest['question'].lower().replace(" ", "") in message.content.lower().replace(" ", ""):
                        amount = random.randint(1, 500)
                        await message.reply(
                            embed=embed_generator(
                                author_name=f"{message.author.name}, вы справились с квестом!", icon_url=message.author.avatar,
                                description=f"**Ваша награда:** `{amount}`<:__:1140642430887137361>"
                                )
                            )
                        self.economy.update_one({"_id": message.author.id}, {"$inc": {'balance': amount}})
                        self.quest.update_one({"_id": message.author.id}, {"$set": {"question": 0}})
                        self.quest.update_one({"_id": message.author.id}, {"$set": {'at_this_chat': 1}})

                post = {
                    "_id": message.author.id,
                    "balance": 0,
                    "items": [],
                    "kd": int(time.time())
                    }
                if 0 == self.economy.count_documents({"_id": message.author.id}):
                    self.economy.insert_one(post)

                if self.economy.find_one({'_id': message.author.id})['kd'] >= int(time.time()):
                    return

                self.economy.update_one(
                    {"_id": message.author.id}, {"$set": {'kd': int(time.time()) + 10}}
                    )
                self.economy.update_one(
                    {"_id": message.author.id}, {"$inc": {'balance': random.randint(1, 10)}}
                    )

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        if before.channel.type != disnake.ChannelType.private:
            return
        else:
            try:
                comp = self.collection.find_one({'_id': before.author.id})['comp']
                member = await self.bot.getch_user(comp)
                if member is None:
                    try:
                        guild = self.collection.find_one({'_id': comp})['guild']
                        g = await self.bot.fetch_guild(guild)
                        member = await g.fetch_member(int(comp))
                    except:
                        comp = 0
                        member = None
            except:
                comp = 0
                member = None
            if comp != 0 and member is not None:
                try:
                    comp = self.collection.find_one({'_id': before.author.id})['comp']
                    id_c = self.collection.find_one({'_id': comp})['channel']
                    channel = await self.bot.fetch_channel(id_c)
                except:
                    channel = None
                try:
                    history = self.collection.find_one({'_id': before.author.id})['history']
                except:
                    history = []
                msg_id = None
                for i in history:
                    if i[0] == before.id:
                        msg_id = i[1]
                    else:
                        continue
                if msg_id is None:
                    try:
                        await before.add_reaction("❌")
                    except:
                        pass
                else:
                    try:
                        emoji = self.economy.find_one({'_id': after.author.id})['emoji']
                    except:
                        emoji = None
                    msg_test = after.content.replace(" ", "").replace("\n", "")
                    discord_invite_filter = re.compile(
                        r"(...)?(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)/?[a-zA-Z\d]+/?"
                        )
                    check = re.search(discord_invite_filter, msg_test)
                    if check:
                        self.stats.update_one({"_id": after.author.id}, {"$set": {"banned": 1}})
                        emb = disnake.Embed(
                            description="Вы были заблокированны за отправку приглашения на другой сервер.\n"
                                        "Если вы хотите обжаловать блокировку, обратитесь за помощью на [сервер поддержки](https://discord.gg/YBzKe7vCYY) AnonChat бота.",
                            color=disnake.Color.red()
                            )
                        emb.set_author(name="Вы были заблокированы в AnonChat", icon_url=self.bot.user.avatar)
                        await after.author.send(embed=emb)

                        lol = {"_id": after.author.id}
                        self.collection.delete_one(lol)
                        self.search.delete_one(lol)

                        lol = {"_id": comp}
                        self.collection.delete_one(lol)
                        self.search.delete_one(lol)

                        emb = embed_generator(
                            description="Ваш собеседник получил блокировку в AnonChat, так как пытался "
                                        "отправить приглашение на сервер.",
                            author_name="Конец чата", icon_url=self.bot.user.avatar
                            )

                        try:
                            m = await member.send(embed=emb)
                            self.stats.update_one({"_id": member.id}, {"$set": {'stop_m': m.id}})
                        except:
                            pass

                        emb1 = embed_generator(
                            description="Чат остановлен, так как вы заблокированы\n",
                            author_name="Конец чата", icon_url=self.bot.user.avatar
                            )

                        try:
                            m1 = await after.author.send(embed=emb1)
                            self.stats.update_one({"_id": after.author.id}, {"$set": {'stop_m': m1.id}})
                        except:
                            pass
                        channel = self.bot.get_guild(config.config["guild"]).get_channel(config.config["channel3"])
                        emb = disnake.Embed(
                            description=f'{after.author} / {after.author.id} заблокирован за отправку приглашения, вот его сообщение - `{after.content}`',
                            color=disnake.Color.red()
                            )
                        emb.set_author(name="Блокировка", icon_url=self.bot.user.avatar)
                        return await channel.send(embed=emb)

                    try:
                        block = self.stats.find_one({'_id': comp})['block']
                    except:
                        block = 0

                    if emoji == 1:
                        emoji = random.choice(
                            [
                                '🔥',
                                '❤',
                                '🗿',
                                '👀',
                                '⚠',
                                '👻'
                                ]
                            )
                    msg_c = f"{emoji}・{after.content}" if emoji is not None and emoji != 0 and block == 0 and len(
                        after.content
                        ) > 0 else after.content
                    try:
                        message = await channel.fetch_message(msg_id)
                        await message.edit(msg_c)
                        await before.add_reaction("✅")
                    except:
                        try:
                            await before.add_reaction("❌")
                        except:
                            pass

                    quest = self.quest.find_one({'_id': after.author.id})
                    if quest is not None:
                        if quest['question'] == 0:
                            return
                        if quest['question'].lower().replace(" ", "") in after.content.lower().replace(" ", ""):
                            amount = random.randint(1, 500)
                            await after.reply(
                                embed=embed_generator(
                                    author_name=f"{after.author.name}, вы справились с квестом!", icon_url=after.author.avatar,
                                    description=f"**Ваша награда:** `{amount}`<:__:1140642430887137361>"
                                    )
                                )
                            self.economy.update_one({"_id": after.author.id}, {"$inc": {'balance': amount}})
                            self.quest.update_one({"_id": after.author.id}, {"$set": {"question": 0}})
                            self.quest.update_one({"_id": after.author.id}, {"$set": {'at_this_chat': 1}})

    @commands.Cog.listener()
    async def on_message_delete(self, before):
        if before.author.bot:
            return
        if before.channel.type != disnake.ChannelType.private:
            return
        else:
            try:
                comp = self.collection.find_one({'_id': before.author.id})['comp']
                member = await self.bot.getch_user(comp)
                if member is None:
                    try:
                        guild = self.collection.find_one({'_id': comp})['guild']
                        g = await self.bot.fetch_guild(guild)
                        member = await g.fetch_member(int(comp))
                    except:
                        comp = 0
                        member = None
            except:
                comp = 0
                member = None
            if comp != 0 and member is not None:
                comp = self.collection.find_one({'_id': before.author.id})['comp']
                id_c = self.collection.find_one({'_id': comp})['channel']
                channel = await self.bot.fetch_channel(id_c)
                history = self.collection.find_one({'_id': before.author.id})['history']
                msg_id = None
                for i in history:
                    if i[0] == before.id:
                        msg_id = i[1]
                    else:
                        continue
                if msg_id is None:
                    pass
                else:
                    message = await channel.fetch_message(msg_id)
                    await message.delete()

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        if user.bot:
            return
        if channel.type != disnake.ChannelType.private:
            return
        else:
            try:
                comp = self.collection.find_one({'_id': user.id})['comp']
                member = await self.bot.getch_user(comp)
                if member is None:
                    try:
                        guild = self.collection.find_one({'_id': comp})['guild']
                        g = await self.bot.fetch_guild(guild)
                        member = await g.fetch_member(int(comp))
                    except:
                        comp = 0
                        member = None
            except:
                comp = 0
                member = None
            if comp != 0 and member is not None:
                try:
                    comp = self.collection.find_one({'_id': user.id})['comp']
                    channell = self.collection.find_one({'_id': comp})['channel']
                    channel = await self.bot.fetch_channel(channell)
                    async with channel.typing():
                        pass
                except:
                    pass


def setup(bot):
    bot.add_cog(Controller(bot))
