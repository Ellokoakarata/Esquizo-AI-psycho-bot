# config.py
import os

# Variables de entorno
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")

# Definir CONVERSATION_DIR
CONVERSATION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conversation_logs')

# Asegurarse de que el directorio existe
if not os.path.exists(CONVERSATION_DIR):
    os.makedirs(CONVERSATION_DIR)

# Verificar si las variables de entorno están configuradas
if not TELEGRAM_TOKEN:
    raise ValueError("La variable de entorno TELEGRAM_TOKEN no está configurada.")

if not GROQ_API_KEY and not GOOGLE_API_KEY:
    raise ValueError("Debe configurar al menos una de las claves GROQ_API_KEY o GOOGLE_API_KEY.")

if ADMIN_CHAT_ID:
    try:
        ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)
    except ValueError:
        raise ValueError("ADMIN_CHAT_ID debe ser un número entero válido.")
else:
    ADMIN_CHAT_ID = None
