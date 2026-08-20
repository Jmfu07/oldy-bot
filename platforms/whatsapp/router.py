import logging
import time

from fastapi import APIRouter, HTTPException, Query, Request

from services.whatsapp_service import whatsapp_service
from platforms.whatsapp.handlers.ia import handle_ia_message

router = APIRouter(prefix="/webhook/whatsapp", tags=["whatsapp"])
logger = logging.getLogger(__name__)

_SEEN_MESSAGES: dict[str, float] = {}
_SEEN_TTL_SECONDS = 600
_MAX_MESSAGE_AGE_SECONDS = 120


def _cleanup_seen(now_ts: float) -> None:
    stale = [k for k, v in _SEEN_MESSAGES.items() if now_ts - v > _SEEN_TTL_SECONDS]
    for k in stale:
        _SEEN_MESSAGES.pop(k, None)


def _extract_message_envelope(payload: dict) -> tuple[str, str, str]:
    entry = (payload.get("entry") or [{}])[0]
    changes = (entry.get("changes") or [{}])[0]
    value = changes.get("value") or {}

    if value.get("statuses"):
        return "", "", "status_event"

    messages = value.get("messages") or []
    if not messages:
        return "", "", "no_message"

    msg = messages[0] if isinstance(messages[0], dict) else {}
    msg_id = str(msg.get("id") or "")
    ts = str(msg.get("timestamp") or "")
    if not msg_id:
        return "", "", "missing_message_id"

    return msg_id, ts, "ok"


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
    logger.info("WhatsApp webhook received")

    now_ts = time.time()
    _cleanup_seen(now_ts)

    msg_id, msg_ts, state = _extract_message_envelope(payload)
    if state != "ok":
        return {"ok": True, "ignored": True, "reason": state}

    if msg_id in _SEEN_MESSAGES:
        return {"ok": True, "ignored": True, "reason": "duplicate"}

    if msg_ts.isdigit() and (now_ts - float(msg_ts)) > _MAX_MESSAGE_AGE_SECONDS:
        _SEEN_MESSAGES[msg_id] = now_ts
        return {"ok": True, "ignored": True, "reason": "old_message"}

    _SEEN_MESSAGES[msg_id] = now_ts

    bot_jid = ""
    entry = (payload.get("entry") or [{}])[0]
    changes = (entry.get("changes") or [{}])[0]
    value = changes.get("value") or {}
    metadata = value.get("metadata") or {}
    if isinstance(metadata, dict):
        bot_jid = str(metadata.get("display_phone_number") or metadata.get("phone_number_id") or "")

    result = await handle_ia_message(payload, bot_jid=bot_jid)
    logger.info("WhatsApp handler result: %s", result)

    if result.get("ignored"):
        return {"ok": True, "ignored": True}

    chat_id = result.get("chatId") or payload.get("chatId") or payload.get("from") or ""
    reply = result.get("reply") or ""

    if chat_id and reply:
        send_result = await whatsapp_service.send_text(to=str(chat_id), body=str(reply))
        logger.info("WhatsApp send result: %s", send_result)

    return {"ok": True, "sent": bool(chat_id and reply)}
