from telegram.ext import Application, CommandHandler

from platforms.telegram.handlers.moderacion.gestionar_usuario import gestionar_usuario


async def _start(update, context) -> None:
    await update.effective_message.reply_text("Bot de Telegram activo ✅")


def build_telegram_application(token: str) -> Application:
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", _start))
    app.add_handler(CommandHandler("gestionar_usuario", gestionar_usuario))

    return app
