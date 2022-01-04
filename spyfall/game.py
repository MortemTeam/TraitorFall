from typing import List, Optional, Dict
import datetime
import random

from discord import Embed, Guild, TextChannel, Message, Colour, Member

import states


class Player:
    def __init__(self, member: Member, role: str):
        self.member = member
        self.role = role


class Game:
    guild: Guild = None
    channel: TextChannel = None
    admins: Optional[List[int]] = []
    intents: Optional[List[str]] = []

    locations: Dict = {}
    current_location: Dict = None
    antagonist: str = None
    min_players: int = 0

    state: Colour = states.IDLE
    message: Optional[Message] = None
    lobby: List[Member] = []
    game: List[Player] = []

    @classmethod
    def reset(cls):
        cls.state = states.IDLE
        cls.message = None
        cls.lobby.clear()
        cls.game.clear()

    @classmethod
    def can_start(cls):
        return len(cls.lobby) >= cls.min_players

    @classmethod
    async def start(cls):
        cls.state = states.GAME
        cls.current_location = random.choice(cls.locations)
        for m in cls.lobby:
            cls.game.append(Player(m, random.choice(cls.current_location['Roles'])))

        random.choice(cls.game).role = cls.antagonist
        await cls.announce_roles()

    @classmethod
    async def announce_roles(cls):
        for p in cls.game:
            await p.member.send(embed=Embed(
                title="¯\_(ツ)_/¯" if p.role == cls.antagonist else cls.current_location['Location'],
                description=p.role,
            ).set_author(
                name="Ваша карта: ",
                icon_url="https://cdn.discordapp.com/emojis/829717472088424538.gif?v=1",
            ).set_footer(
                text=cls.get_footer(),
            ))

    @classmethod
    def get_embed(cls):
        return Embed(
            title=cls.get_title(),
            description=cls.get_description(),
            colour=cls.state,
        ).set_footer(
            text=cls.get_footer(),
        )

    @classmethod
    def get_title(cls):
        if cls.state == states.IDLE:
            return "Игра остановлена!"
        if cls.state == states.LOBBY:
            return "Игра начинается!"
        if cls.state == states.GAME:
            return "Игра уже идет!"

    @classmethod
    def get_description(cls):
        return (
            "{} - Присоединиться к игре\n"
            "{} - Получить список локаций\n"
            "{} - Перезапустить таймер\n"
            "{} - Начать игру\n"
            "{} - Закрыть лобби\n"
            "\nИгроки:\n"
            "{}"
            "\n\nУ вас две минуты чтобы присоединиться к игре..."
        ).format(
            *cls.intents,
            "\n".join("> {}. {}#{}".format(i, x.nick, x.discriminator) for i, x in enumerate(cls.lobby, 1))
            if cls.lobby else "¯\_(ツ)_/¯"
        )

    @classmethod
    def get_footer(cls):
        return "Время обновления: %s" % datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
