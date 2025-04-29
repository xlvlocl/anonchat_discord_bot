import random

from ..init import (asyncio, datetime, time, disnake, config, commands, tasks, logger,
                  MongoClient, requests, embed_generator, CommandNotFound)


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cluster = MongoClient(config.config["database"])
        anon = "AnonChatDev" if config.dev else "AnonChat"
        self.collection = self.cluster[anon].anon
        self.search = self.cluster[anon].search
        self.coll = self.cluster[anon].guilds
        self.quest = self.cluster[anon].quest

        self.status.start()
        self.sdc.start()
        self.boticord_timer.start()
        self.afk.start()
        self.questblyat.start()

    def cog_unload(self):
        self.status.close()
        self.sdc.close()
        self.boticord_timer.close()
        self.afk.close()
        self.questblyat.close()
        return

    # noinspection PyUnusedLocal
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            pass

    @tasks.loop(seconds=3600)
    async def questblyat(self):
        await self.bot.wait_until_ready()
        coll = list(self.collection.find())
        random.shuffle(coll)

        i = None
        for x in coll:
            q = self.quest.find_one({'_id': x["_id"]})
            try:
                if q['question'] == 0 and q['at_this_chat'] == 0:
                    i = x
                    break
                else:
                    continue
            except:
                i = x
                break

        if i is None:
            return

        member = await self.bot.getch_user(int(i["_id"]))
        if member is None:
            try:
                guild = self.collection.find_one({'_id': int(i["_id"])})['guild']
                g = await self.bot.fetch_guild(guild)
                member = await g.fetch_member(int(i["_id"]))
            except:
                member = None

        if member is not None:

            questions = {
                0: 'Каковы основные причины изменения климата?',
                1: 'Что такое искусственный интеллект и как он работает?',
                2: 'Как развивается квантовая физика в современном мире?',
                3: 'Что такое блокчейн и как он используется?',
                4: 'Какие существуют основные философские направления?',
                5: 'Почему Луна оказывает влияние на приливы и отливы?',
                6: 'Какие существуют способы изучения иностранных языков?',
                7: 'Как работает человеческий мозг и как развивается память?',
                8: 'Что такое криптовалюта и как она функционирует?',
                9: 'Каковы основные достижения в космических исследованиях?',
                10: 'Как биология объясняет эволюцию живых существ?',
                11: 'Какие существуют основные принципы демократического управления?',
                12: 'Как устроена Вселенная с точки зрения астрономии?',
                13: 'Что такое виртуальная реальность и какие у нее перспективы?',
                14: 'Как влияет музыка на настроение человека?',
                15: 'Какие существуют способы повышения продуктивности?',
                16: 'Почему важно следить за качеством сна?',
                17: 'Что такое генетика и как она влияет на наследственность?',
                18: 'Как работает экономика и в чем ее основные законы?',
                19: 'Какие инновации происходят в медицине?',
                20: 'Что такое биотехнологии и как они развиваются?',
                21: 'Какие ключевые открытия сделаны в области нейробиологии?',
                22: 'Как развивается наука о питании и здоровом образе жизни?',
                23: 'Что такое устойчивое развитие и как его достичь?',
                24: 'Как влияют социальные сети на общество и психологию человека?',
                25: 'Что такое биоинформатика и как она используется в исследованиях?',
                26: 'Как искусственный интеллект изменяет рынок труда?',
                27: 'Что такое глобализация и как она влияет на экономику?',
                28: 'Какие новые технологии используются в сельском хозяйстве?',
                29: 'Что такое машинное обучение и как оно применяется?',
                30: 'Какие основные черты культуры различных цивилизаций?',
                31: 'Как работает Интернет и какие технологии за ним стоят?',
                32: 'Что такое квантовые компьютеры и как они работают?',
                33: 'Какие современные подходы к решению экологических проблем?',
                34: 'Как работает искусственный интеллект в медицине?',
                35: 'Что такое синтетическая биология и какие у нее перспективы?',
                36: 'Как новые технологии меняют систему образования?',
                37: 'Что такое цифровая безопасность и как защитить данные?',
                38: 'Какие новые открытия сделаны в области психологии?',
                39: 'Что такое когнитивные науки и как они развиваются?',
                40: 'Как развивалась история искусства и какие основные направления?',
                41: 'Что такое метеорология и как она помогает прогнозировать погоду?',
                42: 'Какие ключевые аспекты культуры разных народов мира?',
                43: 'Как развивается искусство программирования и компьютерные науки?',
                44: 'Что такое кибербезопасность и как она работает?',
                45: 'Какие изменения происходят в политических системах мира?',
                46: 'Что такое геном человека и как его изучают?',
                47: 'Какие достижения сделаны в робототехнике?',
                48: 'Как новые материалы меняют промышленность и строительство?',
                49: 'Что такое нанотехнологии и как они используются?',
                50: 'Какая твоя любимая книга?',
                51: 'Какое твоё любимое время года?',
                52: 'Чем страдаешь в свободное время?',
                53: 'Какие вкусняхи любишь больше всего?',
                54: 'Какой твой любимый цвет?',
                55: 'У тебя есть животные дома?',
                56: 'Где хочешь побывать?',
                57: 'Какие фильмы тебе нравятся?',
                58: 'У тебя есть хобби?',
                59: 'Спортом занимаешься?',
                60: 'У тебя есть любимый актёр/актриса?',
                61: 'Твой любимый музыкальный жанр?',
                62: 'Тебе больше нравится море или горы?',
                63: 'Быть невидимым или быть бессмертным?',
                64: 'Ты любишь путешествовать?',
                65: 'Во что любишь играть?',
                66: 'Твой любимый праздник?',
                67: 'Тебе нравится готовить?',
                68: 'Какую страну ты мечтаешь посетить?',
                69: 'Вечер или день?',
                70: 'Твоя любимая погода?',
                71: 'Чему хочешь научиться?',
                72: 'Твоя любимая песня?',
                73: 'Чай али кофе?',
                74: 'Фантастика или фэнтези?',
                75: 'Любишь сладости?',
                76: 'На велосипеде катаешься?',
                77: 'Какой твой любимый вид отдыха?',
                78: 'Чем мечтаешь заниматься в будущем?',
                79: 'Ты больше любишь кошек или собак?',
                80: 'Любишь кино?',
                81: 'Какие сериалы нравятся?',
                82: 'Какую страну не поситишь никогда?',
                83: 'Какой твой любимый фрукт?',
                84: 'Зоопарк или аквапарк?',
                85: 'Солнечно или пасмурно?',
                86: 'Любишь морепродукты?',
                87: 'В настолки играешь?',
                88: 'Какой фильм на репите смотерть будешь?',
                89: 'Твоя любимая книга?',
                90: 'Ты любишь ходить на концерты?',
                91: 'Какую музыку ты слушаешь, когда хочешь расслабиться?',
                92: 'Го в доту?',
                93: 'Го в кс?',
                94: 'Го в пабг?',
                95: 'Какие шмотки любишь?',
                96: 'Любишь фотографировать?',
                97: 'Какое место в твоем городе тебе нравится больше всего?',
                98: 'Ты любишь рисовать?',
                99: 'Какой у тебя любимый аромат?'
                }
            try:
                used_phrases = self.quest.find_one({"_id": member.id})['list_of_questions']
            except:
                used_phrases = []
            q, w = None, None
            for i in range(len(questions)):
                while True:
                    random_key = random.choice(list(questions.keys()))
                    if random_key not in used_phrases:
                        used_phrases.append(random_key)
                        q, w = questions[random_key], random_key
                        break
                break
            if q is None or w is None:
                q, w = questions[99], 99
            quest = (f"Напиши собеседнику `{q}`\n\n"
                     f"-# ⚠︎ Важно: для того, чтобы квест был пройден, вы должны вставить вопрос в сообщение (можно со строчной буквы), "
                     f"можно как угодно это оформить, главное не менять сам вопрос. "
                     f"Для удобства копирования ниже представлена его копия.\n\n"
                     f"-# **Запрещено говорить собеседнику о вашем квесте, чтобы не разрушать атмосферу в чате. "
                     f"Вы можете не выполнять квест, он автоматически пропадёт при переходе к другому собеседнику. "
                     f"В качестве наказания собедседник может подать на вас жалобу. "
                     f"Вы получите предупреждение, а собеседник вознаграждение.**")
            emb = embed_generator(author_name=f"Случайный квест", icon_url=member.avatar, description=quest)
            try:
                msg = await member.send(embed=emb)
                await msg.reply(q)
            except:
                pass
            else:
                post = {
                    "_id": member.id,
                    "question": q,
                    "list_of_questions": [w],
                    "at_this_chat": 0
                    }
                if 0 == self.quest.count_documents({"_id": member.id}):
                    self.quest.insert_one(post)
                else:
                    self.quest.update_one({"_id": member.id}, {"$push": {"list_of_questions": w}})
                    self.quest.update_one({"_id": member.id}, {"$set": {"question": q}})

    @tasks.loop(seconds=600)
    async def afk(self):
        await self.bot.wait_until_ready()
        members = self.collection.find()
        for i in members:
            if int(i["afk"]) + 3600 * 24 * 3 < int(time.time()):
                if i["warned"] == 1:
                    if int(i["afk"]) + 3600 * 24 * 3 + 12 * 3600 < int(time.time()):
                        self.collection.delete_one({"_id": i["_id"]})
                        self.collection.delete_one({"_id": i["comp"]})

                        member = await self.bot.getch_user(int(i["_id"]))
                        if member is None:
                            try:
                                guild = self.collection.find_one({'_id': int(i["_id"])})['guild']
                                g = await self.bot.fetch_guild(guild)
                                member = await g.fetch_member(int(i["_id"]))
                            except:
                                member = None
                        if member is not None:
                            emb = embed_generator(
                                description="Т.к. вы не проявляли активность в чате более трёх дней, вы были отключены от диалога",
                                author_name="Вы были отключены от диалога", icon_url=self.bot.user.avatar
                                )
                            try:
                                await member.send(embed=emb)
                            except:
                                pass
                else:
                    self.collection.update_one({"_id": i["_id"]}, {"$set": {"warned": 1}})
                    member = await self.bot.getch_user(int(i["_id"]))
                    if member is None:
                        try:
                            guild = self.collection.find_one({'_id': int(i["_id"])})['guild']
                            g = await self.bot.fetch_guild(guild)
                            member = await g.fetch_member(int(i["_id"]))
                        except:
                            member = None
                    if member is not None:
                        emb = embed_generator(
                            description="Чтобы вас не отключили от диалога, пожалуйста, продолжите общаться с вашим собеседником в течении 12 часов :)",
                            author_name="Вы не проявляли активность в чате более трёх дней", icon_url=self.bot.user.avatar
                            )
                        try:
                            await member.send(embed=emb)
                        except:
                            pass

    @tasks.loop(seconds=3600)
    async def sdc(self):
        await self.bot.wait_until_ready()
        if config.dev:
            return
        stats = {'servers': len(self.bot.guilds), "shards": 1}
        response = requests.post(
            url='https://api.server-discord.com/v2/bots/1180439411062734949/stats', headers={
                "Authorization": config.config['SDC'],
                'Content-Type': 'application/json'
                },
            json=stats
            )
        if response.status_code == 200:
            pass
        else:
            logger.error(str(response.status_code) + " SDC")

    @tasks.loop(seconds=3600)
    async def boticord_timer(self):
        await self.bot.wait_until_ready()
        if config.dev:
            return
        stats = {'servers': len(self.bot.guilds)}
        response = requests.post(
            url='https://api.boticord.top/v3/bots/1180439411062734949/stats', headers={
                "Authorization": config.config['Boticord'],
                'Content-Type': 'application/json'
                },
            json=stats
            )
        if response.status_code == 201:
            pass
        else:
            logger.error(str(response.status_code) + " Boticord")

    @tasks.loop(seconds=30)
    async def status(self):
        await self.bot.wait_until_ready()
        await self.bot.change_presence(
            status=disnake.Status.online,
            activity=disnake.Activity(name=f"/help", type=disnake.ActivityType.playing),
            )
        await asyncio.sleep(15)
        await self.bot.change_presence(
            status=disnake.Status.online,
            activity=disnake.Activity(
                name=f"за {len(self.bot.guilds)} серверами", type=disnake.ActivityType.watching
                ),
            )

    @commands.Cog.listener("on_member_remove")
    async def leave(self, member):
        if config.dev:
            return
        lol1 = {"_id": member.id}
        self.search.delete_one(lol1)

        mem = self.collection.find_one({"_id": member.id})

        if mem is None:
            return

        comp_id = mem['comp'] if "comp" in mem.keys() else 0

        lol = {"_id": member.id}
        self.collection.delete_one(lol)

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

        if comp_id != 0:
            lol2 = {"_id": comp_id}
            self.collection.delete_one(lol2)
            memberx = await self.bot.getch_user(comp_id)
            try:
                await memberx.send(
                    embed=embed_generator(
                        description="Ваш собеседник остановил чат, увы и ах...\n",
                        author_name="Конец чата", icon_url=self.bot.user.avatar
                        ),
                    view=buttons
                    )
            except:
                pass
        try:
            emb1 = embed_generator(
                description="Вы остановили чат, класс...\n",
                author_name="Конец чата", icon_url=self.bot.user.avatar
                )
            await member.send(embed=emb1, view=buttons)
        except:
            pass

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        if config.dev:
            return
        lol = {"_id": guild.id}
        self.coll.delete_one(lol)

        peoplex = self.collection.find()
        for people in peoplex:
            comp_id = people["comp"] if "comp" in people.keys() else 0
            guilde = people["guild"] if "guild" in people.keys() else 0
            try:
                guild_of_comp = self.collection.find_one({"_id": comp_id})['guild']
            except:
                guild_of_comp = 0
            if (guilde == guild.id) or guild_of_comp == guild.id:
                member = await self.bot.getch_user(people["_id"])
                memberx = await self.bot.getch_user(comp_id)
                if member is None and memberx is not None:
                    a = {"_id": people["_id"]}
                    self.collection.delete_one(a)
                    self.search.delete_one(a)

                    try:
                        await memberx.send(
                            embed=embed_generator(
                                description="Бота удалили с вашего сервера или с сервера вашего собеседника. Я вынужен отключить вас.\n",
                                author_name="Конец чата", icon_url=self.bot.user.avatar
                                )
                            )
                    except:
                        pass
                if memberx is None and member is not None:
                    a = {"_id": comp_id}
                    self.collection.delete_one(a)
                    self.search.delete_one(a)

                    try:
                        await member.send(
                            embed=embed_generator(
                                description="Бота удалили с вашего сервера или с сервера вашего собеседника. Я вынужен отключить вас.\n",
                                author_name="Конец чата", icon_url=self.bot.user.avatar
                                )
                            )
                    except:
                        pass

                if member is None and memberx is None:
                    a = {"_id": people["_id"]}
                    self.collection.delete_one(a)
                    self.search.delete_one(a)

                    b = {"_id": comp_id}
                    self.collection.delete_one(b)
                    self.search.delete_one(b)

        guilds = await self.bot.fetch_guild(config.config['guild'])
        channel = await guilds.fetch_channel(config.config['channel1'])
        emb = disnake.Embed(
            title=f"Убрали сервер",
            description=f"❌ Бота удалили с сервера **{guild.name}** ({guild.member_count} участников)",
            color=disnake.Color.red(), timestamp=datetime.datetime.now()
            )
        emb.set_thumbnail(guild.icon)
        emb.set_footer(text=f"{guild.name} | {guild.id}", icon_url=guild.icon)
        await channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if config.dev:
            return
        post = {
            '_id': guild.id,
            'channel': 0,
            'chats': 0,
            'messages': 0
            }
        if 0 == self.coll.count_documents({"_id": guild.id}):
            self.coll.insert_one(post)

        channels = guild.text_channels

        async def get_user_who_invited_bot(guild):
            integrations = await guild.integrations()

            bot_integration = next(
                (integration for integration in integrations if isinstance(integration, disnake.BotIntegration)
                 and integration.application.user.name == self.bot.user.name), None
                )

            return bot_integration.user if bot_integration else None

        try:
            user = await get_user_who_invited_bot(guild)
            emb1 = disnake.Embed(
                title="👋 ┃ Спасибо, что добавили бота!",
                description=f"*Привет* {user.mention}, *ты добавил* **AnonChat** *на сервер* **{guild.name}**, *поэтому получил это сообщение. Ознакомься с текстом ниже, чтобы понимать как пользоваться и настраивать бота!*",
                color=disnake.Color.random()
                )
        except:
            user = None
            emb1 = None

        emb = disnake.Embed(
            title="⚙️ ┃ Начальная настройка",
            description=f"> *Привет, я* **AnonChat** *- бот для анонимного общения в лс.*\n"
                        f"> *Чтобы пользоваться мною используйте слэш команды* </start:1238618601393754284> *и* </stop:1180457805069692929>\n\n"
                        f"> *Также для удобного пользования ботом вы можете назначить специальный канал для анонимного чата командой </setup:1180457805069692931>*\n\n"
                        f"> *Вы можете отправить отчёт об ошибке в боте командой* </bug:1180457805069692936> *или зайдти на* **[саппорт сервер](https://discord.gg/YBzKe7vCYY)**\n\n"
                        f"> *Команды для более подробной информации:* </help:1180454759191298141> | </info:1180457805069692930>\n"
                        f"### Важно: бот может искать собеседников как со всех серверов, так и только с вашего, так что вы можете играть в \"угадай кто?\" <:ya_tvoyu_mat_uvagayu:1284104971595284523>\n"
                        f"> *Оставить отзыв боту можно на* **[bots.server](https://bots.server-discord.com/1180439411062734949)** *или на* **[boticord](https://boticord.top/bot/1180439411062734949)**\n",
            color=disnake.Color.random(), timestamp=datetime.datetime.now()
            )
        emb.set_footer(text=f"{guild.name} | {guild.id}", icon_url=guild.icon)
        emb.set_image(file=disnake.File('files/banner.png'))

        try:
            await user.send(embeds=[emb1, emb])
        except:
            for channel in channels:
                try:
                    await channel.send(embed=emb)
                    break
                except:
                    continue

        guilds = await self.bot.fetch_guild(config.config['guild'])
        channel = await guilds.fetch_channel(config.config['channel1'])
        try:
            us, usid = user, user.id
        except:
            us, usid = "неизветно", "неизветно"
        emb = embed_generator(
            description=f"✅ Бот зашёл на сервер **{guild.name}** ({guild.member_count} участников)\nЕго добавил **{us} | {usid}**",
            author_name="Новый сервер", icon_url=self.bot.user.avatar
            )
        emb.set_thumbnail(guild.icon)
        emb.set_footer(text=f"{guild.name} | {guild.id}", icon_url=guild.icon)

        await channel.send(embed=emb)


def setup(bot):
    bot.add_cog(Tasks(bot))
