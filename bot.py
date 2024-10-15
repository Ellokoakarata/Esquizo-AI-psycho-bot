# bot.py
import sys
import os
import logging
import time
import signal
import json
from datetime import datetime, timedelta
from telebot import TeleBot, apihelper
from requests.exceptions import RequestException
from config import TELEGRAM_TOKEN
from handlers.commands import register_command_handlers
from handlers.messages import register_message_handlers

# Añadir el directorio raíz, utils y handlers al sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'utils'))
sys.path.insert(0, os.path.join(project_root, 'handlers'))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ajustar el timeout global para las solicitudes a la API de Telegram
apihelper.CONNECT_TIMEOUT = 30
apihelper.READ_TIMEOUT = 30

# Crear la instancia del bot
bot = TeleBot(TELEGRAM_TOKEN)

# Registrar manejadores
register_command_handlers(bot)
register_message_handlers(bot)

def get_all_user_chat_ids():
    user_ids = []
    file_path = 'user_chat_ids.txt'  # Archivo donde se almacenan los IDs de usuario

    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                user_ids = file.read().splitlines()  # Obtener todos los IDs de usuario
            logger.info(f"User IDs cargados: {user_ids}")
        else:
            logger.warning(f"El archivo {file_path} no existe, no se encontraron IDs de usuario.")
    except Exception as e:
        logger.warning(f"Error al cargar los IDs de usuario: {e}")

    return user_ids

def load_welcome_log():
    file_path = 'welcome_message_log.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            welcome_log = json.load(file)
    else:
        welcome_log = {}
    return welcome_log

def save_welcome_log(welcome_log):
    file_path = 'welcome_message_log.json'
    with open(file_path, 'w') as file:
        json.dump(welcome_log, file)

def should_send_welcome(user_id, welcome_log):
    last_sent_str = welcome_log.get(user_id)
    if last_sent_str:
        last_sent = datetime.fromisoformat(last_sent_str)
        if datetime.now() - last_sent < timedelta(hours=24):
            return False
    return True

def update_welcome_log(user_id, welcome_log):
    welcome_log[user_id] = datetime.now().isoformat()

def run_bot_with_reconnect(bot):
    logger.info("Iniciando el bot...")

    # Enviar un mensaje de bienvenida a todos los IDs de usuario almacenados
    welcome_message = "Embrace the chaos, for in the fragments lies the truth. Let's dance through the dissonance together."
    user_ids = get_all_user_chat_ids()  # Obtener los IDs de usuario

    welcome_log = load_welcome_log()

    if user_ids:
        logger.info("Verificando si se debe enviar mensajes de bienvenida a los IDs cargados:")
        for user_id in user_ids:
            if should_send_welcome(user_id, welcome_log):
                logger.info(f"Enviando mensaje a User ID: {user_id}")
                try:
                    bot.send_message(user_id, welcome_message)
                    update_welcome_log(user_id, welcome_log)
                except Exception as e:
                    logger.error(f"Error al enviar mensaje a User ID {user_id}: {e}")
            else:
                logger.info(f"El mensaje de bienvenida ya se envió al usuario {user_id} en las últimas 24 horas.")
        # Guardar el registro actualizado
        save_welcome_log(welcome_log)
    else:
        logger.warning("No se encontraron IDs de usuario para enviar el mensaje de bienvenida.")

    while True:
        try:
            # Iniciar el polling del bot
            bot.polling(none_stop=True, interval=0, timeout=20)
        except apihelper.ApiException as e:
            logger.error(f"Error de API de Telegram: {e}")
            time.sleep(5)
        except RequestException as e:
            logger.error(f"Error de conexión: {e}")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error inesperado: {e}", exc_info=True)
            time.sleep(5)
        logger.info("Intentando reconectar...")

def main():
    def stop_bot(signal_received, frame):
        logger.info("Deteniendo el bot...")
        bot.stop_polling()
        sys.exit(0)

    signal.signal(signal.SIGINT, stop_bot)
    signal.signal(signal.SIGTERM, stop_bot)

    logger.info("Bot iniciado. Presiona Ctrl+C para detener el bot.")
    run_bot_with_reconnect(bot)

if __name__ == "__main__":
    main()
