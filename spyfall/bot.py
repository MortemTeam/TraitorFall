from configparser import ConfigParser
import json

from discord import Member, Embed, Message, RawReactionActionEvent
from discord.ext import tasks
from discord.ext.commands import Bot, Context, CommandNotFound

import terminal
import states
import buttons

from game import Game

config = ConfigParser(allow_no_value=True)
config.read("config.ini")

terminal.info("Initializing...")

bot = Bot(command_prefix=config.get("AUTH", "PREFIX"))


@bot.event
async def on_ready():
    Game.guild = await bot.fetch_guild(config.getint("GUILD", "GUILD_ID"))
    Game.channel = await bot.fetch_channel(config.getint("GUILD", "CHANNEL_ID"))
    Game.admins = [
        await Game.guild.fetch_member(int(x)) for x in filter(lambda x: x, config.get("GUILD", "ADMINS").split(" "))
    ]
    Game.intents = [buttons.JOIN, buttons.LOCATIONS, buttons.RESTART, buttons.START, buttons.CLOSE]

    Game.min_players = config.getint("GAME", "MIN_PLAYERS")
    Game.antagonist = config.get("GAME", "ANTAGONIST")
    with open(config.get("GAME", "LOCATIONS_FILE"), encoding='utf8') as file:
        Game.locations = json.loads(file.read())

    terminal.info("Guild: %s (%s)" % (Game.guild.name, len(Game.guild.members)))
    terminal.info("Channel: %s/%s" % (Game.channel.category, Game.channel.name))
    terminal.info("Admins: %s" % ", ".join("{}#{}".format(x.nick, x.discriminator) for x in Game.admins))
    terminal.successful("Started: %s" % bot.user)


@bot.event
async def on_command_error(ctx: Context, err: CommandNotFound):
    await ctx.reply(embed=Embed(description=err, colour=Game.state))


@bot.group()
async def start(ctx: Context):
    if ctx.channel.id != Game.channel.id:
        return

    if Game.state != states.IDLE:
        return await ctx.reply(embed=Embed(description="Игра уже началась!", colour=Game.state))

    Game.state = states.LOBBY
    message: Message = await ctx.reply(
        embed=Game.get_embed()
    )

    Game.message = message

    for b in Game.intents:
        await message.add_reaction(b)

    close_lobby.start(message)


@bot.event
async def on_raw_reaction_add(payload: RawReactionActionEvent):
    if payload.user_id == bot.user.id or payload.channel_id != Game.channel.id:
        return

    user: Member = await Game.guild.fetch_member(payload.user_id)
    message: Message = await Game.channel.fetch_message(payload.message_id)
    if payload.emoji.name != buttons.JOIN:
        await message.remove_reaction(payload.emoji, user)

    if payload.emoji.name == buttons.LOCATIONS:
        return await user.send(embed=Embed(
            title="Список локаций и ролей:",
            description="\n".join(
                "{}. {}".format(i, x['Location'])  # "\n".join("- {}".format(y) for y in x['Roles'])
                for i, x in enumerate(Game.locations, 1)
            )))

    if payload.emoji.name == buttons.CLOSE and message != Game.message:
        return await message.delete()

    if message == Game.message:
        if payload.emoji.name == buttons.JOIN:
            Game.lobby.append(user)
            return await message.edit(embed=Game.get_embed())

        if payload.emoji.name == buttons.RESTART:
            await Game.channel.send(embed=Embed(description="Таймер перезапущен!", colour=Game.state))
            return close_lobby.restart()

        if payload.emoji.name == buttons.START:
            if Game.can_start():
                await Game.channel.send(embed=Embed(
                    description="Игра начинается, ожидайте раздачи карт!",
                    colour=Game.state,
                ))
                return await Game.start()

            return await Game.channel.send(embed=Embed(
                description="Недостаточно игроков для старта...",
                colour=Game.state,
            ))

        if user in Game.admins:
            if payload.emoji.name == buttons.CLOSE:
                Game.reset()

                await Game.channel.send(embed=Embed(description="Игра принудительно остановлена!", colour=Game.state))
                await message.clear_reactions()
                await message.edit(embed=Game.get_embed())

                close_lobby.false_start = True
                return close_lobby.cancel()


@bot.event
async def on_raw_reaction_remove(payload: RawReactionActionEvent):
    if payload.user_id == bot.user.id or payload.channel_id != Game.channel.id:
        return

    message: Message = await Game.channel.fetch_message(payload.message_id)
    if message == Game.message:
        user: Member = await Game.guild.fetch_member(payload.user_id)

        if payload.emoji.name == buttons.JOIN:
            Game.lobby.remove(user)
            await message.edit(embed=Game.get_embed())
            return


@tasks.loop(seconds=120, count=2)
async def close_lobby(message: Message):
    if close_lobby.false_start:
        close_lobby.false_start = False
        return

    if Game.can_start():
        await Game.channel.send(embed=Embed(description="Игра начинается, ожидайте раздачи карт!", colour=Game.state))
        return await Game.start()

    Game.reset()
    await message.clear_reactions()
    await message.edit(embed=Embed(description="Игроков не набралось...", colour=Game.state))

    close_lobby.false_start = True
    close_lobby.cancel()


close_lobby.false_start = True
bot.run(config.get("AUTH", "TOKEN"))
