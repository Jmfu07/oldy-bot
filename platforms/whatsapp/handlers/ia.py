from __future__ import annotations

from typing import Any, Dict, List, Tuple
import logging

from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


def _pick_text(message: Dict[str, Any]) -> str:
    text = message.get("text") or {}
    if isinstance(text, dict):
        body = text.get("body")
        if isinstance(body, str) and body.strip():
            return body.strip()
    for key in ("body", "caption"):
        value = message.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _pick_mentions(message: Dict[str, Any]) -> List[str]:
    context = message.get("context") or message.get("contextInfo") or {}
    mentions = context.get("mentionedJid") or []
    if isinstance(mentions, list):
        return [str(x) for x in mentions]
    return []


def _extract_meta_message(payload: Dict[str, Any]) -> Tuple[str, str, str, List[str], bool]:
    entry = (payload.get("entry") or [{}])[0]
    changes = (entry.get("changes") or [{}])[0]
    value = changes.get("value") or {}
    contacts = value.get("contacts") or []
    messages = value.get("messages") or []
    message = messages[0] if messages and isinstance(messages[0], dict) else {}
    contact = contacts[0] if contacts and isinstance(contacts[0], dict) else {}

    sender = str(message.get("from") or contact.get("wa_id") or "")
    text = _pick_text(message)
    mentions = _pick_mentions(message)
    chat_id = sender
    is_group = bool(sender.endswith("@g.us") or value.get("metadata", {}).get("group_id"))

    return chat_id, sender, text, mentions, is_group


def _is_command(text: str) -> bool:
    lowered = text.lower()
    return lowered.startswith("/ia") or lowered.startswith("/reglas")


def _is_bot_mentioned(mentions: List[str], bot_jid: str) -> bool:
    return bool(bot_jid and bot_jid in mentions)


async def handle_ia_message(payload: Dict[str, Any], bot_jid: str) -> Dict[str, Any]:
    chat_id, sender, text, mentions, is_group = _extract_meta_message(payload)
    logger.info("WhatsApp parsed sender=%s text=%s group=%s", sender, text, is_group)

    if not sender or not text:
        return {"ok": True, "ignored": True, "reason": "missing_sender_or_text"}

    if is_group and not (_is_command(text) or _is_bot_mentioned(mentions, bot_jid)):
        return {"ok": True, "ignored": True, "reason": "group_message_not_addressed_to_bot"}

    prompt = text[3:].strip() if text.lower().startswith("/ia") else text
    if not prompt:
        prompt = "Hola, ¿puedes ayudarme?"

    reply = await gemini_service.ask(prompt=prompt, user_id=sender)
    logger.info("WhatsApp Gemini reply ready for sender=%s", sender)

    logger.info(
        "[WHATSAPP_IA] sender=%s group=%s processed=%s",
        sender,
        is_group,
        True,
    )

    return {
        "ok": True,
        "ignored": False,
        "chatId": sender,
        "reply": reply,
    }
