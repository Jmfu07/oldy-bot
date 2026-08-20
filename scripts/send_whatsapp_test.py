import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.whatsapp_service import whatsapp_service


async def main() -> None:
    load_dotenv(ROOT / ".env")
    recipient = os.getenv("WHATSAPP_RECIPIENT", "").strip()
    if not recipient:
        raise ValueError("Falta WHATSAPP_RECIPIENT en el entorno.")

    result = await whatsapp_service.send_text(
        to=recipient,
        body=os.getenv(
            "WHATSAPP_TEST_MESSAGE",
            "Segundo mensaje de prueba desde mi_bot_comunidad. Si te llega, ya está todo listo.",
        ),
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
