import discord
from discord.ext import commands
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

AYUDA_TEXT = """
🤖 **PANEL DE AYUDA Y COMANDOS DEL BOT**

📌 **Categoría General:**
• `/reglas` o `!reglas` — Muestra las normas de la comunidad.
• `/ayuda` o `!ayuda` — Muestra este menú de comandos.

🛡️ **Categoría Moderación:**
• `/limpiar <cantidad>` o `!limpiar <cantidad>` — Borra una cantidad de mensajes recientes (requiere permisos).
• `/aviso @usuario <motivo>` o `!aviso @usuario <motivo>` — Envía una advertencia de moderación.

🧠 **Categoría Inteligencia Artificial (Google Gemini):**
• `/ia <tu pregunta>` o `!ia <tu pregunta>` — Consulta directamente a la IA.
• **Mención directa**: Etiqueta al bot con `@Bot <pregunta>` en cualquier canal/grupo para que te responda.

💡 *Bot híbrido activo en Discord y Telegram con Google Gemini.*
"""


# ==============================================================================
# DISCORD INTEGRATION
# ==============================================================================
class AyudaDiscord(commands.Cog, name="Ayuda"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ayuda", aliases=["help"], help="Muestra el menú de ayuda con todos los comandos.")
    async def cmd_ayuda(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🤖 Comandos del Bot de Comunidad",
            description=AYUDA_TEXT.strip(),
            color=discord.Color.green(),
        )
        embed.set_footer(text="Usa el prefijo ! o los comandos slash /")
        await ctx.send(embed=embed)


async def setup_discord(bot: commands.Bot):
    await bot.add_cog(AyudaDiscord(bot))


# ==============================================================================
# TELEGRAM INTEGRATION
# ==============================================================================
async def tg_cmd_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ayuda y /help en Telegram."""
    if update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=AYUDA_TEXT.strip(),
            parse_mode="Markdown",
        )


def setup_telegram(app):
    app.add_handler(CommandHandler("ayuda", tg_cmd_ayuda))
    app.add_handler(CommandHandler("help", tg_cmd_ayuda))
    app.add_handler(CommandHandler("start", tg_cmd_ayuda))
