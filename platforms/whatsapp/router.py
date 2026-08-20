from fastapi import APIRouter, HTTPException, Query, Request

from services.whatsapp_service import whatsapp_service
from platforms.whatsapp.handlers.ia import handle_ia_message
from platforms.whatsapp.handlers.moderacion.gestionar_participante import (
    gestionar_participante,
)

router = APIRouter(prefix="/webhook/whatsapp", tags=["whatsapp"])


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(default=""),
    hub_token: str = Query(default=""),
    hub_challenge: str = Query(default=""),
):
    challenge = whatsapp_service.verify_webhook(hub_mode, hub_token, hub_challenge)
    if challenge is None:
        raise HTTPException(status_code=403, detail="Verification failed")
    return challenge


@router.post("")
async def webhook(request: Request):
    payload = await request.json()
    event_type = str(payload.get("event") or "message")

    if event_type == "moderacion":
        return {"ok": True, "result": await gestionar_participante(payload)}

    bot_jid = payload.get("botJid") or ""
    return {"ok": True, "result": await handle_ia_message(payload, bot_jid=bot_jid)}
