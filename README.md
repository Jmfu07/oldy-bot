# 🤖 Bot Híbrido de Comunidad (Discord + Telegram + Google Gemini)

Un bot unificado, modular y robusto escrito 100% en Python, diseñado para gestionar comunidades y servidores en **Discord** y grupos en **Telegram** de forma simultánea, potenciado por la Inteligencia Artificial de **Google Gemini (`google-genai`)** y listo para despliegue **24/7 gratuito en Render**.

---

## 🌟 Características Principales

- **Arquitectura Modular por Categorías**:
  - `commands/general/`: Comandos informativos (`/reglas`, `/ayuda`).
  - `commands/moderacion/`: Herramientas de administración (`/limpiar`, `/aviso`).
  - `commands/ia/`: Consultas con IA (`/ia <pregunta>`) y respuestas automáticas al mencionar al bot (`@Bot`).
- **Google Gemini Integrado (`@google-genai`)**:
  - Respuestas inteligentes, amigables y formateadas en Markdown adaptadas a chats comunitarios.
  - Ejecución asíncrona no bloqueante con control automático de límites de caracteres.
- **Doble Plataforma Simultánea**:
  - Ejecuta Discord y Telegram en paralelo dentro del mismo proceso utilizando `asyncio`.
- **Listo para Render 24/7**:
  - Incluye `Procfile` configurado para Background Worker.

---

## 📁 Estructura del Proyecto

```text
mi_bot_comunidad/
├── commands/
│   ├── general/
│   │   ├── __init__.py
│   │   ├── reglas.py      # Comando /reglas
│   │   └── ayuda.py       # Comando /ayuda
│   ├── moderacion/
│   │   ├── __init__.py
│   │   └── moderacion.py  # Comandos de moderación (/limpiar, /aviso)
│   └── ia/
│       ├── __init__.py
│       └── ia.py          # Comando /ia y respuestas por mención
├── services/
│   ├── __init__.py
│   └── gemini_service.py  # Cliente oficial de Google Gemini
├── .env.example           # Plantilla de variables de entorno
├── .env                   # Variables locales
├── requirements.txt       # Dependencias del proyecto
├── pyproject.toml         # Configuración de uv / pip
├── Procfile               # Definición del worker para Render ('worker: python main.py')
├── README.md              # Documentación
└── main.py                # Cargador dinámico y ejecutor dual
```

---

## 🔑 Obtención de Tokens y Credenciales

### 1. Google Gemini API Key (Gratis)
1. Ve a **[Google AI Studio](https://aistudio.google.com/)**.
2. Inicia sesión con tu cuenta de Google y haz clic en **"Get API key"** > **"Create API key"**.
3. Cópiala en tu variable `GEMINI_API_KEY`.

### 2. Telegram Bot Token (30 Segundos)
1. Abre Telegram y busca al bot oficial: **[@BotFather](https://t.me/BotFather)**.
2. Envía el comando `/newbot` y sigue las instrucciones para elegir nombre y usuario.
3. BotFather te dará un Token (ej: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).
4. Cópialo en `TELEGRAM_TOKEN`.
5. *(Opcional)* En BotFather envía `/setprivacy` > Elige tu bot > Selecciona **"Disable"** para que el bot pueda leer mensajes en grupos cuando lo etiqueten.

### 3. Discord Bot Token
1. Entra a **[Discord Developer Portal](https://discord.com/developers/applications)**.
2. Haz clic en **"New Application"**, ponle un nombre y ve a la pestaña **"Bot"**.
3. Haz clic en **"Reset Token"** / **"Copy"** para obtener el `DISCORD_TOKEN`.
4. En esa misma pestaña activa los **Privileged Gateway Intents**:
   - ✅ **Message Content Intent** (Obligatorio para leer mensajes y menciones).
   - ✅ **Server Members Intent**.
5. Para invitar el bot a tu servidor: Ve a **OAuth2** > **URL Generator** > Selecciona `bot` y `applications.commands` con permisos de Administrador o Gestión de Mensajes, copia el enlace generado y ábrelo en tu navegador.

---

## 💻 Ejecución Local

### 1. Instalar dependencias
En una terminal en la carpeta del proyecto:
```powershell
cd C:\Users\nubma\OneDrive\Desktop\mi_bot_comunidad
pip install -r requirements.txt
```
*(O si usas uv: `uv sync` o `uv run python main.py`)*

### 2. Configurar variables en `.env`
Edita el archivo `.env`:
```ini
DISCORD_TOKEN=tu_discord_token_aqui
DISCORD_PREFIX=!
TELEGRAM_TOKEN=tu_telegram_token_aqui
GEMINI_API_KEY=tu_gemini_api_key_aqui
GEMINI_MODEL=gemini-3.6-flash
```

### 3. Iniciar los bots
```powershell
python main.py
```

---

## ☁️ Guía Paso a Paso: Despliegue Gratis 24/7 en Render

[Render](https://render.com/) permite alojar bots de Discord y Telegram de forma continua sin costo en su plan gratuito.

### Paso 1: Subir el proyecto a GitHub
1. Abre una terminal en la carpeta del proyecto:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Bot de Comunidad Discord & Telegram"
   ```
2. Crea un repositorio **Privado** en [GitHub](https://github.com/new).
3. Conecta y sube tu código:
   ```bash
   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   git branch -M main
   git push -u origin main
   ```

### Paso 2: Crear el servicio en Render
1. Inicia sesión en **[Render.com](https://render.com/)**.
2. En el Dashboard, haz clic en **"New +"** y selecciona **"Background Worker"**.
3. Conecta tu cuenta de GitHub y selecciona tu repositorio.
4. Configura los datos del servicio:
   - **Name**: `mi-bot-comunidad`
   - **Region**: La más cercana (ej: `Oregon` o `Frankfurt`).
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py` (o se detectará automáticamente por el `Procfile`).
   - **Instance Type**: `Free`

### Paso 3: Configurar Variables de Entorno en Render
En la pestaña **Environment Variables** de tu servicio en Render, agrega:
- `DISCORD_TOKEN` = *(Tu token de Discord)*
- `TELEGRAM_TOKEN` = *(Tu token de Telegram)*
- `GEMINI_API_KEY` = *(Tu API Key de Google Gemini)*
- `GEMINI_MODEL` = `gemini-3.6-flash`
- `DISCORD_PREFIX` = `!`

### Paso 4: ¡Desplegar!
Haz clic en **"Create Background Worker"**. Render construirá el entorno e iniciará tus bots. En la pestaña **Logs** verás cómo ambos bots se conectan y quedan activos **24 horas al día, 7 días a la semana**. 🚀
