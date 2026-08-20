import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def _is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat = update.effective_chat
    user = update.effective_user
    if not chat or not user:
        return False

    member = await context.bot.get_chat_member(chat.id, user.id)
    return member.status in ("administrator", "creator")


async def gestionar_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Stub seguro de gestión/auditoría para Telegram.
    Requiere admin y solo registra el evento.
    Uso sugerido: /gestionar_usuario <accion> <motivo>
    """
    if not update.effective_chat or update.effective_chat.type == "private":
        await update.effective_message.reply_text(
            "Este comando está pensado para grupos."
        )
        return

    if not await _is_admin(update, context):
        await update.effective_message.reply_text(
            "Solo administradores pueden usar este comando."
        )
        return

    actor = update.effective_user
    chat = update.effective_chat
    args = context.args or []
    accion = args[0] if len(args) > 0 else "sin_accion"
    motivo = " ".join(args[1:]).strip() if len(args) > 1 else "sin_motivo"

    logger.info(
        "[TELEGRAM_AUDIT] chat=%s actor=%s accion=%s motivo=%s msg_id=%s",
        chat.id,
        actor.id if actor else None,
        accion,
        motivo,
        update.effective_message.message_id if update.effective_message else None,
    )

    await update.effective_message.reply_text(
        "Evento de gestión registrado en auditoría. "
        "Modo seguro activo (sin acción punitiva automática)."
    )
