import logging

try:
    import discord
    from discord.ext import commands
except Exception as exc:
    discord = None
    commands = None
    _discord_import_error = exc

logger = logging.getLogger(__name__)


def build_discord_bot() -> commands.Bot:
    if discord is None or commands is None:
        raise RuntimeError(f"Discord no puede iniciarse en este entorno: {_discord_import_error}")

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready() -> None:
        logger.info("[Discord] Conectado como %s (%s)", bot.user, bot.user.id if bot.user else "N/A")

    return bot
