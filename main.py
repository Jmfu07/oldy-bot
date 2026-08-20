import asyncio
import logging
import os
from contextlib import suppress

from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn

from platforms.whatsapp.handlers.ia import handle_ia_message
from platforms.whatsapp.handlers.moderacion.gestionar_participante import (
    gestionar_participante,
)

from platforms.discord.bot import build_discord_bot
from platforms.telegram.bot import build_telegram_application

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("main")

app = FastAPI(title="mi_bot_comunidad", version="1.0.0")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request) -> dict:
    payload = await request.json()
    event_type = str(payload.get("event") or "message")

    if event_type == "moderacion":
        result = await gestionar_participante(payload)
        return {"ok": True, "result": result}

    bot_jid = os.getenv("WHATSAPP_BOT_JID", "")
    result = await handle_ia_message(payload, bot_jid=bot_jid)
    return {"ok": True, "result": result}


async def run_fastapi_server() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "10000"))
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level=os.getenv("UVICORN_LOG_LEVEL", "info"),
    )
    server = uvicorn.Server(config)
    await server.serve()


async def run_discord_bot() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.warning("DISCORD_TOKEN no configurado; Discord no iniciará.")
        await asyncio.Event().wait()
        return

    bot = build_discord_bot()
    await bot.start(token)


async def run_telegram_bot() -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.warning("TELEGRAM_TOKEN no configurado; Telegram no iniciará.")
        await asyncio.Event().wait()
        return

    application = build_telegram_application(token)
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    try:
        await asyncio.Event().wait()
    finally:
        with suppress(Exception):
            await application.updater.stop()
        with suppress(Exception):
            await application.stop()
        with suppress(Exception):
            await application.shutdown()


async def main() -> None:
    await asyncio.gather(
        run_discord_bot(),
        run_telegram_bot(),
        run_fastapi_server(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Cierre manual recibido.")
