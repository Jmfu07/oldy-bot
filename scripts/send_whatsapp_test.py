import asyncio
import os

from dotenv import load_dotenv

from services.whatsapp_service import whatsapp_service


async def main() -> None:
    load_dotenv()
    recipient = os.getenv("WHATSAPP_RECIPIENT", "").strip()
    if not recipient:
        raise ValueError("Falta WHATSAPP_RECIPIENT en el entorno.")

    result = await whatsapp_service.send_text(
        to=recipient,
        body=os.getenv(
            "WHATSAPP_TEST_MESSAGE",
            "Hola, este es un mensaje de prueba desde mi_bot_comunidad.",
        ),
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
