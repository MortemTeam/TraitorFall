from typing import List, Optional, Dict

from discord import Embed, Guild, TextChannel, Message, Colour, Member

import states


class Game:
    guild: Guild = None
    channel: TextChannel = None
    admins: Optional[List[int]] = []
    intents: Optional[List[str]] = []

    locations: Dict = {}
    current_location: str = None
    antagonist: str = None

    state: Colour = states.IDLE
    message: Optional[Message] = None
    lobby: List[Member] = []

    @classmethod
    def reset(cls):
        cls.state = states.IDLE
        cls.message = None
        cls.lobby.clear()

    @classmethod
    def get_embed(cls):
        return Embed(
            title=cls.get_title(),
            description=cls.get_description(),
            colour=cls.state,
        ).set_footer(
            text="У вас две минуты чтобы присоединиться к игре...",
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
        ).format(
            *cls.intents,
            "\n".join("> {}. {}#{}".format(i, x.nick, x.discriminator) for i, x in enumerate(cls.lobby, 1))
            if cls.lobby else "¯\_(ツ)_/¯"
        )
