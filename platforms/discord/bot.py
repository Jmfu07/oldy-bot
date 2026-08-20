import logging

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


def build_discord_bot() -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready() -> None:
        logger.info("[Discord] Conectado como %s (%s)", bot.user, bot.user.id if bot.user else "N/A")

    return bot
