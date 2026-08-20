from fastapi import APIRouter, HTTPException, Query, Request

from services.whatsapp_service import whatsapp_service
from platforms.whatsapp.handlers.ia import handle_ia_message

router = APIRouter(prefix="/webhook/whatsapp", tags=["whatsapp"])


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(default="", alias="hub.mode"),
    hub_token: str = Query(default="", alias="hub.verify_token"),
    hub_challenge: str = Query(default="", alias="hub.challenge"),
):
    challenge = whatsapp_service.verify_webhook(hub_mode, hub_token, hub_challenge)
    if challenge is None:
        raise HTTPException(status_code=403, detail="Verification failed")
    return int(hub_challenge) if hub_challenge.isdigit() else hub_challenge


@router.post("")
async def webhook(request: Request):
    payload = await request.json()
    logging.getLogger(__name__).info("WhatsApp webhook received")
    bot_jid = ""
    entry = (payload.get("entry") or [{}])[0]
    changes = (entry.get("changes") or [{}])[0]
    value = changes.get("value") or {}
    metadata = value.get("metadata") or {}
    if isinstance(metadata, dict):
        bot_jid = str(metadata.get("display_phone_number") or metadata.get("phone_number_id") or "")
    result = await handle_ia_message(payload, bot_jid=bot_jid)
    logging.getLogger(__name__).info("WhatsApp handler result: %s", result)

    if result.get("ignored"):
        return {"ok": True, "ignored": True}

    chat_id = result.get("chatId") or payload.get("chatId") or payload.get("from") or ""
    reply = result.get("reply") or ""

    if chat_id and reply:
        send_result = await whatsapp_service.send_text(to=str(chat_id), body=str(reply))
        logging.getLogger(__name__).info("WhatsApp send result: %s", send_result)

    return {"ok": True, "sent": bool(chat_id and reply)}

