import os
import logging
import time
import re
from collections import deque
from typing import Optional

from google import genai
from google.genai import types, errors as ga_errors

logger = logging.getLogger(__name__)


class GeminiService:
    """Gemini client with simple local rate limiting and graceful 429 handling."""

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Falta GEMINI_API_KEY en variables de entorno.")

        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = genai.Client(api_key=api_key)
        self.system_instruction = os.getenv(
            "GEMINI_SYSTEM_INSTRUCTION",
            "Eres un asistente amable y claro para comunidades online. Responde en español neutro, con tono respetuoso, breve y útil."
        )

        # Simple leaky bucket: limit requests per window
        try:
            self._limit = int(os.getenv("GEMINI_RATE_LIMIT_PER_MIN", "5"))
        except Exception:
            self._limit = 5
        try:
            self._window = int(os.getenv("GEMINI_RATE_LIMIT_WINDOW", "60"))
        except Exception:
            self._window = 60

        self._calls = deque()

    def _allow_request(self) -> bool:
        now = time.time()
        # purge old
        while self._calls and now - self._calls[0] > self._window:
            self._calls.popleft()
        return len(self._calls) < self._limit

    def _time_until_available(self) -> int:
        if not self._calls:
            return 0
        now = time.time()
        oldest = self._calls[0]
        remain = int(max(0, self._window - (now - oldest)))
        return remain

    async def ask(self, prompt: str, user_id: Optional[str] = None) -> str:
        """
        Genera una respuesta de Gemini. Aplica limitación local para evitar 429 y maneja errores con mensajes de fallback.
        """
        if not prompt or not prompt.strip():
            return "Necesito una pregunta para poder ayudarte."

        if not self._allow_request():
            wait = self._time_until_available() + 1
            logger.warning("Gemini rate limit reached (local). user=%s wait=%s", user_id, wait)
            return f"La IA está ocupada; intenta de nuevo en {wait} segundos."

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt.strip(),
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.6")),
                    top_p=float(os.getenv("GEMINI_TOP_P", "0.9")),
                    max_output_tokens=int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "700")),
                ),
            )
            # record call AFTER successful call to avoid counting failures
            self._calls.append(time.time())
            text = (response.text or "").strip()
            if not text:
                return "No pude generar una respuesta en este momento."
            return text

        except ga_errors.ClientError as e:
            # Handle rate/quota errors specifically
            logger.exception("Gemini ClientError for user=%s: %s", user_id, e)
            msg = str(e)
            # try to extract retryDelay like 'retryDelay': '28.26437971s'
            m = re.search(r"retryDelay[^\d]*(\d+\.?\d*)s", msg)
            if m:
                secs = int(float(m.group(1)))
                return f"La IA alcanzó su límite de uso. Intenta de nuevo en {secs} segundos."
            # try to detect seconds in message
            m2 = re.search(r"limit.*?(\d+)" , msg)
            if m2:
                return "La IA alcanzó su límite de uso. Intenta de nuevo en unos segundos."
            return "La IA alcanzó su límite de uso. Intenta de nuevo más tarde."

        except Exception:
            logger.exception("Error al consultar Gemini (user_id=%s).", user_id)
            return "Hubo un problema temporal con la IA. Intenta de nuevo en unos segundos."


# singleton
try:
    gemini_service = GeminiService()
except Exception as ex:
    # If init fails (missing API key), create a stub that returns friendly error
    logging.getLogger(__name__).warning("GeminiService init failed: %s", ex)

    class _Stub:
        async def ask(self, prompt: str, user_id: Optional[str] = None) -> str:
            return "Gemini no está configurado. Revisa GEMINI_API_KEY en el entorno."

    gemini_service = _Stub()
