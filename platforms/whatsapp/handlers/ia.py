from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import logging

from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


def _pick_text(message: Dict[str, Any]) -> str:
    for key in ("text", "body", "caption"):
        value = message.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _pick_mentions(message: Dict[str, Any]) -> List[str]:
    context = message.get("contextInfo") or {}
    mentions = context.get("mentionedJid") or message.get("mentionedJid") or []
    if isinstance(mentions, list):
        return [str(x) for x in mentions]
    return []


def _extract_meta_message(payload: Dict[str, Any]) -> Tuple[str, str, str, List[str], Dict[str, Any]]:
    entry = (payload.get("entry") or [{}])[0]
    changes = (entry.get("changes") or [{}])[0]
    value = changes.get("value") or {}
    messages = value.get("messages") or []
    contacts = value.get("contacts") or []
    message = messages[0] if messages and isinstance(messages[0], dict) else {}
    contact = contacts[0] if contacts and isinstance(contacts[0], dict) else {}

    from_id = str(message.get("from") or value.get("from") or contact.get("wa_id") or "")
    chat_id = str(value.get("chatId") or message.get("chatId") or from_id)
    sender = str(contact.get("wa_id") or message.get("from") or from_id)
    text = _pick_text(message)
    mentions = _pick_mentions(message)

    return chat_id, sender, text, mentions, value


def _is_group(chat_id: str) -> bool:
    return chat_id.endswith("@g.us")


def _is_command(text: str) -> bool:
    lowered = text.lower()
    return lowered.startswith("/ia") or lowered.startswith("/reglas")


def _is_bot_mentioned(mentions: List[str], bot_jid: str) -> bool:
    if not bot_jid:
        return False
    return bot_jid in mentions


async def handle_ia_message(payload: Dict[str, Any], bot_jid: str) -> Dict[str, Any]:
    """
    Lógica WhatsApp IA:
    - Privado (1 a 1): procesa todos los mensajes.
    - Grupo (@g.us): solo si es comando (/ia,/reglas) o si menciona al bot.
    """
    chat_id, sender, text, mentions, value = _extract_meta_message(payload)

    if not chat_id or not text:
        return {"ok": True, "ignored": True, "reason": "missing_chat_or_text"}

    group = _is_group(chat_id) or bool((value.get("metadata") or {}).get("group_id"))
    should_process = True

    if group:
        should_process = _is_command(text) or _is_bot_mentioned(mentions, bot_jid)
        if not should_process:
            return {"ok": True, "ignored": True, "reason": "group_message_not_addressed_to_bot"}

    prompt = text
    if text.lower().startswith("/ia"):
        prompt = text[3:].strip() or "Hola, ¿puedes ayudarme?"

    reply = await gemini_service.ask(prompt=prompt, user_id=sender)

    logger.info(
        "[WHATSAPP_IA] chat=%s sender=%s group=%s processed=%s",
        chat_id,
        sender,
        group,
        should_process,
    )

    return {
        "ok": True,
        "ignored": False,
        "chatId": chat_id,
        "reply": reply,
    }
