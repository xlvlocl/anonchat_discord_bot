from ..init import (
    io, random, time, disnake, Image, ImageDraw, Option, OptionType, commands, MongoClient, string, config, embed_generator
    )


class Stuff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cluster = MongoClient(config.config["database"])
        anon = "AnonChatDev" if config.dev else "AnonChat"

        self.collection = self.cluster[anon].anon
        self.stats = self.cluster[anon].stats
        self.guilds = self.cluster[anon].guilds
        self.anon_say = self.cluster[anon].anon_say
        self.economy = self.cluster[anon].economy
        self.promo = self.cluster[anon].promo

    @commands.slash_command(
        name="rps",
        description="Сыграть в камень, ножницы, бумагу",
        dm_permission=True,
        options=[
            Option(
                name="предмет",
                description="Выберите предмет, которым хотите сыграть",
                type=disnake.OptionType.integer,
                choices=[
                    disnake.OptionChoice(name="Камень", value=1),
                    disnake.OptionChoice(name="Ножницы", value=2),
                    disnake.OptionChoice(name="Бумага", value=3)
                    ],
                required=True
                ),
            Option(
                name="ставка",
                description="Выберите ставку",
                type=disnake.OptionType.integer,
                choices=[
                    disnake.OptionChoice(name="Играть на просто так", value=0),
                    disnake.OptionChoice(name="100", value=100),
                    disnake.OptionChoice(name="200", value=200),
                    disnake.OptionChoice(name="300", value=300),
                    disnake.OptionChoice(name="400", value=400),
                    disnake.OptionChoice(name="500", value=500),
                    disnake.OptionChoice(name="600", value=600),
                    disnake.OptionChoice(name="700", value=700),
                    disnake.OptionChoice(name="800", value=800),
                    disnake.OptionChoice(name="900", value=900),
                    disnake.OptionChoice(name="1000", value=1000)
                    ], required=True
                )
            ]
        )
    async def rps(self, inter: disnake.CommandInteraction, предмет: int, ставка: int):
        try:
            await inter.response.defer(ephemeral=True)
        except:
            pass
        if inter.channel.type != disnake.ChannelType.private:
            return await inter.send(
                embed=embed_generator(
                    author_name="Команда доступна только в личных сообщениях бота",
                    icon_url=self.bot.user.avatar
                    ),
                )
        try:
            comp = self.collection.find_one({"_id": inter.author.id})['comp']
        except:
            return await inter.send(
                embed=embed_generator(
                    author_name="Вы не состоите в чате",
                    icon_url=self.bot.user.avatar
                    ),
                )
        a = self.economy.find_one({"_id": inter.author.id})
        c = self.economy.find_one({"_id": comp})
        try:
            if a['in_game'] or c['in_game']:
                return await inter.send(embed=embed_generator(author_name="Вы уже играете", icon_url=self.bot.user.avatar))
        except:
            pass
        try:
            bal = a['balance']
        except:
            bal = 0
        try:
            bal_comp = c['balance']
        except:
            bal_comp = 0
        try:
            access = a['paketik']
        except:
            access = 0
        try:
            access_comp = c['paketik']
        except:
            access_comp = 0

        if access == 0 or access_comp == 0:
            return await inter.send(
                embed=embed_generator(
                    author_name="У вас или у вашего собеседника нету доступа к игре, купите и используйте \"Странный пакетик\" в магазине, чтобы сыграть.",
                    icon_url=self.bot.user.avatar
                    ),
                )

        if bal < ставка or bal_comp < ставка:
            return await inter.send(
                embed=embed_generator(
                    author_name="У вас или у вашего собеседника недостаточно средств для игры",
                    icon_url=self.bot.user.avatar
                    ),
                )

        member = await self.bot.getch_user(comp)
        if member is None:
            try:
                guild = self.collection.find_one({"_id": comp})['guild']
                g = await self.bot.fetch_guild(guild)
                member = await g.fetch_member(comp)
            except:
                member = None
        await inter.delete_original_message()
        abs = f"`{str(ставка)}" + "` <:__:1140642430887137361>" if ставка > 0 else "`на просто так`\n"

        msg = await inter.author.send(
            embed=embed_generator(
                author_name=f"Вы вызвали собеседника на игру в \nкамень, ножницы, бумагу!",
                description=f"**Ставка:** {abs}\n"
                            f"**Предмет собеседника:** `неизвестно`\n\n"
                            f"**Статус:** `собеседник не сделал выбор`",
                icon_url=self.bot.user.avatar
                ),
            )
        item = "камень" if предмет == 1 else "ножницы" if предмет == 2 else "бумагу"
        await msg.reply(embed=embed_generator(author_name=f"Вы выбрали {item}", icon_url=self.bot.user.avatar))

        buttons = disnake.ui.View()
        buttons.add_item(
            disnake.ui.Button(
                label='Принять вызов', emoji='⚔', style=disnake.ButtonStyle.gray,
                custom_id=f"fight {msg.id} {предмет} {inter.author.id} {comp} {ставка}"
                )
            )
        buttons.add_item(
            disnake.ui.Button(
                label='Отказаться от игры', emoji='❌', style=disnake.ButtonStyle.gray,
                custom_id=f"reject {msg.id} {предмет} {inter.author.id} {comp} {ставка}"
                )
            )
        try:
            abs = f"`{str(ставка)}" + "` <:__:1140642430887137361>" if ставка > 0 else "`на просто так`\n"

            await member.send(
                embed=embed_generator(
                    author_name=f"Вас вызвали на игру в \nкамень, ножницы, бумагу!",
                    description=f"**Ставка:** {abs}\n"
                                f"**Предмет собеседника:** `неизвестно`\n\n"
                                f"**Статус:** `вы не сделали выбор`",
                    icon_url=self.bot.user.avatar
                    ), view=buttons
                )
        except:
            return await inter.send(embed=embed_generator(author_name="Невозомжно сыграть в камень, ножницы, бумагу", icon_url=self.bot.user.avatar))

        self.economy.update_one({'_id': comp}, {'$set': {'in_game': True}})
        self.economy.update_one({'_id': inter.author.id}, {'$set': {'in_game': True}})

    @commands.slash_command(
        name="promo",
        description="Активирует промокод",
        dm_permission=True,
        options=[
            Option("code", "код промокода", OptionType.string, required=True)
            ]
        )
    async def promo(self, inter: disnake.CommandInteraction, code):
        try:
            await inter.response.defer(ephemeral=True)
        except:
            pass
        promo = self.promo.find_one({"_id": code})

        if promo is None:
            return await inter.send(
                embed=embed_generator(
                    author_name="Такого промокода не существует",
                    icon_url=self.bot.user.avatar
                    ), ephemeral=True
                )

        if promo['used'] != 0:
            return await inter.send(
                embed=embed_generator(
                    author_name="Промокод уже активирован",
                    icon_url=self.bot.user.avatar
                    ), ephemeral=True
                )

        self.promo.update_one({"_id": code}, {"$set": {"used": inter.author.id}})
        self.economy.update_one({"_id": inter.author.id}, {"$inc": {"balance": int(promo["amount"])}})
        await inter.send(
            embed=embed_generator(
                author_name=f"Промокод успешно активирован",
                description=f"Вы получили `{promo['amount']}`<:__:1140642430887137361>",
                icon_url=self.bot.user.avatar
                ), ephemeral=True
            )

    @commands.slash_command(
        name="generate_promo",
        description="generates promo",
        dm_permission=False,
        guild_ids=[config.config['guild']],
        options=[
            Option("amount", "how much money will user get", OptionType.integer, required=True)
            ]
        )
    @commands.default_member_permissions(administrator=True)
    async def gen_promo(self, inter: disnake.CommandInteraction, amount):
        try:
            await inter.response.defer(ephemeral=True)
        except:
            pass
        if inter.author.id != config.config['id']:
            emb = embed_generator(author_name=f"Только разработчик может использовать данную команду", icon_url=self.bot.user.avatar)
            return await inter.send(embed=emb, ephemeral=True)

        code_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz'
        code = ''
        for i in range(16):
            code += random.choice(code_chars)

        if 0 == self.promo.count_documents({"_id": code}):
            self.promo.insert_one({"_id": code, "amount": amount, "used": 0})
            return await inter.send(f"Промокод успешно сгенерирован - `{code}`", ephemeral=True)
        else:
            return await inter.send(f"Ты сгенерил промо (`{code}`), который уже существует, иди посчитай вероятность", ephemeral=True)

    @commands.slash_command(
        name="unban",
        description="unban member",
        dm_permission=False,
        guild_ids=[config.config['guild']],
        options=[
            Option("member", "enter id of member or select him", OptionType.user, required=True)
            ]
        )
    @commands.default_member_permissions(administrator=True)
    async def unban(self, inter, member):
        try:
            await inter.response.defer(ephemeral=True)
        except:
            pass
        if inter.author.id != config.config['id']:
            emb = embed_generator(author_name=f"Только разработчик может использовать данную команду", icon_url=self.bot.user.avatar)
            return await inter.send(embed=emb, ephemeral=True)

        member = member.id

        check = self.stats.find_one({"_id": member})
        if check is not None and check['banned'] == 1:
            self.stats.update_one({"_id": member}, {"$set": {"banned": 0}})
            self.stats.update_one({"_id": member}, {"$set": {"warns": 0}})
            embed = embed_generator(author_name=f"Пользователь {member} успешно разбанен", icon_url=self.bot.user.avatar)
            await inter.send(embed=embed, ephemeral=True)

            try:
                xx = await self.bot.getch_user(member)
                embd = disnake.Embed(
                    description='Постарайтесь, пожалуйста, не нарушать правила впредь.',
                    color=disnake.Color.green()
                    )
                embd.set_author(name="Вас разбанили", icon_url=self.bot.user.avatar)
                await xx.send(embed=embd)
            except:
                embd = disnake.Embed(
                    description='Постарайтесь, пожалуйста, не нарушать правила впредь.',
                    color=disnake.Color.green()
                    )
                embd.set_author(name="Вас разбанили", icon_url=self.bot.user.avatar)

                await member.send(embd)
        else:
            embed = embed_generator(author_name=f"Пользователь {member} не забанен!", icon_url=self.bot.user.avatar)
            await inter.send(embed=embed, ephemeral=True)

        channel = self.bot.get_guild(config.config['guild']).get_channel(config.config["channel3"])
        em1 = disnake.Embed(
            description=f'{inter.author.mention} разбанил `{member}`',
            color=disnake.Color.red()
            )
        em1.set_author(name="Разбан", icon_url=self.bot.user.avatar)
        await channel.send(embed=em1)

    @commands.slash_command(
        name="total_stats",
        description="admin command",
        dm_permission=False,
        guild_ids=[config.config['guild']],
        )
    @commands.default_member_permissions(administrator=True)
    async def total_stats(self, inter):
        try:
            await inter.response.defer(ephemeral=True)
        except:
            pass
        people = self.guilds.find()
        messages = 0
        chats = 0
        for i in people:
            messages += i['messages']
            chats += i['chats']
        await inter.send(f"Всего сообщений: `{messages}`, чатов: `{chats}`", ephemeral=True)

    @commands.slash_command(
        name="stats", description="Покажет информацию об анонимном чате на этом сервере",
        dm_permission=False
        )
    async def stats(self, inter):
        try:
            await inter.response.defer(ephemeral=True)
        except:
            pass
        guild = inter.guild
        people = self.collection.find()
        num = 0

        try:
            messages = self.guilds.find_one({"_id": guild.id})["messages"]
        except:
            messages = 0

        try:
            chats = self.guilds.find_one({"_id": guild.id})["chats"]
        except:
            chats = 0
        try:
            channel = await inter.guild.fetch_channel(
                self.guilds.find_one({'_id': inter.guild.id})["channel"]
                )
        except:
            channel = None

        for i in people:
            if i["guild"] == guild.id:
                num += 1

        emb = embed_generator(author_name=f"Статистика {guild.name} в анонимном чате", icon_url=guild.icon)
        emb.add_field(name='В анонимном чате:', value=f"`{num}` человек", inline=False)
        emb.add_field(name='Они написали:', value=f"`{messages}` сообщений", inline=False)
        emb.add_field(name='Поменяв при этом', value=f"`{chats}` собеседников", inline=False)
        emb.add_field(
            name='Канал с анонимным чатом',
            value=f'{"Не установлен" if channel is None else channel.mention}', inline=False
            )
        emb.set_footer(
            text=f"{guild.name} ・ Вся статистика пишется только для этого сервера",
            icon_url=guild.icon
            )
        await inter.edit_original_message(embed=emb)

    @commands.slash_command(
        name="say",
        description="Пишет указанный текст в текущий канал или в другой указанный от лица бота",
        dm_permission=False,
        options=[
            Option(
                "message", "Напишите сообщение", OptionType.string, required=True,
                max_length=300
                ),
            Option("channel", "Укажите канал для отправки", OptionType.channel, required=False),
            Option("file", 'Добавить файл', OptionType.attachment, required=False),
            Option("new", "Создать новый профиль", OptionType.boolean, required=False),
            ]
        )
    async def say(
            self, inter: disnake.CommandInteraction, message, channel: disnake.TextChannel = None,
            file: disnake.Attachment = None, new: bool = False
            ):
        try:
            await inter.response.defer(ephemeral=True)
        except:
            pass
        post = {
            "_id": inter.author.id,
            "name": 0,
            "avatar": 0,
            }
        if 0 == self.anon_say.count_documents({"_id": inter.author.id}):
            self.anon_say.insert_one(post)

        def generate(new=False, seed=None):
            width = 400
            height = 400
            pixel_size = 80
            gap_chance = 0.5
            img = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(img)

            colors = [
                (255, 0, 0),
                (0, 255, 0),
                (0, 0, 255),
                (255, 255, 0),
                (255, 0, 255),
                (0, 255, 255)
                ]

            if new:
                date = str(time.time()).replace(".", "")
                random.seed(int(date))
            else:
                date = seed
                random.seed(int(date))

            name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))

            for x in range(0, width, pixel_size):
                for y in range(0, height, pixel_size):
                    if random.random() > gap_chance:
                        color = random.choice(colors)
                        draw.rectangle(
                            ((x, y), (x + pixel_size - 1, y + pixel_size - 1)), fill=color
                            )

            byte_array = io.BytesIO()
            img.save(byte_array, format='PNG')
            ava = byte_array.getvalue()
            byte_array.close()
            return ava, name, date

        channel = channel if channel is not None else inter.channel
        if channel.permissions_for(inter.author).send_messages:
            member = self.anon_say.find_one({'_id': inter.author.id})
            if member['avatar'] == 0 or member['name'] == 0 or new:
                ava, name, date = generate(new=True)
                self.anon_say.update_one(
                    {'_id': inter.author.id}, {'$set': {'avatar': date, 'name': name}}
                    )
            else:
                ava, name = member['avatar'], member['name']
                ava, name, date = generate(new=False, seed=ava)
            if file is None:
                try:
                    webhook = await channel.create_webhook(name=f"anon {name}", avatar=ava)
                    await webhook.send(
                        message, allowed_mentions=disnake.AllowedMentions(
                            roles=False, users=True,
                            everyone=False
                            )
                        )
                    await webhook.delete()
                except:
                    return await inter.edit_original_message(
                        embed=embed_generator(author_name=f"У бота нет прав на создание вебхуков или отправку сообщений, обратитесь к администратору", icon_url=self.bot.user.avatar)
                        )

            else:
                filee = await file.to_file()
                try:
                    webhook = await channel.create_webhook(name=f"anon {name}", avatar=ava)
                    await webhook.send(
                        message, allowed_mentions=disnake.AllowedMentions(
                            roles=False, users=True,
                            everyone=False
                            ), file=filee
                        )
                    await webhook.delete()
                except:
                    return await inter.edit_original_message(
                        embed=embed_generator(author_name=f"У бота нет прав на создание вебхуков или отправку сообщений, обратитесь к администратору", icon_url=self.bot.user.avatar)
                        )
            await inter.edit_original_message(embed=embed_generator(author_name="Успешно отправлено!", icon_url=self.bot.user.avatar))
        else:
            await inter.edit_original_message(
                embed=embed_generator(author_name=f"У вас недостаточно прав чтобы писать в канал {channel.mention}", icon_url=self.bot.user.avatar)
                )

    @commands.slash_command(
        name="shop", description="Показывает магазин с плюшками для анонимного чата",
        dm_permission=True
        )
    async def shop(self, inter: disnake.CommandInteraction):
        try:
            await inter.response.defer(ephemeral=True)
        except:
            pass

        # noinspection PyUnusedLocal
        class CreatePaginator(disnake.ui.View):
            def __init__(self, embedss: list, cls=self):
                super().__init__(timeout=180)
                # self.embeds = embedss
                # self.CurrentEmbed = 0
                # self.last_index = len(self.embeds) - 1
                self.economy = cls.economy

            async def on_timeout(self):
                try:
                    await inter.delete_original_message()
                except:
                    pass

            # @disnake.ui.button(emoji="<a:2_:1067947438607958120>", style=disnake.ButtonStyle.grey)
            # async def previous(self, button, inter):
            #     try:
            #         if self.CurrentEmbed - 1 < 0:
            #             self.CurrentEmbed = self.last_index
            #         else:
            #             self.CurrentEmbed -= 1
            #         await inter.response.edit_message(embed=self.embeds[self.CurrentEmbed])
            #     except:
            #         await inter.send('Не могу щёлкнуть страницу', ephemeral=True)

            @disnake.ui.button(
                label="Купить", emoji="<:__:1047207216261910558>", style=disnake.ButtonStyle.grey
                )
            async def buy(self, button, inter):
                post = {
                    "_id": inter.author.id,
                    "balance": 0,
                    "items": [],
                    "kd": 0
                    }
                if 0 == self.economy.count_documents({"_id": inter.author.id}):
                    self.economy.insert_one(post)

                class MyViewx(disnake.ui.StringSelect):
                    def __init__(self):
                        super().__init__(
                            placeholder="Выберите предмет",
                            options=[
                                disnake.SelectOption(
                                    label="Префикс перед сообщением",
                                    description="Вы сможете настроить его в инвентаре"
                                    ),
                                disnake.SelectOption(
                                    label="Странный пакетик",
                                    description="Необходим для игры в камень, ножницы, бумагу"
                                    ),
                                disnake.SelectOption(
                                    label="Выключатель",
                                    description="Позволяет скрыть свою репутацию в AnonChat. Имеет прочность - 10 использований."
                                    )
                                ],
                            min_values=1,
                            max_values=1,
                            custom_id="buy"
                            )

                view = disnake.ui.View()
                view.add_item(MyViewx())
                await inter.send(view=view, ephemeral=True)

            @disnake.ui.button(
                label="Инвентарь", emoji="<:onlineshopping:1213414924521578577>",
                style=disnake.ButtonStyle.grey
                )
            async def inv(self, button, inter):
                post = {
                    "_id": inter.author.id,
                    "balance": 0,
                    "items": [],
                    "kd": 0
                    }
                if 0 == self.economy.count_documents({"_id": inter.author.id}):
                    self.economy.insert_one(post)

                member = self.economy.find_one({"_id": inter.author.id})
                items = ''
                counter = 1
                for i in member['items']:
                    items += ''.join(f"ㅤㅤ**{counter}.** `{i}`\n")
                    counter += 1
                try:
                    emoji = member['emoji']
                except:
                    emoji = ''

                emb = embed_generator(
                    description=f'**Алмазы:** `{member["balance"]}`<:__:1140642430887137361>\n',
                    author_name=f"Инвентарь {inter.author.name}", icon_url=inter.author.avatar
                    )

                if emoji == '':
                    pass
                elif emoji == 1:
                    emb.add_field(name='Текущий префикс', value="Случайный", inline=False)
                elif emoji == 0:
                    emb.add_field(name='Текущий префикс', value="Скрыт", inline=False)

                try:
                    paketik = member["paketik"]
                except:
                    paketik = 0

                if paketik == 1:
                    emb.description += '**Возможность играть в \nкамень, ножницы, бумагу:** `имеется`\n'
                elif paketik == 0:
                    pass
                emb.description += f'\n**Предметы:**\n\n{items if items != "" else "Нету"}'

                buttons = disnake.ui.View()
                buttons.add_item(
                    disnake.ui.Button(
                        label='Использовать предмет', emoji='⚙', style=disnake.ButtonStyle.gray,
                        custom_id="settings"
                        )
                    )
                if items == '':
                    await inter.send(embed=emb, ephemeral=True)
                else:
                    await inter.send(embed=emb, view=buttons, ephemeral=True)

            # @disnake.ui.button(emoji="<a:1_:1067947382970535998>", style=disnake.ButtonStyle.grey)
            # async def next(self, button, inter):
            #     try:
            #         if self.CurrentEmbed + 1 > self.last_index:
            #             self.CurrentEmbed = 0
            #         else:
            #             self.CurrentEmbed += 1
            #         await inter.response.edit_message(embed=self.embeds[self.CurrentEmbed])
            #     except:
            #         await inter.send('Не могу щёлкнуть страницу', ephemeral=True)

        emb = embed_generator(
            author_name="Магазин", icon_url=self.bot.user.avatar
            )
        emb.add_field(
            name="Префикс перед сообщением", value='**Стоимость** `1000`<:__:1140642430887137361>', inline=False
            )
        emb.add_field(
            name="Странный пакетик", value='**Стоимость** `100`<:__:1140642430887137361>', inline=False
            )
        emb.add_field(
            name="Выключатель", value='**Стоимость** `500`<:__:1140642430887137361>', inline=False
            )
        embedss = [emb]

        await inter.send(embed=embedss[0], view=CreatePaginator(embedss))

    @commands.Cog.listener()
    async def on_interaction(self, inter: disnake.MessageInteraction):
        try:
            await inter.response.defer(ephemeral=True)
        except:
            pass
        try:
            a = inter.component.custom_id
        except:
            return
        if a == "buy":
            post = {
                "_id": inter.author.id,
                "balance": 0,
                "items": [],
                "kd": 0
                }
            if 0 == self.economy.count_documents({"_id": inter.author.id}):
                self.economy.insert_one(post)

            if inter.values[0] == "Префикс перед сообщением":
                member = self.economy.find_one({"_id": inter.author.id})
                await inter.delete_original_message()
                if "Префикс перед сообщением" in member['items']:
                    return await inter.send(embed=embed_generator(author_name=self.bot.user.name, description=f"<a:730143539450871831:748990431458492477> Вы уже купили `{inter.values[0].lower()}`", icon_url=self.bot.user.avatar), ephemeral=True)
                if member["balance"] < 1000:
                    return await inter.send(embed=embed_generator(author_name=self.bot.user.name, description=f"<a:730143539450871831:748990431458492477> У вас недостаточно валюты для покупки!", icon_url=self.bot.user.avatar), ephemeral=True)
                self.economy.update_one({"_id": inter.author.id}, {"$inc": {'balance': -1000}})
                self.economy.update_one(
                    {"_id": inter.author.id}, {"$push": {'items': inter.values[0]}}
                    )
                await inter.send(embed=embed_generator(author_name=self.bot.user.name, description=f"<a:727350151680884826:748990431345246228> Вы купили `{inter.values[0].lower()}`", icon_url=self.bot.user.avatar), ephemeral=True)

            if inter.values[0] == "Странный пакетик":
                member = self.economy.find_one({"_id": inter.author.id})
                await inter.delete_original_message()
                if "Странный пакетик" in member['items']:
                    return await inter.send(embed=embed_generator(author_name=self.bot.user.name, description=f"<a:730143539450871831:748990431458492477> Вы уже купили `{inter.values[0].lower()}`", icon_url=self.bot.user.avatar), ephemeral=True)
                if member["balance"] < 100:
                    return await inter.send(embed=embed_generator(author_name=self.bot.user.name, description=f"<a:730143539450871831:748990431458492477> У вас недостаточно валюты для покупки!", icon_url=self.bot.user.avatar), ephemeral=True)
                self.economy.update_one({"_id": inter.author.id}, {"$inc": {'balance': -100}})
                self.economy.update_one(
                    {"_id": inter.author.id}, {"$push": {'items': inter.values[0]}}
                    )
                await inter.send(embed=embed_generator(author_name=self.bot.user.name, description=f"<a:727350151680884826:748990431345246228> Вы купили `{inter.values[0].lower()}`", icon_url=self.bot.user.avatar), ephemeral=True)

            if inter.values[0] == "Выключатель":
                member = self.economy.find_one({"_id": inter.author.id})
                await inter.delete_original_message()
                if "Выключатель" in member['items']:
                    return await inter.send(embed=embed_generator(author_name=self.bot.user.name, description=f"<a:730143539450871831:748990431458492477> Вы уже купили `{inter.values[0].lower()}`", icon_url=self.bot.user.avatar), ephemeral=True)
                if member["balance"] < 500:
                    return await inter.send(embed=embed_generator(author_name=self.bot.user.name, description=f"<a:730143539450871831:748990431458492477> У вас недостаточно валюты для покупки!", icon_url=self.bot.user.avatar), ephemeral=True)
                self.economy.update_one({"_id": inter.author.id}, {"$inc": {'balance': -500}})
                self.economy.update_one(
                    {"_id": inter.author.id}, {"$push": {'items': inter.values[0]}}
                    )
                await inter.send(embed=embed_generator(author_name=self.bot.user.name, description=f"<a:727350151680884826:748990431345246228> Вы купили `{inter.values[0].lower()}`", icon_url=self.bot.user.avatar), ephemeral=True)

        elif a == 'choice':
            if inter.values[0] == "Префикс перед сообщением":
                await inter.delete_original_message()

                class MyViewx(disnake.ui.StringSelect):
                    def __init__(self):
                        super().__init__(
                            placeholder="Выберите эмодзи",
                            options=[disnake.SelectOption(label=i) for i in [
                                '🔥',
                                '❤',
                                '🗿',
                                '👀',
                                '⚠',
                                '👻',
                                "Случайный префикс",
                                "Убрать префикс"
                                ]],
                            min_values=1,
                            max_values=1,
                            custom_id="ch_emoji"
                            )

                view = disnake.ui.View()
                view.add_item(MyViewx())
                await inter.send(view=view, ephemeral=True)

            elif inter.values[0] == "Странный пакетик":
                await inter.delete_original_message()
                self.economy.update_one({"_id": inter.author.id}, {"$set": {'paketik': 1}})
                lst = self.economy.find_one({"_id": inter.author.id})['items']
                lst.remove("Странный пакетик")
                self.economy.update_one({"_id": inter.author.id}, {"$set": {'items': lst}})
                await inter.send(
                    embed=embed_generator(
                        author_name=f"{inter.author.name}, вы открыли странный пакетик. В нём лежали камень, ножницы и бумага...",
                        description=f"-# Теперь вы **можете** играть в эту игру с собеседником!",
                        icon_url=inter.author.avatar
                        ),
                    ephemeral=True
                    )
            else:
                await inter.send(
                    embed=embed_generator(
                        author_name=f"{inter.author.name}, "
                                    f"этот предмет не может быть использован здесь.",
                        icon_url=inter.author.avatar
                        ),
                    ephemeral=True
                    )

        elif a == 'ch_emoji':
            emoji = inter.values[0]
            await inter.delete_original_message()
            if emoji == "Убрать префикс":
                self.economy.update_one({"_id": inter.author.id}, {"$set": {'emoji': 0}})
                await inter.send(embed=embed_generator(author_name=self.bot.user.name, description=f"<a:727350151680884826:748990431345246228> Вы убрали префикс", icon_url=self.bot.user.avatar), ephemeral=True)
            elif emoji == "Случайный префикс":
                self.economy.update_one({"_id": inter.author.id}, {"$set": {'emoji': 1}})
                await inter.send(embed=embed_generator(author_name=self.bot.user.name, description=f"<a:727350151680884826:748990431345246228> Вы установили случайный префикс. "f"Около каждого вашего сообщения он будет рандомным.", icon_url=self.bot.user.avatar), ephemeral=True)
            else:
                self.economy.update_one({"_id": inter.author.id}, {"$set": {'emoji': emoji}})
                await inter.send(embed=embed_generator(author_name=self.bot.user.name, description=f"<a:727350151680884826:748990431345246228> Вы установили {emoji} в качестве префикса", icon_url=self.bot.user.avatar), ephemeral=True)

        elif a == "RPS":
            values = self.economy.find_one({'_id': inter.author.id})['values']

            await inter.delete_original_message()
            author_message = await inter.channel.fetch_message(values[5])

            def check(m, v):
                if v == "Камень":
                    index = 1
                elif v == "Ножницы":
                    index = 2
                else:
                    index = 3

                    # Проверяем результат
                if index == m:
                    return 0  # ничья
                elif (index == 1 and m == 2) or (index == 2 and m == 3) or (index == 3 and m == 1):
                    return 1  # победа собеседника
                else:
                    return 2  # проигрыш собеседника

            result = check(values[1], inter.values[0])
            if result == 1:
                status = "победа"
                status2 = "поражение"
                color2 = "red"
            elif result == 2:
                status = "поражение"
                status2 = "победа"
                color2 = "green"
            else:
                status = "ничья"
                status2 = "ничья"
                color2 = None

            item = "камень" if values[1] == 1 else "ножницы" if values[1] == 2 else "бумага"
            abs = f"`{str(values[4])}" + "` <:__:1140642430887137361>" if values[4] > 0 else "`на просто так`\n"
            await author_message.edit(

                embed=embed_generator(
                    author_name=f"Вас вызвали на игру в \nкамень, ножницы, бумагу!",
                    description=f"**Ставка:** {abs}\n"
                                f"**Предмет собеседника:** `{item}`\n\n"
                                f"**Статус:** `{status}`",
                    icon_url=self.bot.user.avatar,
                    color="green" if color2 == "red" else "red" if color2 == "green" else None
                    ),
                view=None
                )
            try:
                id_c = self.collection.find_one({'_id': values[2]})['channel']
                channel = await self.bot.fetch_channel(id_c)
            except:
                channel = None
            try:
                message = await channel.fetch_message(values[0])
                abs = f"`{str(values[4])}" + "` <:__:1140642430887137361>" if values[4] > 0 else "`на просто так`\n"

                await message.edit(
                    embed=embed_generator(
                        author_name=f"Вы вызвали собеседника на игру в \nкамень, ножницы, бумагу!",
                        description=f"**Ставка:** {abs}\n"
                                    f"**Предмет собеседника:** `{inter.values[0].lower()}`\n\n"
                                    f"**Статус:** `{status2}`",
                        icon_url=self.bot.user.avatar,
                        color=color2
                        ),
                    )
            except:
                pass
            self.economy.update_one({'_id': values[2]}, {'$unset': {'in_game': ""}})
            self.economy.update_one({'_id': inter.author.id}, {'$unset': {'in_game': ""}})
            self.economy.update_one({'_id': inter.author.id}, {'$unset': {'values': ""}})

            if result == 1:
                self.economy.update_one({'_id': inter.author.id}, {'$inc': {'balance': values[4]}})
                self.economy.update_one({'_id': values[2]}, {'$inc': {'balance': -values[4]}})
            elif result == 2:
                self.economy.update_one({'_id': inter.author.id}, {'$inc': {'balance': -values[4]}})
                self.economy.update_one({'_id': values[2]}, {'$inc': {'balance': values[4]}})


def setup(bot):
    bot.add_cog(Stuff(bot))
