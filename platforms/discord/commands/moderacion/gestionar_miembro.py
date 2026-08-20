import logging
from discord.ext import commands
from discord import app_commands
import discord

logger = logging.getLogger(__name__)


class GestionarMiembro(commands.Cog):
    """
    Stub seguro de gestión/auditoría de miembros.
    Verifica permisos y registra el evento en logs.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="gestionar_miembro",
        description="Audita una solicitud de gestión de miembro (stub seguro).",
    )
    @app_commands.describe(
        miembro="Miembro objetivo",
        accion="Acción de auditoría (ej: revisar_rol, seguimiento, observacion)",
        motivo="Motivo de la acción",
    )
    async def gestionar_miembro(
        self,
        interaction: discord.Interaction,
        miembro: discord.Member,
        accion: str,
        motivo: str,
    ) -> None:
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "No tienes permisos para usar este comando.", ephemeral=True
            )
            return

        logger.info(
            "[DISCORD_AUDIT] guild=%s canal=%s actor=%s target=%s accion=%s motivo=%s",
            interaction.guild_id,
            interaction.channel_id,
            interaction.user.id,
            miembro.id,
            accion,
            motivo,
        )

        await interaction.response.send_message(
            "Evento de gestión registrado en auditoría. "
            "Este comando está en modo seguro (sin acción punitiva automática).",
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GestionarMiembro(bot))
