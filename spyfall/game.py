import random
import sys
import os
import json
import time

import config
from discord import Embed

SPY = "Traitor"

# object to keep track of players in the game
class Player:
    def __init__(self, channel):
        # discord messagable pipe
        self.channel = channel
        
        # game role
        self.role = None


# object to keep track of game state
class Game:
    def __init__(self, bot):
        self.bot = bot

        # variable for config location
        self.LOCATIONS_FILE = 'spyfall_locations.json'

        # locations, roles and other json settings
        if os.path.exists(self.LOCATIONS_FILE):
            with open(self.LOCATIONS_FILE, 'r') as locations_file:
                self._game_data = json.load(locations_file)
        else:
            print("The file %s does not exist or cannot be opened" % LOCATIONS_FILE)
            sys.exit(-1)
        
        # location list
        self.loc_list = self._game_data['locations']
        
        # messagable pipe
        self.channel = None
        self.guild   = None
        
        # list of player objects
        self.players = []

        # keeps track of the current location (int index of locations json key)
        self.location = None

        # game is live only when it is started, by default it is not
        self.is_live = False

        # the amount of time in seconds available in each round (default: 480 seconds or 8 minutes)
        self.round_time = 480

        # time left in seconds
        self.time_left = self.round_time

    # add player to game
    async def join_player(self, user_channel):
        for player in self.players:
            if player.channel == user_channel:
                return
    
        self.players.append(Player(user_channel))
        await self.channel.send(embed=Embed(description="<@%s> присоединяется к игре" % user_channel.id, colour=config.PREGAME))
        
    # remove player from game
    async def leave_player(self, user_channel):
        for player in self.players:
            if player.channel == user_channel:
                self.players.remove(player)
                return await self.channel.send(embed=Embed(description="<@%s> покидает игру." % user_channel.id, colour=config.PREGAME))
    
    # get player by pipe
    def get_player(self, user_channel):
        for player in self.players:
            if player.channel == user_channel:
                return player
    
    async def show_locations(self):
        locs = await self.channel.send(embed=Embed(
            colour=config.SHOW_CREDITS,
            title="TraitorFall - Locations List", 
            description="\n".join("%s. **%s**" % (i, l['Location']) for i, l in enumerate(self.loc_list, 1))))        
    
    # show player to pipe
    async def show_player(self):
        playing = 'Текущие игроки:\n'
        for i, player in enumerate(self.players, 1):
            playing += "%s. **%s#%s**\n" % (i, player.channel.display_name, player.channel.discriminator)

        await self.channel.send(embed=Embed(description=playing, colour=config.PREGAME))
    
    # make alive while, show roles, locations
    async def start_game(self):
        if len(self.players) < 3:
            return await self.channel.send('Мало игроков.')

        self.is_live = True
        self.time_left = time.time() + self.round_time
        self.location = random.choice(self.loc_list)
        random.choice(self.players).role = SPY

        title = "TraitorFall - Game"
        for player in self.players:
            description = "Ваша роль ---> **ПРЕДАТЕЛЬ** \n Локация ---> *???*"
            if player.role != SPY:
                player.role = random.choice(self.location['Roles'])
                description = "Ваша роль ---> **%s** \nЛокация ---> *%s*" % (player.role, self.location['Location'])

            await player.channel.send(embed=Embed(title=title, description=description, colour=config.SHOW_CREDITS))
        
        await self.channel.send("Игра начинается!")
    
        locs = await self.channel.send(embed=Embed(
            colour=config.SHOW_CREDITS,
            title="TraitorFall - Locations List", 
            description="\n".join("%s. **%s**" % (i, l['Location']) for i, l in enumerate(self.loc_list, 1))))

        while self.is_live and time.time() < self.time_left:
            await asyncio.sleep(1)

        # Loop exited, game has ended or has run out of time. End it and clear messages.
        await locs.delete()

        # If game is still live, it means the spy has not been revealed yet even though the time is up.
        # Players still have a last chance to vote who the spy is before ending the game.
        if self.is_live:
            await self.channel.send("Время вышло! Укажите шпиона.")        

    # take end by Traitor
    async def choice_location(self, user_channel, choice):
        player = self.get_player(user_channel)
        if player.role != SPY or not(choice.isdigit()) or not(0 < int(choice) < len(self.loc_list) + 1):
            await self.channel.send(embed=Embed(description="<@%s> наказан" % user_channel.id, colour=config.ANTITRAIT))
            role = guild.get_role(config.ANTITRAITOR)
            return await user_channel.add_roles(config.ANTITRAITOR)
        
        self.end_game(1)
        
        description = "<@%s> тренируйся лучше, ты проиграл!"
        if self.loc_list[int(choice)-1] == self.location:
            description = "<@%s> победил в игре!"
        await self.channel.send(embed=Embed(description=description, colour=config.SHOW_END))

    # reveal identity of the spy
    async def end_game(self, force=0):
        if force or time.time() > self.time_left():
            self.is_live = False
            self.players.clear()

            title = 'TraitorFall - Reveal'
            description = 'Локацией было --> **%s**\n\n' % self.location['Location']
        
            for i, player in enumerate(self.players):
                playing += "%s. **%s#%s**\n" % (i, player.channel.display_name, player.channel.discriminator)
    
            await self.channel.send(embed=Embed(title=title, description=description, colour=config.SHOW_END))