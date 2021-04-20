import discord
from discord.ext import commands
from discord.ext.commands import Bot

import game
import config

import asyncio
import json

bot_token = config.TOKEN
bot_trigger = config.PREFIX

bot = Bot(command_prefix=bot_trigger)
game = game.Game(bot)

@bot.event
async def on_ready():
    print("Bot User-Name: %s" % bot.user)
    print("Bot User-ID: %s" % bot.user.id)
    print("--------------------")
    
    game.channel = await bot.fetch_channel(config.GAME_CHANNEL)
    game.guild   = await bot.fetch_guild(config.GAME_GUILD)    

@bot.event
async def on_message(message):
    def check_trigger(arg=''):
        return message.content.lower().startswith(bot_trigger + arg) 

    if check_trigger('players'):
        await game.show_player()

    if check_trigger('loc'):
        await game.show_locations(message.author)

    if not game.is_live:
        if check_trigger('start'):
            await game.start_game()

        if check_trigger('join'):
            await game.join_player(message.author)
        
        if check_trigger('leave'):
            await game.leave_player(message.author)

    
    if game.get_player(message.author):
        # choice location by Traitor
        if check_trigger('c'):
            await game.choice_location(message.author, message.content.split(" ")[-1])
        
        if check_trigger('reveal'):
            await game.end_game()        

    if check_trigger():
        await message.delete()

bot.run(bot_token)