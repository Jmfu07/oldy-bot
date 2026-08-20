import discord
from discord.ext import commands


def build_discord_bot() -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready() -> None:
        print(f"[Discord] Conectado como {bot.user} ({bot.user.id})")

    return bot
