import re
import logging
import discord
from discord.ext import commands
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from services.gemini_service import ask_gemini, split_message

logger = logging.getLogger("community_bot.ia")


# ==============================================================================
# DISCORD INTEGRATION
# ==============================================================================
class IADiscord(commands.Cog, name="Inteligencia Artificial"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ia", aliases=["gemini", "ask", "pregunta"], help="Consulta a la IA de Google Gemini.")
    async def cmd_ia(self, ctx: commands.Context, *, pregunta: str = None):
        if not pregunta:
            await ctx.send("💡 Por favor escribe tu consulta. Ejemplo: `!ia ¿cómo optimizar mi código Python?`")
            return

        async with ctx.typing():
            respuesta = await ask_gemini(pregunta, user_name=ctx.author.display_name)
            partes = split_message(respuesta, max_length=1950)
            for parte in partes:
                await ctx.reply(parte)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignorar mensajes de bots
        if message.author.bot:
            return

        # Si el bot es mencionado directamente en el mensaje
        if self.bot.user and self.bot.user in message.mentions:
            # Eliminar la mención del texto para procesar solo la consulta limpia
            prompt_limpio = re.sub(r"<@!?" + str(self.bot.user.id) + r">", "", message.content).strip()
            
            if not prompt_limpio:
                await message.reply("👋 ¡Hola! ¿En qué puedo ayudarte hoy? Escribe tu consulta junto a mi mención o usa `!ia <pregunta>`.")
                return

            async with message.channel.typing():
                respuesta = await ask_gemini(prompt_limpio, user_name=message.author.display_name)
                partes = split_message(respuesta, max_length=1950)
                for parte in partes:
                    await message.reply(parte)


async def setup_discord(bot: commands.Bot):
    await bot.add_cog(IADiscord(bot))


# ==============================================================================
# TELEGRAM INTEGRATION
# ==============================================================================
async def tg_cmd_ia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ia [pregunta] en Telegram."""
    if not update.effective_message or not update.effective_chat:
        return

    pregunta = " ".join(context.args) if context.args else ""
    if not pregunta:
        await update.effective_message.reply_text(
            "💡 Por favor ingresa tu consulta. Ejemplo: `/ia ¿Cuáles son los mejores hábitos para programar?`",
            parse_mode="Markdown",
        )
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    usuario = update.effective_user.first_name if update.effective_user else "Usuario"
    
    respuesta = await ask_gemini(pregunta, user_name=usuario)
    partes = split_message(respuesta, max_length=4000)
    for parte in partes:
        await update.effective_message.reply_text(parte)


async def tg_mention_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde cuando mencionan al bot o le escriben en chat privado."""
    if not update.effective_message or not update.effective_message.text or not update.effective_chat:
        return

    texto = update.effective_message.text
    chat_type = update.effective_chat.type
    bot_username = context.bot.username or ""

    # Determinar si el bot fue mencionado o es chat privado
    es_privado = chat_type == "private"
    es_mencion = bot_username and f"@{bot_username.lower()}" in texto.lower()
    es_reply_al_bot = (
        update.effective_message.reply_to_message
        and update.effective_message.reply_to_message.from_user
        and update.effective_message.reply_to_message.from_user.id == context.bot.id
    )

    if es_privado or es_mencion or es_reply_al_bot:
        prompt_limpio = re.sub(rf"@{bot_username}", "", texto, flags=re.IGNORECASE).strip() if bot_username else texto
        
        if not prompt_limpio and not es_reply_al_bot:
            await update.effective_message.reply_text("👋 ¡Hola! ¿En qué te puedo ayudar hoy? Escribe tu consulta o usa `/ia <pregunta>`.")
            return

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        usuario = update.effective_user.first_name if update.effective_user else "Usuario"

        respuesta = await ask_gemini(prompt_limpio or texto, user_name=usuario)
        partes = split_message(respuesta, max_length=4000)
        for parte in partes:
            await update.effective_message.reply_text(parte)


def setup_telegram(app):
    app.add_handler(CommandHandler("ia", tg_cmd_ia))
    app.add_handler(CommandHandler("gemini", tg_cmd_ia))
    app.add_handler(CommandHandler("ask", tg_cmd_ia))
    # Escucha menciones y mensajes privados (ignorando comandos para no duplicar)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tg_mention_handler))
