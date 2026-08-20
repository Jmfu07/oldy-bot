import os
import logging
from typing import Optional

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Cliente unificado para Google Gemini.
    Configura el modelo gemini-2.5-flash con instrucciones de sistema.
    """

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Falta GEMINI_API_KEY en variables de entorno.")

        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = genai.Client(api_key=api_key)
        self.system_instruction = (
            "Eres un asistente amable y claro para comunidades online. "
            "Responde en español neutro, con tono respetuoso, breve y útil. "
            "Si no sabes algo, dilo con honestidad y sugiere un siguiente paso."
        )

    async def ask(self, prompt: str, user_id: Optional[str] = None) -> str:
        """
        Genera una respuesta de Gemini para el texto recibido.
        """
        if not prompt or not prompt.strip():
            return "Necesito una pregunta para poder ayudarte."

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt.strip(),
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.6,
                    top_p=0.9,
                    max_output_tokens=700,
                ),
            )
            text = (response.text or "").strip()
            if not text:
                return "No pude generar una respuesta en este momento."
            return text
        except Exception:
            logger.exception("Error al consultar Gemini (user_id=%s).", user_id)
            return "Hubo un problema temporal con la IA. Intenta de nuevo en unos segundos."


gemini_service = GeminiService()
