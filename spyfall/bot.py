from configparser import ConfigParser

from discord import Message
from discord.ext.commands import Bot

import terminal
import states

config = ConfigParser(allow_no_value=True)
config.read("config.ini")

terminal.info("Initializing...")

bot = Bot(command_prefix=config.get("AUTH", "PREFIX"))


class Game:
    guild = channel = None
    admins = []
    state = states.IDLE


@bot.event
async def on_ready():
    Game.guild = await bot.fetch_guild(config.getint("GUILD", "GUILD_ID"))
    Game.channel = await bot.fetch_channel(config.getint("GUILD", "CHANNEL_ID"))
    Game.admins = [
        await Game.guild.fetch_member(x) for x in filter(lambda x: x, config.get("GUILD", "ADMINS").split(" "))
    ]

    terminal.info("Guild: %s" % Game.guild.name)
    terminal.info("Channel: %s/%s" % (Game.channel.category, Game.channel.name))
    terminal.info("Admins: %s" % ", ".join("{}#{}".format(x.nick, x.discriminator) for x in Game.admins))
    terminal.successful("Started: %s" % bot.user)


@bot.event
async def on_message(message: Message):
    pass

bot.run(config.get("AUTH", "TOKEN"))
