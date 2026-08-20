from __future__ import annotations

from typing import Any, Dict, List
import logging

from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


def _extract_text(payload: Dict[str, Any]) -> str:
    text = payload.get("text") or payload.get("body") or ""
    if isinstance(text, str):
        return text.strip()
    return ""


def _extract_chat_id(payload: Dict[str, Any]) -> str:
    return str(payload.get("chatId") or payload.get("from") or "")


def _extract_sender(payload: Dict[str, Any]) -> str:
    return str(payload.get("sender") or payload.get("author") or payload.get("from") or "")


def _extract_mentions(payload: Dict[str, Any]) -> List[str]:
    mentions = payload.get("mentionedJid") or []
    if isinstance(mentions, list):
        return [str(x) for x in mentions]
    return []


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
    chat_id = _extract_chat_id(payload)
    sender = _extract_sender(payload)
    text = _extract_text(payload)
    mentions = _extract_mentions(payload)

    if not chat_id or not text:
        return {"ok": True, "ignored": True, "reason": "missing_chat_or_text"}

    group = _is_group(chat_id)
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
