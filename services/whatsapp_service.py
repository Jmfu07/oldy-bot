import os
import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self) -> None:
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN", "").strip()
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "").strip()
        self.verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "").strip()
        self.api_version = os.getenv("WHATSAPP_API_VERSION", "v20.0").strip()

    def is_configured(self) -> bool:
        return bool(self.access_token and self.phone_number_id)

    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        if mode != "subscribe":
            return None
        if token != self.verify_token:
            return None
        return challenge

    async def send_text(self, to: str, body: str) -> Dict[str, Any]:
        if not self.is_configured():
            raise ValueError("WhatsApp Cloud API no está configurada.")

        url = (
            f"https://graph.facebook.com/{self.api_version}/"
            f"{self.phone_number_id}/messages"
        )
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": body},
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=headers, json=payload)

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.error("WhatsApp send failed: %s", response.text)
            raise

        return response.json()


whatsapp_service = WhatsAppService()
