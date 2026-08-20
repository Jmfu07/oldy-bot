import os
import sys
import logging
import asyncio
import importlib
import pkgutil
from pathlib import Path
from dotenv import load_dotenv

import discord
from discord.ext import commands
from telegram.ext import ApplicationBuilder

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración del sistema de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("community_bot.main")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
DISCORD_PREFIX = os.getenv("DISCORD_PREFIX", "!").strip() or "!"

# ==============================================================================
# INICIALIZACIÓN DE INSTANCIAS DE BOTS
# ==============================================================================
# Configurar Discord con los intents necesarios para leer mensajes y menciones
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

discord_bot = commands.Bot(command_prefix=DISCORD_PREFIX, intents=intents, help_command=None)
telegram_app = None

if TELEGRAM_TOKEN and TELEGRAM_TOKEN != "tu_telegram_bot_token_aqui":
    telegram_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()


@discord_bot.event
async def on_ready():
    logger.info("=" * 60)
    logger.info("🎮 DISCORD BOT CONECTADO")
    logger.info("🤖 Usuario: %s (ID: %s)", discord_bot.user, discord_bot.user.id if discord_bot.user else "N/A")
    logger.info("🌐 Servidores conectados: %s", len(discord_bot.guilds))
    logger.info("=" * 60)


# ==============================================================================
# CARGADOR MODULAR RECURSIVO DE COMANDOS
# ==============================================================================
async def load_modular_commands():
    """
    Recorre recursivamente la carpeta 'commands/' e importa cada módulo
    registrando sus handlers para Discord y Telegram.
    """
    commands_dir = Path(__file__).resolve().parent / "commands"
    logger.info("🔍 Descubriendo módulos de comandos en: %s", commands_dir)

    loaded_modules = 0

    for root, _, files in os.walk(commands_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_path = Path(root) / file
                relative_path = module_path.relative_to(Path(__file__).resolve().parent)
                module_name = str(relative_path.with_suffix("")).replace(os.sep, ".")

                try:
                    module = importlib.import_module(module_name)
                    logger.info("📦 Módulo cargado: %s", module_name)

                    # Registrar en Discord si define setup_discord
                    if hasattr(module, "setup_discord"):
                        res = module.setup_discord(discord_bot)
                        if asyncio.iscoroutine(res):
                            await res
                        logger.debug(" -> Registrado en Discord: %s", module_name)

                    # Registrar en Telegram si define setup_telegram
                    if telegram_app and hasattr(module, "setup_telegram"):
                        module.setup_telegram(telegram_app)
                        logger.debug(" -> Registrado en Telegram: %s", module_name)

                    loaded_modules += 1
                except Exception as exc:
                    logger.error("❌ Error al cargar módulo %s: %s", module_name, exc, exc_info=True)

    logger.info("✅ Total de módulos de comandos cargados: %s", loaded_modules)


# ==============================================================================
# EJECUTORES ASÍNCRONOS PARA DISCORD Y TELEGRAM
# ==============================================================================
async def run_discord():
    """Inicia el bot de Discord."""
    if not DISCORD_TOKEN or DISCORD_TOKEN == "tu_discord_bot_token_aqui":
        logger.warning("⚠️ DISCORD_TOKEN no configurado. El bot de Discord estará inactivo.")
        return

    logger.info("🚀 Iniciando conexión con Discord...")
    try:
        await discord_bot.start(DISCORD_TOKEN)
    except Exception as exc:
        logger.error("❌ Error en Discord Bot: %s", exc)


async def run_telegram():
    """Inicia el bot de Telegram."""
    if not telegram_app:
        logger.warning("⚠️ TELEGRAM_TOKEN no configurado. El bot de Telegram estará inactivo.")
        return

    logger.info("🚀 Iniciando conexión con Telegram (Polling)...")
    try:
        await telegram_app.initialize()
        await telegram_app.start()
        await telegram_app.updater.start_polling(drop_pending_updates=True)
        logger.info("=" * 60)
        logger.info("📱 TELEGRAM BOT CONECTADO Y ESCUCHANDO MENSAJES")
        logger.info("=" * 60)

        # Mantener activo mientras no se cancele la tarea
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("🛑 Deteniendo bot de Telegram...")
    except Exception as exc:
        logger.error("❌ Error en Telegram Bot: %s", exc)
    finally:
        if telegram_app.updater and telegram_app.updater.running:
            await telegram_app.updater.stop()
        if telegram_app.running:
            await telegram_app.stop()
        await telegram_app.shutdown()


# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL CONCURRENTE
# ==============================================================================
async def main():
    """Orquesta la carga de módulos y arranca ambos bots concurrentemente."""
    print("""
    ===============================================================
    🤖 BOT HÍBRIDO DE COMUNIDAD (DISCORD + TELEGRAM + GEMINI AI)
    ===============================================================
    """)

    # 1. Cargar comandos modulares
    await load_modular_commands()

    # 2. Verificar estado de tokens
    has_discord = bool(DISCORD_TOKEN and DISCORD_TOKEN != "tu_discord_bot_token_aqui")
    has_telegram = bool(TELEGRAM_TOKEN and TELEGRAM_TOKEN != "tu_telegram_bot_token_aqui")

    if not has_discord and not has_telegram:
        logger.warning("⚠️ No se ha proporcionado DISCORD_TOKEN ni TELEGRAM_TOKEN en .env")
        logger.info("💡 Agrega tus tokens al archivo .env para conectar los bots.")
        logger.info("El servidor permanecerá en espera. Presiona Ctrl+C para salir.")

    # 3. Lanzar tareas en paralelo
    tasks = []
    if has_discord:
        tasks.append(asyncio.create_task(run_discord()))
    if has_telegram:
        tasks.append(asyncio.create_task(run_telegram()))

    if tasks:
        await asyncio.gather(*tasks)
    else:
        while True:
            await asyncio.sleep(60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Programa finalizado por el usuario.")
