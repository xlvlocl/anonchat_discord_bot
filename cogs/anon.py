from ..init import disnake, commands, MongoClient, config, search_user, stop, post_stats, embed_generator


class Anon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cluster = MongoClient(config.config["database"])
        anon = "AnonChatDev" if config.dev else "AnonChat"
        self.collection = self.cluster[anon].anon
        self.search = self.cluster[anon].search
        self.stats = self.cluster[anon].stats
        self.reports = self.cluster[anon].reports
        self.economy = self.cluster[anon].economy

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "startV2":
            try:
                await inter.response.defer(ephemeral=True)
            except:
                pass
            try:
                mode = self.stats.find_one({"_id": inter.author.id})["mode"]
            except:
                mode = 0

            await search_user(inter, self.bot, frombtn=True, locale=True if mode == 1 else False)

        elif inter.component.custom_id == "stopV2":
            try:
                await inter.response.defer(ephemeral=True)
            except:
                pass
            try:
                mode = self.stats.find_one({"_id": inter.author.id})["mode"]
            except:
                mode = 0

            await stop(inter, self.bot, locale=True if mode == 1 else False)

        elif inter.component.custom_id == "infoV2":
            try:
                await inter.response.defer()
            except:
                pass
            emb = embed_generator(
                title="",
                description="**Правила:** """"\n\n<:to4ka:1213510909922902057> **1)** *Излишняя ненормативная лексика*\n<a:znak:1213510911298379787> Предупреждение\n\n<:to4ka:1213510909922902057> **2)** *Оскорбительное поведение в отношении собеседника*\n<a:znak:1213510911298379787> Предупреждение\n\n<:to4ka:1213510909922902057> **3)** *Фишинг, попрошайничество, мошенничество в любых проявлениях*\n<a:znak:1213510911298379787> Бан\n\n<:to4ka:1213510909922902057> **4)** *Подстрекательство на совершение противоправных действий как в рамках платформы Discord так и реальной жизни*\n<a:znak:1213510911298379787> Бан\n\n<:to4ka:1213510909922902057> **5)** *Несогласованный пиар/реклама*\n<a:znak:1213510911298379787> Бан\n\n<:to4ka:1213510909922902057> **6)** *Пропаганда чего бы то ни было, будь то идеология, запрещённые вещества и т.д.*\n<a:znak:1213510911298379787> Бан\n\n<:to4ka:1213510909922902057> **7)** *Отправлять шокирующий контент, контент, содержащий яркие вспышки, 
                сцены откровенного и/или завуалированного сексуального характера, сцены насилия БЕЗ СОГЛАСИЯ СОБЕСЕДНИКА*\n<a:znak:1213510911298379787> Бан\n\n<:to4ka:1213510909922902057> **8)** *Дискриминация по гендерному, расовому, религиозному или любому другому признаку*\n<a:znak:1213510911298379787> Бан""""\n\n"
                            "\nЕсли есть вопросы/предложения заходи на [саппорт сервер](https://discord.gg/YBzKe7vCYY)\n\n"
                            "> 😈 Основной игровой сервер: [Suck Or Play](https://discord.gg/abnRQzebdF)",
                author_name="Справка по анонимному чату", icon_url=self.bot.user.avatar
                )

            await inter.send(embed=emb, ephemeral=True)

        elif inter.component.custom_id == "mode":
            # 0 - global search
            # 1 - local search
            # 2 - group search

            post_stats(id=inter.author.id)

            try:
                mode = self.stats.find_one({"_id": inter.author.id})["mode"]
            except:
                mode = 0
            mode_str = "Глобальный" if mode == 0 else "Локальный" if mode == 1 else "Групповой"
            emb = embed_generator(
                description=f"**Текущий режим**: `{mode_str}`\n\n"
                            "**Глобальный поиск** - бот будет искать собеседника с **любого сервера**\n"
                            "**Локальный поиск** - бот будет искать собеседника с **текущего сервера**\n"
                            "**Групповой поиск** - в разработке. \n\n"
                            "Идею по реализации можно предложить на [саппорт сервере](https://discord.gg/YBzKe7vCYY)\n",
                author_name="Выбор режима | БЕТА", icon_url=self.bot.user.avatar
                )

            buttons = disnake.ui.View()

            buttons.add_item(disnake.ui.Button(label="Глобальный", custom_id="global_search", style=disnake.ButtonStyle.gray))
            buttons.add_item(disnake.ui.Button(label="Локальный", custom_id="local_search", style=disnake.ButtonStyle.gray))
            buttons.add_item(disnake.ui.Button(label="Групповой", custom_id="group_search", style=disnake.ButtonStyle.gray, disabled=True))

            await inter.send(embed=emb, view=buttons, ephemeral=True)

        elif inter.component.custom_id in ["global_search", "local_search", "group_search"]:
            try:
                await inter.response.defer()
            except:
                pass

            post_stats(id=inter.author.id)

            try:
                mode = self.stats.find_one({"_id": inter.author.id})["mode"]
            except:
                mode = 0

            if inter.component.custom_id == "global_search":
                if mode == 0:
                    emb = embed_generator(author_name="У вас уже установлен этот режим!", icon_url=self.bot.user.avatar)
                    return await inter.send(embed=emb, ephemeral=True)
                self.stats.update_one({"_id": inter.author.id}, {"$set": {"mode": 0}})
                mode = 0
            elif inter.component.custom_id == "local_search":
                if mode == 1:
                    emb = embed_generator(author_name="У вас уже установлен этот режим!", icon_url=self.bot.user.avatar)
                    return await inter.send(embed=emb, ephemeral=True)
                self.stats.update_one({"_id": inter.author.id}, {"$set": {"mode": 1}})
                mode = 1
            elif inter.component.custom_id == "group_search":
                if mode == 2:
                    emb = embed_generator(author_name="У вас уже установлен этот режим!", icon_url=self.bot.user.avatar)
                    return await inter.send(embed=emb, ephemeral=True)
                self.stats.update_one({"_id": inter.author.id}, {"$set": {"mode": 2}})
                mode = 2
            mode_str = "Глобальный" if mode == 0 else "Локальный" if mode == 1 else "Групповой"
            emb = embed_generator(
                description=f"**Текущий режим**: `{mode_str}`\n\n"
                            "**Глобальный поиск** - бот будет искать собеседника с **любого сервера**\n"
                            "**Локальный поиск** - бот будет искать собеседника с **текущего сервера**\n"
                            "**Групповой поиск** - в разработке. \n\n"
                            "Идею по реализации можно предложить на [саппорт сервере](https://discord.gg/YBzKe7vCYY)\n",
                author_name="Выбор режима | БЕТА", icon_url=self.bot.user.avatar
                )

            buttons = disnake.ui.View()

            buttons.add_item(disnake.ui.Button(label="Глобальный", custom_id="global_search", style=disnake.ButtonStyle.gray))
            buttons.add_item(disnake.ui.Button(label="Локальный", custom_id="local_search", style=disnake.ButtonStyle.gray))
            buttons.add_item(disnake.ui.Button(label="Групповой", custom_id="group_search", style=disnake.ButtonStyle.gray, disabled=True))

            await inter.edit_original_message(embed=emb, view=buttons)

        elif inter.component.custom_id == "like":
            try:
                await inter.response.defer()
            except:
                pass
            try:
                last_comp = self.stats.find_one({'_id': inter.author.id})['last_comp']
            except:
                pass
            else:
                buttons = disnake.ui.View()
                buttons.add_item(
                    disnake.ui.Button(
                        label='', emoji='👍', style=disnake.ButtonStyle.gray, custom_id="like",
                        disabled=True
                        )
                    )
                buttons.add_item(
                    disnake.ui.Button(
                        label='', emoji='👎', style=disnake.ButtonStyle.gray, custom_id="dlike",
                        disabled=True
                        )
                    )
                buttons.add_item(
                    disnake.ui.Button(
                        label='', emoji='⚠', style=disnake.ButtonStyle.gray, custom_id="report"
                        )
                    )
                try:
                    likes = self.stats.find_one({'_id': last_comp})['rep']
                    self.stats.update_one({"_id": last_comp}, {"$set": {'rep': likes + 1}})
                except:
                    pass
                emb = embed_generator(
                    description=f"Вы поставили собеседнику лайк.",
                    author_name="Лайк!", icon_url=self.bot.user.avatar
                    )
                await inter.edit_original_response(view=buttons)
                await inter.send(embed=emb)

        elif inter.component.custom_id == "dlike":
            try:
                await inter.response.defer()
            except:
                pass
            try:
                last_comp = self.stats.find_one({'_id': inter.author.id})['last_comp']
            except:
                pass
            else:
                buttons = disnake.ui.View()
                buttons.add_item(
                    disnake.ui.Button(
                        label='', emoji='👍', style=disnake.ButtonStyle.gray, custom_id="like",
                        disabled=True
                        )
                    )
                buttons.add_item(
                    disnake.ui.Button(
                        label='', emoji='👎', style=disnake.ButtonStyle.gray, custom_id="dlike",
                        disabled=True
                        )
                    )
                buttons.add_item(
                    disnake.ui.Button(
                        label='', emoji='⚠', style=disnake.ButtonStyle.gray, custom_id="report"
                        )
                    )
                try:
                    likes = self.stats.find_one({'_id': last_comp})['rep']
                    self.stats.update_one({"_id": last_comp}, {"$set": {'rep': likes - 1}})
                except:
                    pass
                emb = embed_generator(
                    description=f"Вы поставили собеседнику дизлайк.",
                    author_name="Дизлайк!", icon_url=self.bot.user.avatar
                    )
                await inter.edit_original_response(view=buttons)
                await inter.send(embed=emb)
        elif inter.component.custom_id == "report":
            bot = self.bot
            id = self.stats.find_one({'_id': inter.author.id})['last_comp']
            num = self.reports.find_one({'_id': "super"})['num']

            class MyModal(disnake.ui.Modal):
                def __init__(self):
                    # Детали модального окна и его компонентов
                    self.bot = bot
                    self.cluster = MongoClient(config.config["database"])
                    anon = "AnonChatDev" if config.dev else "AnonChat"
                    self.reports = self.cluster[anon].reports

                    components = [
                        disnake.ui.TextInput(
                            label="Причина жалобы",
                            placeholder="Оскорбления в мой адрес",
                            custom_id="Причина",
                            style=disnake.TextInputStyle.short,
                            max_length=250,
                            min_length=20
                            ),
                        disnake.ui.TextInput(
                            label="Ссылка на скрин с доказательством",
                            placeholder="https://...",
                            custom_id="Пруф",
                            style=disnake.TextInputStyle.short,
                            max_length=250,
                            min_length=10
                            )
                        ]
                    super().__init__(
                        title="Жалоба",
                        custom_id="create_tag",
                        components=components,
                        )

                async def callback(self, interr: disnake.ModalInteraction):
                    desc = ''
                    link = ''
                    for key, value in interr.text_values.items():
                        if key.capitalize() == "Пруф":
                            link = value
                        else:
                            desc += ''.join(f'\n `{key.capitalize()}`: {value}')

                    emb = embed_generator(
                        description=f"Вы пожаловались на вашего собеседника, результат обработки жалобы придёт вам здесь.",
                        author_name=f"Жалоба #{num + 1}", icon_url=self.bot.user.avatar
                        )

                    await interr.send(embed=emb)

                    try:
                        embed = disnake.Embed(
                            description=desc,
                            color=disnake.Color.orange(),
                            )
                        embed.set_footer(
                            text=f"Отправитель: {interr.author} | {interr.author.id}",
                            icon_url=interr.author.avatar
                            )
                        embed.set_author(name=f"Жалоба #{num + 1}", icon_url=self.bot.user.avatar)
                        embed.set_image(link)
                        buttons = disnake.ui.View()
                        buttons.add_item(
                            disnake.ui.Button(
                                label='Предупредить', style=disnake.ButtonStyle.gray,
                                custom_id=f"warn,{id},{interr.author.id},{num + 1}"
                                )
                            )
                        buttons.add_item(
                            disnake.ui.Button(
                                label='Забанить', style=disnake.ButtonStyle.gray,
                                custom_id=f"ban,{id},{interr.author.id},{num + 1}"
                                )
                            )
                        buttons.add_item(
                            disnake.ui.Button(
                                label='Понять и простить', style=disnake.ButtonStyle.gray,
                                custom_id=f"dismiss,{id},{interr.author.id},{num + 1}"
                                )
                            )

                        msg = await (self.bot.get_guild(config.config["guild"]).get_channel(
                            config.config["channel3"]
                            ).
                                     send(embed=embed, view=buttons))
                    except:
                        embedd = disnake.Embed(
                            description=desc,
                            color=disnake.Color.orange(),
                            )
                        embedd.set_author(name=f"Жалоба #{num + 1}", icon_url=self.bot.user.avatar)
                        embedd.set_footer(
                            text=f"Отправитель: {interr.author} | {interr.author.id}",
                            icon_url=interr.author.avatar
                            )
                        buttons = disnake.ui.View()
                        buttons.add_item(
                            disnake.ui.Button(
                                label='Предупредить', style=disnake.ButtonStyle.gray,
                                custom_id=f"warn,{id},{interr.author.id},{num + 1}"
                                )
                            )
                        buttons.add_item(
                            disnake.ui.Button(
                                label='Забанить', style=disnake.ButtonStyle.gray,
                                custom_id=f"ban,{id},{interr.author.id},{num + 1}"
                                )
                            )
                        buttons.add_item(
                            disnake.ui.Button(
                                label='Понять и простить', style=disnake.ButtonStyle.gray,
                                custom_id=f"dismiss,{id},{interr.author.id},{num + 1}"
                                )
                            )
                        msg = await self.bot.get_guild(config.config["guild"]).get_channel(config.config["channel3"]).send(embed=embedd, view=buttons)
                    self.reports.update_one({"_id": "super"}, {"$set": {'num': num + 1}})

                    buttons = disnake.ui.View()
                    buttons.add_item(
                        disnake.ui.Button(
                            label='', emoji='👍', style=disnake.ButtonStyle.gray, custom_id="like",
                            disabled=True
                            )
                        )
                    buttons.add_item(
                        disnake.ui.Button(
                            label='', emoji='👎', style=disnake.ButtonStyle.gray, custom_id="dlike",
                            disabled=True
                            )
                        )
                    buttons.add_item(
                        disnake.ui.Button(
                            label='', emoji='⚠', style=disnake.ButtonStyle.gray, custom_id="report",
                            disabled=True
                            )
                        )

                    await inter.edit_original_response(view=buttons)
                    post = {
                        "_id": num + 1,
                        "reason": desc,
                        'msg_id': msg.id
                        }
                    self.reports.insert_one(post)

            await inter.response.send_modal(MyModal())
        elif inter.component.custom_id == "settings":
            try:
                await inter.response.defer()
            except:
                pass

            class MyViewx(disnake.ui.StringSelect):
                def __init__(self):
                    self.cluster = MongoClient(config.config["database"])
                    anon = "AnonChatDev" if config.dev else "AnonChat"
                    self.eco = self.cluster[anon].economy
                    mem = self.eco.find_one({"_id": inter.author.id})
                    super().__init__(
                        placeholder="Выберите предмет",
                        options=[disnake.SelectOption(label=i) for i in mem['items']],
                        min_values=1,
                        max_values=1,
                        custom_id="choice"
                        )

            view = disnake.ui.View()
            view.add_item(MyViewx())
            await inter.send(view=view, ephemeral=True)
        elif inter.component.custom_id == "block":
            try:
                await inter.response.defer()
            except:
                pass
            self.stats.update_one({"_id": inter.author.id}, {"$set": {"block": 1}})
            buttons = disnake.ui.View()
            buttons.add_item(
                disnake.ui.Button(
                    label='Включить префиксы', emoji="<:emoji_39:963680447609573396>",
                    style=disnake.ButtonStyle.gray, custom_id=f"unblock"
                    )
                )
            await inter.edit_original_message(view=buttons)
        elif inter.component.custom_id == "unblock":
            try:
                await inter.response.defer()
            except:
                pass
            self.stats.update_one({"_id": inter.author.id}, {"$set": {"block": 0}})
            buttons = disnake.ui.View()
            buttons.add_item(
                disnake.ui.Button(
                    label='Отключить префиксы', emoji="<:emoji_38:963679797991575572>",
                    style=disnake.ButtonStyle.gray, custom_id=f"block"
                    )
                )
            await inter.edit_original_message(view=buttons)
        elif inter.component.custom_id in ['start', 'stop', 'info']:
            try:
                await inter.response.defer()
            except:
                pass
            embed = embed_generator(
                description="В связи с недавним обновлением вам необходимо переустановить анонимный чат. Пожалуйста, восползуйтесь командой "
                            "</unsetup:1180457805069692933>, а затем </setup:1180457805069692931> или обратитесь к администрации сервера",
                author_name="Обновление", icon_url=self.bot.user.avatar
                )
            await inter.send(embed=embed, ephemeral=True)
        elif inter.component.custom_id.startswith("fight") or inter.component.custom_id.startswith("reject"):
            try:
                x = inter.component.custom_id.split(" ")
                status = x[0]
                msg_id = int(x[1])
                choice = int(x[2])
                authorr = int(x[3])
                comp = int(x[4])
                bet = int(x[5])
            except:
                return
            if status == "reject":
                author = await self.bot.getch_user(authorr)
                if author is None:
                    try:
                        guild = self.collection.find_one({"_id": authorr})["guild"]
                        g = await self.bot.fetch_guild(guild)
                        author = await g.fetch_member(authorr)
                    except:
                        author = None
                abs = f"`{str(bet)}" + "` <:__:1140642430887137361>" if bet > 0 else "`на просто так`\n"
                await inter.edit_original_message(
                    embed=embed_generator(
                        author_name=f"Вас вызвали на игру в \nкамень ножницы бумагу!",
                        description=f"**Ставка:** {abs}\n"
                                    f"**Статус:** `вы отклонили вызов на игру`",
                        icon_url=self.bot.user.avatar
                        ),
                    view=None
                    )
                if author is not None:
                    try:
                        id_c = self.collection.find_one({'_id': authorr})['channel']
                        channel = await self.bot.fetch_channel(id_c)
                    except:
                        channel = None
                    try:
                        message = await channel.fetch_message(msg_id)
                        abs = f"`{str(bet)}" + "` <:__:1140642430887137361>" if bet > 0 else "`на просто так`\n"
                        await message.edit(
                            embed=embed_generator(
                                author_name=f"Вы вызвали собеседника на игру в \nкамень ножницы бумагу!",
                                description=f"**Ставка:** {abs}\n"
                                            f"**Статус:** `собеседник отклонил вызов на игру`",
                                icon_url=self.bot.user.avatar
                                )
                            )
                    except:
                        pass
                self.economy.update_one({'_id': authorr}, {'$unset': {'in_game': ""}})
                self.economy.update_one({'_id': inter.author.id}, {'$unset': {'in_game': ""}})

            else:
                self.economy.update_one({'_id': inter.author.id}, {'$set': {'values': [msg_id, choice, authorr, comp, bet, inter.message.id]}})

                class MyViewx(disnake.ui.StringSelect):
                    def __init__(self):
                        super().__init__(
                            placeholder="Выберите предмет",
                            options=[
                                disnake.SelectOption(
                                    label="Камень",
                                    ),
                                disnake.SelectOption(
                                    label="Ножницы",
                                    ),
                                disnake.SelectOption(
                                    label="Бумага",
                                    )
                                ],
                            min_values=1,
                            max_values=1,
                            custom_id="RPS"
                            )

                view = disnake.ui.View()
                view.add_item(MyViewx())
                await inter.send(view=view, ephemeral=True)
        else:
            try:
                x = inter.component.custom_id.split(",")
                verdict = x[0]
                podsuidmiy = int(x[1])
                istec = int(x[2])
                number_of_report = int(x[3])
            except:
                return

            podsuidmiy_member = await self.bot.getch_user(podsuidmiy)
            istec_member = await self.bot.getch_user(istec)

            if verdict == "warn":
                self.stats.update_one({"_id": podsuidmiy}, {"$inc": {"warns": 1}})
                warns = self.stats.find_one({"_id": podsuidmiy})['warns']
                reason = self.reports.find_one({"_id": number_of_report})['reason']
                msg_id = self.reports.find_one({"_id": number_of_report})['msg_id']
                if warns == 5:
                    self.stats.update_one({"_id": podsuidmiy}, {"$set": {"banned": 1}})
                    embed = disnake.Embed(
                        description="Вы были заблокированны из-за большого количества жалоб в вашу сторону.\n"
                                    "Если вы хотите обжаловать блокировку, обратитесь за помощью на [сервер поддержки](https://discord.gg/YBzKe7vCYY) **AnonChat** бота.",
                        color=disnake.Color.red()
                        )
                    embed.set_author(name="Блокировка AnonChat", icon_url=self.bot.user.avatar)
                    await podsuidmiy_member.send(embed=embed)

                    try:
                        comp = self.collection.find_one({'_id': podsuidmiy})['comp']
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
                        lol = {"_id": podsuidmiy}
                        self.collection.delete_one(lol)
                        self.search.delete_one(lol)

                        lol = {"_id": comp}
                        self.collection.delete_one(lol)
                        self.search.delete_one(lol)

                        emb = embed_generator(
                            description="Ваш собеседник получил блокировку в **AnonChat**",
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
                            m1 = await podsuidmiy_member.send(embed=emb1)
                            self.stats.update_one(
                                {"_id": podsuidmiy_member.id}, {"$set": {'stop_m': m1.id}}
                                )
                        except:
                            pass

                    await istec_member.send(
                        embed=embed_generator(
                            description=f"*Вы отправили жалобу* **#{number_of_report}**.\n**{reason}**\n*Вердикт: пользователь был заблокирован и больше не сможет общаться в* **AnonChat**.\n\n**Спасибо за то, что поддерживаете хорошую атмосферу в AnonChat!**",
                            author_name="Результат по отправленной жалобе", icon_url=self.bot.user.avatar
                            )
                        )

                else:
                    await podsuidmiy_member.send(
                        embed=embed_generator(
                            description=f"Вам было выдано предупреждение за нарушение правил.\n{reason}"
                                        "\n\nЕсли вы хотите обжаловать предупреждение, обратитесь за помощью на [сервер поддержки](https://discord.gg/YBzKe7vCYY) **AnonChat** бота.",
                            author_name=f"Вы получили {warns} предупреждение", icon_url=self.bot.user.avatar
                            )
                        )
                    await istec_member.send(
                        embed=embed_generator(
                            description=f"*Вы отправили жалобу* **#{number_of_report}**.\n**{reason}**\n*Вердикт: пользователь получил предупреждение*\n\n**Спасибо за то, что поддерживаете хорошую атмосферу в AnonChat!**",
                            author_name="Результат по отправленной жалобе", icon_url=self.bot.user.avatar
                            )
                        )
                await inter.edit_original_response(view=None)
                channel = self.bot.get_guild(config.config['guild']).get_channel(config.config["channel3"])
                msg = await channel.fetch_message(msg_id)

                await msg.reply(
                    embed=embed_generator(
                        description=f'{inter.author.mention} обработал заявку.\n*Вердикт:* **{podsuidmiy} / {podsuidmiy_member}** `{"предупреждён" if warns + 1 <= 5 else "заблокирован"}`\n\n*Отправитель жалобы:* **{istec} / {istec_member}**',
                        author_name="Вердикт по жалобе", icon_url=self.bot.user.avatar
                        )
                    )
            elif verdict == "ban":
                self.stats.update_one({"_id": podsuidmiy}, {"$set": {"banned": 1}})
                reason = self.reports.find_one({"_id": number_of_report})['reason']
                msg_id = self.reports.find_one({"_id": number_of_report})['msg_id']
                embed = disnake.Embed(
                    description="Вы были заблокированны из-за большого количества жалоб в вашу сторону.\n"
                                "Если вы хотите обжаловать блокировку, обратитесь за помощью на [сервер поддержки](https://discord.gg/YBzKe7vCYY) **AnonChat** бота.",
                    color=disnake.Color.red()
                    )
                embed.set_author(name="Блокировка AnonChat", icon_url=self.bot.user.avatar)
                await podsuidmiy_member.send(embed=embed)
                try:
                    comp = self.collection.find_one({'_id': podsuidmiy})['comp']
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
                    lol = {"_id": podsuidmiy}
                    self.collection.delete_one(lol)
                    self.search.delete_one(lol)

                    lol = {"_id": comp}
                    self.collection.delete_one(lol)
                    self.search.delete_one(lol)

                    try:
                        emb = embed_generator(
                            description="Ваш собеседник получил блокировку в **AnonChat**",
                            author_name='Конец чата', icon_url=self.bot.user.avatar
                            )

                        m = await member.send(embed=emb)
                        self.stats.update_one({"_id": member.id}, {"$set": {'stop_m': m.id}})
                    except:
                        pass
                    try:
                        emb1 = embed_generator(
                            description="Чат остановлен, так как вы заблокированы\n",
                            author_name='Конец чата', icon_url=self.bot.user.avatar
                            )
                        emb1.set_footer(
                            text=f"{podsuidmiy_member.name}", icon_url=podsuidmiy_member.avatar
                            )

                        m1 = await podsuidmiy_member.send(embed=emb1)
                        self.stats.update_one(
                            {"_id": podsuidmiy_member.id}, {"$set": {'stop_m': m1.id}}
                            )
                    except:
                        pass

                await istec_member.send(
                    embed=embed_generator(
                        description=f"*Вы отправили жалобу* **#{number_of_report}**.\n**{reason}**\n*Вердикт: пользователь был заблокирован и больше не сможет общаться в* **AnonChat**.\n\n**Спасибо за то, что поддерживаете хорошую атмосферу в AnonChat!**",
                        author_name="Результат по отправленной жалобе", icon_url=self.bot.user.avatar
                        )
                    )

                await inter.edit_original_response(view=None)
                channel = self.bot.get_guild(config.config['guild']).get_channel(config.config["channel3"])
                msg = await channel.fetch_message(msg_id)
                await msg.reply(
                    embed=embed_generator(
                        description=f'{inter.author.mention} обработал заявку.\n*Вердикт:* **{podsuidmiy} / {podsuidmiy_member}** `{"предупреждён" if verdict == "warn" else "заблокирован" if verdict == "ban" else "прощён"}`\n\n*Отправитель жалобы:* **{istec} / {istec_member}**',
                        author_name="Вердикт по жалобе", icon_url=self.bot.user.avatar
                        )
                    )
            else:
                reason = self.reports.find_one({"_id": number_of_report})['reason']
                msg_id = self.reports.find_one({"_id": number_of_report})['msg_id']

                await istec_member.send(
                    embed=embed_generator(
                        description=f"*Вы отправили жалобу* **#{number_of_report}**.\n**{reason}**\n*Вердикт: мы не нашли нарушений.*\n\n**Спасибо за то, что поддерживаете хорошую атмосферу в AnonChat!**",
                        author_name="Результат по отправленной жалобе", icon_url=self.bot.user.avatar
                        )
                    )

                await inter.edit_original_response(view=None)
                channel = self.bot.get_guild(config.config['guild']).get_channel(config.config["channel3"])
                msg = await channel.fetch_message(msg_id)
                await msg.reply(
                    embed=embed_generator(
                        description=f'{inter.author.mention} обработал заявку.\n*Вердикт:* **{podsuidmiy} / {podsuidmiy_member}** `{"предупреждён" if verdict == "warn" else "заблокирован" if verdict == "ban" else "прощён"}`\n\n*Отправитель жалобы:* **{istec} / {istec_member}**',
                        author_name="Вердикт по жалобе", icon_url=self.bot.user.avatar
                        )
                    )


def setup(bot):
    bot.add_cog(Anon(bot))
