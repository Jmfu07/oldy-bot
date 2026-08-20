import discord
from discord.ext import commands
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


# ==============================================================================
# DISCORD INTEGRATION
# ==============================================================================
class ModeracionDiscord(commands.Cog, name="Moderación"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="limpiar", aliases=["purge", "clear"], help="Elimina una cantidad de mensajes en el canal.")
    @commands.has_permissions(manage_messages=True)
    async def cmd_limpiar(self, ctx: commands.Context, cantidad: int = 5):
        if cantidad < 1 or cantidad > 100:
            await ctx.send("⚠️ Por favor indica una cantidad entre 1 y 100 mensajes.")
            return

        # +1 para incluir el comando del usuario
        eliminados = await ctx.channel.purge(limit=cantidad + 1)
        confirm = await ctx.send(f"🧹 Se han eliminado **{len(eliminados) - 1}** mensajes correctamente.", delete_after=4)

    @cmd_limpiar.error
    async def cmd_limpiar_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ No tienes permisos de `Gestionar Mensajes` para usar este comando.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("⚠️ Uso correcto: `!limpiar <cantidad de mensajes>` (ej: `!limpiar 10`).")
        else:
            await ctx.send(f"⚠️ Error al ejecutar moderación: {error}")

    @commands.command(name="aviso", aliases=["warn"], help="Envía una advertencia a un miembro de la comunidad.")
    @commands.has_permissions(kick_members=True)
    async def cmd_aviso(self, ctx: commands.Context, miembro: discord.Member, *, motivo: str = "Incumplimiento de las reglas"):
        embed = discord.Embed(
            title="⚠️ Advertencia de Moderación",
            description=f"El usuario {miembro.mention} ha recibido un aviso formal.",
            color=discord.Color.gold(),
        )
        embed.add_field(name="Motivo:", value=motivo, inline=False)
        embed.add_field(name="Moderador:", value=ctx.author.display_name, inline=True)
        embed.set_footer(text="Por favor revisa las reglas con !reglas")
        await ctx.send(embed=embed)

    @cmd_aviso.error
    async def cmd_aviso_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ No tienes permisos de moderación para emitir avisos.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("⚠️ No se encontró al usuario especificado. Uso: `!aviso @usuario <motivo>`.")
        else:
            await ctx.send(f"⚠️ Error: {error}")


async def setup_discord(bot: commands.Bot):
    await bot.add_cog(ModeracionDiscord(bot))


# ==============================================================================
# TELEGRAM INTEGRATION
# ==============================================================================
async def tg_cmd_limpiar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /limpiar en Telegram (elimina el mensaje citado o envía instrucción)."""
    if not update.effective_chat or not update.message:
        return

    # Verificar si responde a un mensaje
    if update.message.reply_to_message:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.reply_to_message.message_id,
            )
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id,
            )
        except Exception as e:
            await update.message.reply_text(f"⚠️ No pude eliminar el mensaje. Asegúrate de que el bot sea administrador: {e}")
    else:
        await update.message.reply_text("💡 Para eliminar un mensaje específico, responde al mensaje con `/limpiar`.")


async def tg_cmd_aviso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /aviso en Telegram."""
    if not update.effective_message:
        return

    args = context.args or []
    motivo = " ".join(args) if args else "Incumplimiento de las reglas"

    if update.message and update.message.reply_to_message and update.message.reply_to_message.from_user:
        usuario = update.message.reply_to_message.from_user.first_name
        msg = f"⚠️ *Aviso de Moderación para {usuario}*\n\n📋 *Motivo:* {motivo}\n\nPor favor consulta las `/reglas`."
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.effective_message.reply_text(
            "💡 Para advertir a un miembro, responde a uno de sus mensajes con `/aviso <motivo>`."
        )


def setup_telegram(app):
    app.add_handler(CommandHandler("limpiar", tg_cmd_limpiar))
    app.add_handler(CommandHandler("aviso", tg_cmd_aviso))
    app.add_handler(CommandHandler("warn", tg_cmd_aviso))
