from ..init import (search_user, stop, disnake, commands,
                    MongoClient, config, HTTPException, Option, OptionType, embed_generator, post_stats)


class MyView(disnake.ui.StringSelect):
    def __init__(self):
        options = [
            disnake.SelectOption(
                label="Создать новый канал",
                description="Бот создаст канал и установит чат сам",
                emoji='⚙',
                ),
            disnake.SelectOption(
                label="Выбрать имеющийся",
                description="Вы укажите канал для установки",
                emoji='🗳',
                )
            ]

        super().__init__(
            placeholder="Выберите действие",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="select1"
            )

    class MyViewx(disnake.ui.ChannelSelect):
        def __init__(self):
            super().__init__(
                placeholder="Выберите канал",
                channel_types=[disnake.ChannelType.text],
                min_values=1,
                max_values=1,
                custom_id="select2"
                )


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cluster = MongoClient(config.config["database"])
        anon = "AnonChatDev" if config.dev else "AnonChat"
        self.collection = self.cluster[anon].anon
        self.search = self.cluster[anon].search
        self.stats = self.cluster[anon].stats
        self.guild = self.cluster[anon].guilds
        self.economy = self.cluster[anon].economy

    @commands.slash_command(
        name="start", description="Добавляет вас в очередь в анонимный чат", dm_permission=True
        )
    async def start(self, inter):
        try:
            await inter.response.defer(ephemeral=True)
        except:
            pass

        await search_user(inter, self.bot)

    @commands.slash_command(
        name="next", description="Удаляет вас из чата и добавляет в очередь", dm_permission=True
        )
    async def next(self, inter):
        try:
            await inter.response.defer(ephemeral=True)
        except:
            pass
        try:
            findd = self.collection.find_one({'_id': inter.author.id})['comp']
        except:
            findd = 0
        if findd == 0:
            emb = embed_generator(author_name="Вы не состоите в чате", icon_url=self.bot.user.avatar)
            return await inter.send(embed=emb)
        try:
            mode = self.stats.find_one({"_id": inter.author.id})["mode"]
        except:
            mode = 0

        await stop(inter, self.bot, locale=True if mode == 1 else False)
        await search_user(inter, self.bot, frombtn=True, locale=True if mode == 1 else False)

    @commands.slash_command(
        name="stop", description="Удаляет вас из очереди или чата", dm_permission=True
        )
    async def stop(self, inter):
        try:
            await inter.response.defer(ephemeral=True)
        except:
            pass
        await stop(inter, self.bot)

    @commands.slash_command(name="help", description="Список команд и их описание", dm_permission=True)
    async def help(self, inter):
        try:
            await inter.response.defer(ephemeral=True)
        except HTTPException:
            pass
        embed = embed_generator(
            description="Ниже представлен список команд бота. Для вывода информации о команде выберите нужную и нажмите на неё.",
            author_name="Список команд", icon_url=self.bot.user.avatar
            )

        await inter.followup.send(
            embed=embed,
            components=[
                disnake.ui.StringSelect(
                    custom_id="command",
                    options=['start', 'next', 'stop', 'help', 'info', 'setup', 'unsetup', 'profile', 'send profile', 'bug', 'say', 'shop', 'rps', 'promo'],
                    )
                ],
            )

    @commands.slash_command(name="info", description="Информация о боте", dm_permission=True)
    async def info(self, inter):
        try:
            await inter.response.defer(ephemeral=True)
        except HTTPException:
            pass
        ping = self.bot.latency * 1000

        emb = embed_generator(
            description=f"・ *Developer -*  **xlvlocl**\n"
                        f"・ **[Сервер поддержки](https://discord.gg/YBzKe7vCYY)**\n"
                        f"・ *Оставить отзыв* **[тут](https://bots.server-discord.com/1180439411062734949)** *и* **[тут](https://boticord.top/bot/1180439411062734949)**\n\n"
                        f"・ *Пинг -*  **{int(ping)}** *мс*\n"
                        f"・ *Серверов -*  **{len(self.bot.guilds)}**\n"
                        f"・ **[Добавить бота](https://discord.com/oauth2/authorize?client_id=1180439411062734949)**",
            author_name="Информация о боте", icon_url=self.bot.user.avatar
            )
        await inter.send(embed=emb)

    @commands.slash_command(name="setup", description="Установить анон-чат", dm_permission=False)
    @commands.default_member_permissions(administrator=True)
    async def setup(self, inter):
        try:
            await inter.response.defer(ephemeral=True)
        except HTTPException:
            pass
        post = {
            '_id': inter.guild.id,
            'channel': 0,
            'chats': 0,
            'messages': 0
            }
        if 0 == self.guild.count_documents({"_id": inter.guild.id}):
            self.guild.insert_one(post)

        try:
            channel = self.guild.find_one({'_id': inter.guild.id})['channel']
        except:
            channel = 0

        if channel != 0:
            embx = embed_generator(
                description=f"На этом сервере уже установлен анонимный чат!\n"
                            f"Если вы хотите его удалить, то используйте команду </unsetup:1180457805069692933>",
                author_name="Ошибка", icon_url=self.bot.user.avatar
                )
            await inter.send(embed=embx)
        else:
            view = disnake.ui.View()
            view.add_item(MyView())
            await inter.send(view=view)

    @commands.Cog.listener()
    async def on_interaction(self, inter: disnake.MessageInteraction):
        try:
            await inter.response.defer(ephemeral=True)
        except HTTPException:
            pass
        try:
            a = inter.component.custom_id
        except:
            a = None
        if a == "command":

            if inter.values[0] == "start":
                embed = embed_generator(
                    author_name=f"Информация по команде {inter.values[0]}",
                    icon_url=self.bot.user.avatar
                    )
                embed.add_field(
                    name="Описание", value="Добавляет вас в **глобальный** поиск, "
                                           "вы будете ожидать до тех пор, пока любой другой пользователь"
                                           " не решит использовать эту команду.", inline=False
                    )
                embed.add_field(name="Права на использование", value="Есть", inline=True)
                embed.add_field(name="Пример использования", value="</start:1238618601393754284>", inline=True)
                embed.set_image(file=disnake.File('files/start.png'))
                await inter.send(embed=embed, ephemeral=True)

            elif inter.values[0] == "next":
                embed = embed_generator(
                    author_name=f"Информация по команде {inter.values[0]}",
                    icon_url=self.bot.user.avatar
                    )
                embed.add_field(
                    name="Описание", value="Останавливает текущий чат и переключает вас "
                                           "на следующего пользователя в очереди, если он есть, "
                                           "иначе добавляет в поиск.", inline=False
                    )
                embed.add_field(name="Права на использование", value="Есть", inline=True)
                embed.add_field(name="Пример использования", value="</next:1238615248538304583>", inline=True)
                embed.set_image(file=disnake.File('files/next.png'))
                await inter.send(embed=embed, ephemeral=True)

            elif inter.values[0] == "stop":
                embed = embed_generator(
                    author_name=f"Информация по команде {inter.values[0]}",
                    icon_url=self.bot.user.avatar
                    )
                embed.add_field(name="Описание", value="Останавливает текущий чат, если он есть, и удаляет вас из поиска.", inline=False)
                embed.add_field(name="Права на использование", value="Есть", inline=True)
                embed.add_field(name="Пример использования", value="</stop:1180457805069692929>", inline=True)
                embed.set_image(file=disnake.File('files/stop.png'))
                await inter.send(embed=embed, ephemeral=True)

            elif inter.values[0] == "help":
                embed = embed_generator(
                    author_name=f"Информация по команде {inter.values[0]}",
                    icon_url=self.bot.user.avatar
                    )
                embed.add_field(name="Описание", value="Отправляет вам список доступных команд.", inline=False)
                embed.add_field(name="Права на использование", value="Есть", inline=True)
                embed.add_field(name="Пример использования", value="</help:1180454759191298141>", inline=True)
                embed.set_image(file=disnake.File('files/help.png'))
                await inter.send(embed=embed, ephemeral=True)

            elif inter.values[0] == "info":
                embed = embed_generator(
                    author_name=f"Информация по команде {inter.values[0]}",
                    icon_url=self.bot.user.avatar
                    )
                embed.add_field(name="Описание", value="Отправляет вам некоторую информацию о боте.", inline=False)
                embed.add_field(name="Права на использование", value="Есть", inline=True)
                embed.add_field(name="Пример использования", value="</info:1180457805069692930>", inline=True)
                embed.set_image(file=disnake.File('files/info.png'))
                await inter.send(embed=embed, ephemeral=True)

            elif inter.values[0] == "unsetup":
                try:
                    rights = inter.channel.permissions_for(inter.author).administrator
                except:
                    rights = False
                embed = embed_generator(
                    author_name=f"Информация по команде {inter.values[0]}",
                    icon_url=self.bot.user.avatar
                    )
                embed.add_field(
                    name="Описание", value="Удаляет канал с анонимным чатом на сервере или "
                                           "отключает его без удаления канала, если это необходимо.", inline=False
                    )
                embed.add_field(name="Права на использование", value="Есть" if rights else "Нету", inline=True)
                embed.add_field(name="Пример использования", value="</unsetup:1180457805069692933>", inline=True)
                embed.set_image(file=disnake.File('files/unsetup.png'))
                await inter.send(embed=embed, ephemeral=True)

            elif inter.values[0] == "setup":
                try:
                    rights = inter.channel.permissions_for(inter.author).administrator
                except:
                    rights = False
                embed = embed_generator(
                    author_name=f"Информация по команде {inter.values[0]}",
                    icon_url=self.bot.user.avatar
                    )
                embed.add_field(
                    name="Описание", value="Создает канал с анонимным чатом на сервере или отправляет "
                                           "сообщение с панелью управления в указанный канал.", inline=False
                    )
                embed.add_field(name="Права на использование", value="Есть" if rights else "Нету", inline=True)
                embed.add_field(name="Пример использования", value="</setup:1180457805069692931>", inline=True)
                embed.set_image(file=disnake.File('files/setup.png'))
                await inter.send(embed=embed, ephemeral=True)

            elif inter.values[0] == "profile":
                embed = embed_generator(
                    author_name=f"Информация по команде {inter.values[0]}",
                    icon_url=self.bot.user.avatar
                    )
                embed.add_field(name="Описание", value="Отправляет вам ваш профиль или профль другого пользователя, если указан. Также позволяет настроить **свой** профиль.", inline=False)
                embed.add_field(name="Права на использование", value="Есть", inline=True)
                embed.add_field(name="Пример использования", value="</profile:1180457805069692935> `member:`@xlvlocl\n\n</profile:1180457805069692935>", inline=True)
                embed.set_image(file=disnake.File('files/profile.png'))
                await inter.send(embed=embed, ephemeral=True)

            elif inter.values[0] == "send profile":
                embed = embed_generator(
                    author_name=f"Информация по команде {inter.values[0]}",
                    icon_url=self.bot.user.avatar
                    )
                embed.add_field(name="Описание", value="Отправляет ваш профиль собеседнику.", inline=False)
                embed.add_field(name="Права на использование", value="Есть", inline=True)
                embed.add_field(name="Пример использования", value="</send profile:1180457805069692934>", inline=True)
                embed.set_image(file=disnake.File('files/sendprofile.png'))
                await inter.send(embed=embed, ephemeral=True)

            elif inter.values[0] == "bug":
                embed = embed_generator(
                    author_name=f"Информация по команде {inter.values[0]}",
                    icon_url=self.bot.user.avatar
                    )
                embed.add_field(name="Описание", value="Отправляет разработчику ошибку, которую вы нашли", inline=False)
                embed.add_field(name="Права на использование", value="Есть", inline=True)
                embed.add_field(name="Пример использования", value="</bug:1180457805069692936> `проблема:`Какая то проблема `скриншот:`123.png", inline=True)
                embed.set_image(file=disnake.File('files/bug.png'))
                await inter.send(embed=embed, ephemeral=True)

            elif inter.values[0] == "say":
                embed = embed_generator(
                    author_name=f"Информация по команде {inter.values[0]}",
                    icon_url=self.bot.user.avatar
                    )
                embed.add_field(name="Описание", value="Отправляет сообщение с помощью вебхука в текущий канал или указанный, если у пользователя есть права.", inline=False)
                embed.add_field(name="Права на использование", value="Есть", inline=False)
                embed.add_field(name="Пример использования", value="</say:1180457805308760145> `message:`Привет всем `channel:`#₊˚‧🗽₊╎тесты `file:`123.png `new:`True *\n\n*new - создаёт новый вебкух с другим аватаром и ником если True, иначе оставляет тот, что есть.", inline=False)
                embed.set_image(file=disnake.File('files/say.png'))
                await inter.send(embed=embed, ephemeral=True)

            elif inter.values[0] == "shop":
                embed = embed_generator(
                    author_name=f"Информация по команде {inter.values[0]}",
                    icon_url=self.bot.user.avatar
                    )
                embed.add_field(name="Описание", value="Отправляет вам меню покупки / управления виртуальными предметами, валютой и прочими товарами.", inline=False)
                embed.add_field(name="Права на использование", value="Есть", inline=True)
                embed.add_field(name="Пример использования", value="</shop:1213395653510832169>", inline=True)
                embed.set_image(file=disnake.File('files/shop.png'))
                await inter.send(embed=embed, ephemeral=True)

            elif inter.values[0] == "promo":
                embed = embed_generator(
                    author_name=f"Информация по команде {inter.values[0]}",
                    icon_url=self.bot.user.avatar
                    )
                embed.add_field(name="Описание", value="Выдаёт вознаграждение за введение действующего промокода.", inline=False)
                embed.add_field(name="Права на использование", value="Есть", inline=True)
                embed.add_field(name="Пример использования", value="</promo:1297976343539220481> `code:`YrgciixaLLx4CkyO", inline=True)
                embed.set_image(file=disnake.File('files/promo.png'))
                await inter.send(embed=embed, ephemeral=True)
            elif inter.values[0] == "rps":
                embed = embed_generator(
                    author_name=f"Информация по команде {inter.values[0]}",
                    icon_url=self.bot.user.avatar
                    )
                embed.add_field(
                    name="Описание", value="Вызывает собеседника на игру в камень, ножницы, бумагу, при условии, "
                                           "что автор команды и собеседник купили и активировали \"Странный пакетик\" в магазине.",
                    inline=False
                    )
                embed.add_field(name="Права на использование", value="Есть", inline=True)
                embed.add_field(name="Пример использования", value="</rps:1297976343539220480> `предмет:`камень `ставка:`100", inline=True)
                embed.set_image(file=disnake.File('files/rps.png'))
                await inter.send(embed=embed, ephemeral=True)

        if a == "select1":
            if inter.values[0] == "Создать новый канал":
                buttons = disnake.ui.View()
                buttons.add_item(
                    disnake.ui.Button(
                        label='Старт', emoji='<:321:1095340832711770222>',
                        style=disnake.ButtonStyle.gray,
                        custom_id="startV2"
                        )
                    )
                buttons.add_item(
                    disnake.ui.Button(
                        label='Стоп', emoji='<:123:1095340836826394644>',
                        style=disnake.ButtonStyle.gray,
                        custom_id="stopV2"
                        )
                    )
                buttons.add_item(
                    disnake.ui.Button(
                        label='Инфо', emoji='<:456:1095340827896725504>',
                        style=disnake.ButtonStyle.gray,
                        custom_id="infoV2"
                        )
                    )
                buttons.add_item(
                    disnake.ui.Button(
                        label='Режим', emoji='⚙',
                        style=disnake.ButtonStyle.gray,
                        custom_id="mode"
                        )
                    )
                emb1 = embed_generator(
                    title="Совет",
                    description=f"Рекомендую отключить участникам возможность писать в этот канал!\n"
                                f"Это сообщение будет автоматически удалено через 30 секунд",
                    author_name="Совет", icon_url=self.bot.user.avatar
                    )

                emb = embed_generator()
                emb.set_image(file=disnake.File('files/banner.png'))

                embx = embed_generator(
                    description=f"У бота нет права писать в этот канал / создавать канал",
                    author_name="Ошибка", icon_url=self.bot.user.avatar
                    )

                try:
                    channe = await inter.channel.category.create_text_channel("Анонимный чат")
                except:
                    try:
                        channe = await inter.guild.create_text_channel("Анонимный чат")
                    except:
                        await inter.delete_original_message()
                        return await inter.send(embed=embx, ephemeral=True)

                try:
                    await channe.set_permissions(
                        inter.guild.default_role, send_messages=False,
                        add_reactions=False
                        )
                except:
                    try:
                        await channe.send(embed=emb1, delete_after=30)
                    except:
                        await inter.delete_original_message()
                        return await inter.send(embed=embx, ephemeral=True)
                try:
                    await channe.send(embed=emb, view=buttons)
                except:
                    await inter.delete_original_message()
                    return await inter.send(embed=embx, ephemeral=True)

                self.guild.update_one(
                    {"_id": inter.guild.id}, {"$set": {'channel': int(channe.id)}}
                    )
            else:
                view = disnake.ui.View()
                view.add_item(MyView.MyViewx())
                await inter.edit_original_response(view=view)
        elif a == "select2":
            buttons = disnake.ui.View()
            buttons.add_item(
                disnake.ui.Button(
                    label='Старт', emoji='<:321:1095340832711770222>',
                    style=disnake.ButtonStyle.gray,
                    custom_id="startV2"
                    )
                )
            buttons.add_item(
                disnake.ui.Button(
                    label='Стоп', emoji='<:123:1095340836826394644>',
                    style=disnake.ButtonStyle.gray,
                    custom_id="stopV2"
                    )
                )
            buttons.add_item(
                disnake.ui.Button(
                    label='Инфо', emoji='<:456:1095340827896725504>',
                    style=disnake.ButtonStyle.gray,
                    custom_id="infoV2"
                    )
                )
            buttons.add_item(
                disnake.ui.Button(
                    label='Режим', emoji='⚙',
                    style=disnake.ButtonStyle.gray,
                    custom_id="mode"
                    )
                )

            emb = embed_generator()
            emb.set_image(file=disnake.File('files/banner.png'))
            channel = inter.guild.get_channel(int(inter.values[0]))
            try:
                await channel.send(embed=emb, view=buttons)
                try:
                    await channel.set_permissions(
                        inter.guild.default_role, send_messages=False, add_reactions=False
                        )
                except:
                    emb = embed_generator(
                        description=f"Рекомендую отключить участникам возможность писать в этот канал!\n"
                                    f"Это сообщение будет автоматически удалено через 30 секунд",
                        author_name="Совет", icon_url=self.bot.user.avatar
                        )

                    await channel.send(embed=emb, delete_after=30)
            except:
                emb = embed_generator(
                    description=f"У бота нет права писать в этот канал.",
                    author_name="Ошибка", icon_url=self.bot.user.avatar
                    )

                await inter.send(embed=emb, ephemeral=True)
            else:
                self.guild.update_one(
                    {"_id": inter.guild.id}, {"$set": {'channel': int(channel.id)}}
                    )
                embx = embed_generator(
                    description=f"*Анонимный чат установлен в канале* {channel.mention}",
                    author_name="Успешно!", icon_url=self.bot.user.avatar
                    )

                await inter.delete_original_message()
                await inter.send(embed=embx, ephemeral=True)

    @commands.slash_command(name="unsetup", description="Отключить анон-чат", dm_permission=False)
    @commands.default_member_permissions(administrator=True)
    async def unsetup(self, inter):
        try:
            await inter.response.defer(ephemeral=True)
        except:
            pass
        try:
            channel = self.guild.find_one({'_id': inter.guild.id})['channel']
        except:
            embx = embed_generator(
                description=f"Анонимный чат не был включен!",
                author_name="Ошибка", icon_url=self.bot.user.avatar
                )

            return await inter.send(embed=embx)

        # noinspection PyUnusedLocal
        class Buttons(disnake.ui.View):
            def __init__(self, bot=self.bot):
                super().__init__(timeout=30)
                self.bot = bot
                self.cluster = MongoClient(config.config["database"])
                anon = "AnonChatDev" if config.dev else "AnonChat"
                self.guild = self.cluster[anon].guilds

            async def on_timeout(self):
                try:
                    await inter.delete_original_message()
                except:
                    pass

            @disnake.ui.button(label='Подтвердить', emoji='✅', style=disnake.ButtonStyle.gray)
            async def conf(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
                try:
                    await inter.response.defer(ephemeral=True)
                except HTTPException:
                    pass
                self.guild.update_one({"_id": inter.guild.id}, {"$set": {"channel": 0}})
                try:
                    ch = inter.guild.get_channel(int(channel))
                    await ch.delete()
                except:
                    embx = embed_generator(
                        description=f"Анонимный чат отключен, но бот не смог удалить канал.",
                        author_name="Ошибка!", icon_url=self.bot.user.avatar
                        )
                    try:
                        await inter.delete_original_message()
                        await inter.send(embed=embx, ephemeral=True)
                    except:
                        pass
                else:
                    embx = embed_generator(
                        description=f"Анонимный чат отключен.",
                        author_name="Успешно!", icon_url=self.bot.user.avatar
                        )
                    try:
                        await inter.delete_original_message()
                        await inter.send(embed=embx, ephemeral=True)
                    except:
                        pass

            @disnake.ui.button(
                label='Отключить без удаления', emoji='⚠', style=disnake.ButtonStyle.gray
                )
            async def dell(self, button: disnake.ui.Button, inter: disnake.CommandInteraction):
                try:
                    await inter.response.defer(ephemeral=True)
                except HTTPException:
                    pass
                self.guild.update_one({"_id": inter.guild.id}, {"$set": {"channel": 0}})
                ch = inter.guild.get_channel(int(channel))

                embx = embed_generator(
                    description=f"Анонимный чат отключен.",
                    author_name="Успешно!", icon_url=self.bot.user.avatar
                    )

                if ch is not None:
                    try:
                        await ch.purge(limit=None, check=lambda m: m.author == self.bot.user)
                    except:
                        pass
                try:
                    await inter.delete_original_message()
                    await inter.send(embed=embx, ephemeral=True)
                except:
                    pass

        try:
            ch = inter.guild.get_channel(int(channel))
        except:
            ch = None
        if ch is not None:
            embed = embed_generator(
                description=f"*После подтверждения действия бот* **удалит** *канал* **{ch.mention},** *вы уверены?*",
                author_name="Подтвердите ваши намерения", icon_url=self.bot.user.avatar
                )
        else:
            embed = embed_generator(
                description=f"*После подтверждения действия бот* **удалит** *канал с анонимным чатом* *вы уверены?*",
                author_name="Подтвердите ваши намерения", icon_url=self.bot.user.avatar
                )
        await inter.send(embed=embed, view=Buttons())

    @commands.slash_command(
        name='send',
        description="",
        dm_permission=True
        )
    async def sendpr(self, inter):
        pass

    @sendpr.sub_command(
        name='profile',
        description=f'Отправит вашему собеседнику ваш профиль'
        )
    async def sendprofile(self, inter):
        try:
            await inter.response.defer(ephemeral=True)
        except HTTPException:
            pass
        post_stats(id=inter.author.id)
        try:
            comp = self.collection.find_one({'_id': inter.author.id})['comp']
        except:
            comp = 0
        if comp is None or comp == 0:
            emb = embed_generator(
                description="Вы не состоите в анонимном чате.",
                author_name="Ошибка!", icon_url=self.bot.user.avatar
                )
            await inter.send(embed=emb, ephemeral=True)
        else:
            name = self.stats.find_one({'_id': inter.author.id})['name']
            age = self.stats.find_one({'_id': inter.author.id})['age']
            gender = self.stats.find_one({'_id': inter.author.id})['gender']
            aboutme = self.stats.find_one({'_id': inter.author.id})['aboutme']

            emb = embed_generator(
                description=f"Имя **{name}**\n"
                            f"Возраст **{'Не указан' if age == 0 else age}**\n"
                            f"Пол **{gender}**\n\n"
                            f"Обо мне\n`{aboutme}`\n\n"
                            f"*Его ник:* **[{inter.author.name}](https://discordapp.com/users/{inter.author.id}/)**\n"
                            f"*Пинг:* {inter.author.mention}",
                author_name="Ваш собеседник отправил свой профиль", icon_url=self.bot.user.avatar
                )

            emb.set_thumbnail(url=inter.author.avatar)

            member = await self.bot.getch_user(comp)
            if member is None:
                try:
                    guild = self.collection.find_one({'_id': comp})['guild']
                    g = await self.bot.fetch_guild(guild)
                    member = await g.fetch_member(comp)
                except:
                    member = None
            try:
                await member.send(embed=emb)
            except:
                emb = embed_generator(
                    description="Я не смог отправить ваш профиль.",
                    author_name="Ошибка!", icon_url=self.bot.user.avatar
                    )
                await inter.send(embed=emb, ephemeral=True)
            else:
                emb = embed_generator(
                    description="Вы отправили собеседнику свой профиль.",
                    author_name="Успешно!", icon_url=self.bot.user.avatar
                    )
                await inter.send(embed=emb, ephemeral=True)

    @commands.slash_command(
        name="profile",
        description="Показывает профиль указанного пользователя (вас если не указан)",
        dm_permission=True,
        options=[
            Option("member", "Укажите пользователя", OptionType.user, required=False),
            ]
        )
    async def profile(self, inter, member=None):
        try:
            await inter.response.defer(ephemeral=True)
        except HTTPException:
            pass
        if member is None:
            member = inter.author
        post_stats(id=member.id)

        messages = self.stats.find_one({'_id': member.id})['messages']
        chats = self.stats.find_one({'_id': member.id})['chats']
        try:
            rep = self.stats.find_one({'_id': member.id})['rep']
        except:
            rep = 0
        if rep >= 0:
            emoji = "👍"
        else:
            emoji = "👎"

        class MyModal(disnake.ui.Modal):
            def __init__(self):
                # Детали модального окна и его компонентов
                self.cluster = MongoClient(config.config["database"])
                anon = "AnonChatDev" if config.dev else "AnonChat"
                self.stats = self.cluster[anon].stats

                components = [
                    disnake.ui.TextInput(
                        label="Имя",
                        placeholder="Олег",
                        custom_id="name",
                        style=disnake.TextInputStyle.short,
                        max_length=16,
                        min_length=2
                        ),
                    disnake.ui.TextInput(
                        label="Возраст",
                        placeholder="14+",
                        custom_id="age",
                        style=disnake.TextInputStyle.single_line,
                        max_length=2,
                        min_length=2
                        ),
                    disnake.ui.TextInput(
                        label="Пол",
                        placeholder="М/Ж",
                        custom_id="gender",
                        style=disnake.TextInputStyle.single_line,
                        max_length=1,
                        min_length=1
                        ),
                    disnake.ui.TextInput(
                        label="Обо мне",
                        placeholder="Саня, разраб бота, молодец в общем",
                        custom_id="aboutme",
                        style=disnake.TextInputStyle.single_line,
                        max_length=75,
                        min_length=10
                        )
                    ]
                super().__init__(
                    title="Профиль",
                    custom_id="profile",
                    components=components,
                    )

            async def callback(self, interr: disnake.ModalInteraction):
                for key, value in interr.text_values.items():
                    if key.capitalize() == "Name":
                        self.stats.update_one({"_id": member.id}, {"$set": {'name': value}})
                    if key.capitalize() == "Age":
                        try:
                            value = int(value)
                        except:
                            pass
                        else:
                            self.stats.update_one({"_id": member.id}, {"$set": {'age': value}})
                    if key.capitalize() == "Gender":
                        if value.lower() == "м":
                            self.stats.update_one(
                                {"_id": member.id}, {"$set": {'gender': "Мужской"}}
                                )
                        elif value.lower() == "ж":
                            self.stats.update_one(
                                {"_id": member.id}, {"$set": {'gender': "Женский"}}
                                )
                    if key.capitalize() == "Aboutme":
                        self.stats.update_one({"_id": member.id}, {"$set": {'aboutme': value}})

                emb = embed_generator(
                    description="Вы обновили свой профиль",
                    author_name="Успешно!", icon_url=member.avatar
                    )

                name = self.stats.find_one({'_id': member.id})['name']
                age = self.stats.find_one({'_id': member.id})['age']
                gender = self.stats.find_one({'_id': member.id})['gender']
                aboutme = self.stats.find_one({'_id': member.id})['aboutme']

                emb1 = embed_generator(
                    author_name=f"Профиль {member.name}", icon_url=member.avatar
                    )
                emb1.add_field(name="Имя:", value=f"`{name}`", inline=True)
                emb1.add_field(
                    name="Возраст:", value=f"`{'Не указан' if age == 0 else age}`", inline=True
                    )
                emb1.add_field(name="Пол:", value=f"`{gender}`", inline=True)
                emb1.add_field(name="Обо мне:", value=f"`{aboutme}`", inline=False)
                emb1.add_field(name="Был в чатах:", value=f"`{chats}`", inline=True)
                emb1.add_field(name="Написал сообщений:", value=f"`{messages}`", inline=True)
                emb1.add_field(name="Репутация:", value=f"`{rep}`{emoji}", inline=True)

                await inter.edit_original_message(embed=emb1, view=None)
                await interr.followup.send(embed=emb, ephemeral=True)

        # noinspection PyUnusedLocal
        class Buttons(disnake.ui.View):
            def __init__(self):
                super().__init__(timeout=120)

            async def on_timeout(self):
                try:
                    await inter.delete_original_message()
                except:
                    pass

            @disnake.ui.button(emoji="⚙", label="Настроить", style=disnake.ButtonStyle.grey)
            async def previous(self, button, inter):
                await inter.response.send_modal(MyModal())

        name = self.stats.find_one({'_id': member.id})['name']
        age = self.stats.find_one({'_id': member.id})['age']
        gender = self.stats.find_one({'_id': member.id})['gender']
        aboutme = self.stats.find_one({'_id': member.id})['aboutme']

        emb1 = embed_generator(
            author_name=f"Профиль {member.name}", icon_url=member.avatar,
            )
        emb1.add_field(name="Имя:", value=f"`{name}`", inline=True)
        emb1.add_field(name="Возраст:", value=f"`{'Не указан' if age == 0 else age}`", inline=True)
        emb1.add_field(name="Пол:", value=f"`{gender}`", inline=True)
        emb1.add_field(name="Обо мне:", value=f"`{aboutme}`", inline=False)
        emb1.add_field(name="Был в чатах:", value=f"`{chats}`", inline=True)
        emb1.add_field(name="Написал сообщений:", value=f"`{messages}`", inline=True)
        emb1.add_field(name="Репутация:", value=f"`{rep}`{emoji}", inline=True)

        if member == inter.author:
            await inter.send(embed=emb1, view=Buttons())
        else:
            await inter.send(embed=emb1)

    @commands.slash_command(
        name="bug", description="Отправить отчёт об ошибке в боте", dm_permission=True
        )
    async def bug(
            self, inter, text: str = commands.Param(
                name="проблема",
                description="пишите, в чём заключается баг и как он получается",
                min_length=50
                ),
            att: disnake.Attachment = commands.Param(
                name="скриншот",
                description="Покажите реакцию от бота при баге"
                )
            ):
        """Отправляет администрации вашу жалобу"""
        try:
            await inter.response.defer(ephemeral=True)
        except HTTPException:
            pass
        emb1 = embed_generator(
            description=f'{inter.author.mention}, в скором времени разработчик устранит эту ошибку, спасибо за помощь!',
            author_name="Отчёт по ошибке отправлен!", icon_url=self.bot.user.avatar
            )

        await inter.send(embed=emb1)
        emb = embed_generator(
            description=f"**Отправитель:** {inter.author}\n**ID:** {inter.author.id}\n**Подробности:**\n\n`{text}`",
            author_name="Нашли новый баг!", icon_url=self.bot.user.avatar
            )
        emb.set_image(url=att)
        guild = await self.bot.fetch_guild(config.config["guild"])
        channel = await guild.fetch_channel(1180441513700888721)
        await channel.send(content=f"{inter.author.mention}", embed=emb)


def setup(bot):
    bot.add_cog(Slash(bot))
