from __future__ import annotations

from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


def _is_group(chat_id: str) -> bool:
    return bool(chat_id and chat_id.endswith("@g.us"))


def _is_admin(payload: Dict[str, Any]) -> bool:
    """
    Lee una bandera de admin desde el webhook.
    Puedes adaptar a tu proveedor real:
    - payload["isAdmin"] = True
    - payload["sender"]["isAdmin"] = True
    """
    if isinstance(payload.get("isAdmin"), bool):
        return payload["isAdmin"]

    sender = payload.get("sender")
    if isinstance(sender, dict) and isinstance(sender.get("isAdmin"), bool):
        return sender["isAdmin"]

    return False


async def gestionar_participante(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stub seguro de gestión en grupos.
    No ejecuta expulsiones ni bloqueos; solo valida y registra auditoría.
    """
    chat_id = str(payload.get("chatId") or payload.get("from") or "")
    actor = payload.get("author") or payload.get("sender") or payload.get("from")
    target = payload.get("target") or payload.get("participant")
    accion = payload.get("action") or "gestion_stub"
    motivo = payload.get("reason") or "sin_motivo"

    if not _is_group(chat_id):
        return {"ok": False, "error": "solo_disponible_en_grupos"}

    if not _is_admin(payload):
        return {"ok": False, "error": "requiere_admin"}

    logger.info(
        "[WHATSAPP_AUDIT] chat=%s actor=%s target=%s accion=%s motivo=%s",
        chat_id,
        actor,
        target,
        accion,
        motivo,
    )

    return {
        "ok": True,
        "status": "audit_logged",
        "message": "Evento de gestión registrado (modo seguro, sin acción punitiva).",
    }
