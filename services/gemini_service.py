import os
import logging
import asyncio
from typing import Optional, List
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

logger = logging.getLogger("community_bot.gemini")

# Prompt del sistema para el asistente de comunidad
SYSTEM_INSTRUCTION = (
    "Eres un Asistente Virtual Amigable y Eficiente para servidores de Discord y grupos de Telegram "
    "de nuestra comunidad. Responde de manera clara, amable, concisa y en español. "
    "Utiliza formato Markdown cuando sea oportuno (*negrita*, _cursiva_, listas con viñetas, bloques de código). "
    "Mantén las respuestas ordenadas y al grano para facilitar la lectura en chats comunitarios."
)

FALLBACK_MESSAGE = (
    "👋 ¡Hola! En este momento no pude conectar con el servicio de IA de Google Gemini. "
    "Por favor, verifica tu `GEMINI_API_KEY` o intenta nuevamente en unos momentos."
)


class GeminiService:
    """Servicio para interactuar con la API oficial de Google Gemini (@google-genai)."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        self._client: Optional[genai.Client] = None
        self._init_client()

    def _init_client(self) -> None:
        """Inicializa el cliente de Google GenAI."""
        if not self.api_key or self.api_key == "tu_gemini_api_key_aqui":
            logger.warning("GEMINI_API_KEY no configurada. Las consultas de IA usarán respuesta de respaldo.")
            self._client = None
            return

        try:
            self._client = genai.Client(api_key=self.api_key)
            logger.info("Cliente de Google Gemini inicializado con modelo '%s'", self.model)
        except Exception as exc:
            logger.error("Error al inicializar cliente de Google GenAI: %s", exc)
            self._client = None

    def _generate_sync(self, prompt: str, user_name: Optional[str] = None) -> str:
        """Llamada síncrona a la API de Gemini con reintentos automáticos."""
        if not self._client:
            return FALLBACK_MESSAGE

        prompt_context = f"El usuario {user_name} consulta: {prompt}" if user_name else prompt

        # Intentar hasta 3 veces en caso de sobrecarga temporal de la API
        for attempt in range(3):
            try:
                config = types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.7,
                    max_output_tokens=1000,
                )

                response = self._client.models.generate_content(
                    model=self.model,
                    contents=prompt_context,
                    config=config,
                )

                if response and response.text:
                    return response.text.strip()

                return "No se obtuvo texto de respuesta de la IA. Por favor, intenta reformular tu pregunta."

            except Exception as err:
                logger.warning("Intento %s/3 falló al consultar Gemini (%s): %s", attempt + 1, type(err).__name__, err)
                if attempt < 2:
                    import time
                    time.sleep(1.5 * (attempt + 1))
                else:
                    logger.error("Todos los intentos con Gemini fallaron.")
                    return FALLBACK_MESSAGE

    async def ask(self, prompt: str, user_name: Optional[str] = None) -> str:
        """
        Ejecuta la consulta a Gemini en un hilo asíncrono sin bloquear el bucle de eventos.
        """
        return await asyncio.to_thread(self._generate_sync, prompt, user_name)


def split_message(text: str, max_length: int = 2000) -> List[str]:
    """Divide un texto largo en fragmentos que respeten el límite de caracteres de cada plataforma."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    current_chunk = ""

    for line in text.split("\n"):
        if len(current_chunk) + len(line) + 1 > max_length:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


# Instancia singleton
gemini_service = GeminiService()


async def ask_gemini(prompt: str, user_name: Optional[str] = None) -> str:
    """Función de conveniencia para consultar Gemini."""
    return await gemini_service.ask(prompt, user_name)
