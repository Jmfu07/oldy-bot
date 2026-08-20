import discord
from discord.ext import commands
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

REGLAS_TEXT = """
📜 **REGLAS OFICIALES DE LA COMUNIDAD** 📜

1. **Respeto y Convivencia**: Trata a todos los miembros con cortesía. Cero tolerancia al acoso, discriminación o lenguaje ofensivo.
2. **Sin Spam ni Auto-promoción**: Prohibido publicar enlaces no autorizados, publicidad no solicitada o flooding de mensajes.
3. **Uso Adecuado de Canales / Temas**: Publica tus dudas o aportes en el canal correspondiente.
4. **Contenido Apto para Todo Público (SFW)**: No compartas contenido explícito, violento o inapropiado.
5. **Respeta las Decisiones de Moderación**: Los moderadores velan por el orden. Sigue sus instrucciones en todo momento.

💡 *¡Gracias por ser parte de nuestra comunidad y ayudarnos a mantener un espacio agradable para todos!*
"""


# ==============================================================================
# DISCORD INTEGRATION
# ==============================================================================
class ReglasDiscord(commands.Cog, name="Reglas"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="reglas", help="Muestra las reglas de convivencia de la comunidad.")
    async def cmd_reglas(self, ctx: commands.Context):
        embed = discord.Embed(
            title="📜 Normas de la Comunidad",
            description=REGLAS_TEXT.strip(),
            color=discord.Color.blue(),
        )
        embed.set_footer(text="Comunidad Unificada • Discord & Telegram")
        await ctx.send(embed=embed)


async def setup_discord(bot: commands.Bot):
    await bot.add_cog(ReglasDiscord(bot))


# ==============================================================================
# TELEGRAM INTEGRATION
# ==============================================================================
async def tg_cmd_reglas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /reglas en Telegram."""
    if update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=REGLAS_TEXT.strip(),
            parse_mode="Markdown",
        )


def setup_telegram(app):
    app.add_handler(CommandHandler("reglas", tg_cmd_reglas))
