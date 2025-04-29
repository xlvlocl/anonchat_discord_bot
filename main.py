from init import disnake, commands, logger, os, signal, config

intents = disnake.Intents.default()

# noinspection PyDunderSlots,PyUnresolvedReferences
intents.guilds = True
# noinspection PyDunderSlots,PyUnresolvedReferences
intents.members = True
# noinspection PyDunderSlots,PyUnresolvedReferences
intents.dm_messages = True

# noinspection PyTypeChecker

bot = commands.Bot(
    command_prefix=commands.when_mentioned, intents=intents, owner_id=config.config["id"],
    chunk_guilds_at_startup=False
    )


@bot.listen("on_connect")
async def podkluchilsya():
    await bot.wait_until_ready()
    logger.warning("Бот подключен к API!")


@bot.command()
async def reload(ctx, cog: str = None):
    if ctx.author.id == config.config["id"]:
        if cog is None:
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py"):
                    try:
                        bot.reload_extension(f"cogs.{filename[:-3]}")
                    except:
                        pass
            await ctx.send("Все модули перезагружены!", delete_after=5)
        else:
            try:
                bot.reload_extension(f"cogs.{cog}")
                await ctx.send(f"Модуль {cog} перезагружен!", delete_after=5)
            except:
                await ctx.send(f"Модуль {cog} не найден!", delete_after=5)
        try:
            await ctx.message.delete()
        except:
            pass
    else:
        try:
            await ctx.message.delete()
        except:
            pass


@bot.command()
async def ds(ctx):
    if ctx.author.id != config.config["id"]:
        pass
    else:
        try:
            await ctx.message.delete()
        except:
            pass
        await bot.close()
        os.kill(os.getpid(), signal.SIGINT)


@bot.listen("on_ready")
async def zapustilsya():
    await bot.wait_until_ready()
    logger.info(f"{bot.user} запущен!")


bot.remove_command("help")


def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")
            logger.info(f"Загрузил: {filename}")


load_extensions()
if config.dev:
    bot.run(config.config['dev_token'])
else:
    bot.run(config.config['token'])
