#bot.py
import sys
import os
import logging
import time
import signal
from telebot import TeleBot, apihelper
from requests.exceptions import RequestException
from config import TELEGRAM_TOKEN
from handlers.commands import register_command_handlers
from handlers.messages import register_message_handlers
from utils.history import ConversationHistory

# Añadir el directorio raíz, utils y handlers al sys.path para poder importar módulos correctamente
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'utils'))
sys.path.insert(0, os.path.join(project_root, 'handlers'))

# Configurar logging para mostrar mensajes de información y errores
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ajustar el timeout global para las solicitudes a la API de Telegram
apihelper.CONNECT_TIMEOUT = 30  # Puedes ajustar este valor según tus necesidades
apihelper.READ_TIMEOUT = 30

# Crear la instancia del bot con el token de Telegram
bot = TeleBot(TELEGRAM_TOKEN)

# Registrar los manejadores de comandos y mensajes del bot
register_command_handlers(bot)
register_message_handlers(bot)

# Función para obtener todos los IDs de los chats almacenados
def get_all_user_chat_ids():
    chat_ids = []
    file_path = 'user_chat_ids.txt'  # Archivo donde se almacenan los IDs de usuario
    
    try:
        # Verificar si el archivo con los IDs de usuario existe
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                chat_ids = file.read().splitlines()  # Obtener todos los IDs de chat
            logger.info(f"Chat IDs cargados: {chat_ids}")  # Log para mostrar los IDs cargados
        else:
            logger.warning(f"El archivo {file_path} no existe, no se encontraron IDs de usuario.")
    except Exception as e:
        logger.warning(f"Error al cargar los IDs de chat: {e}")
    
    return chat_ids

# Función para ejecutar el bot con reconexiones automáticas en caso de error
def run_bot_with_reconnect(bot):
    logger.info("Iniciando el bot...")
    
    # Enviar un mensaje de bienvenida a todos los IDs de chat almacenados
    welcome_message = "Embrace the chaos, for in the fragments lies the truth. Let's dance through the dissonance together."
    chat_ids = get_all_user_chat_ids()  # Obtener los IDs de chat
    
    if chat_ids:
        logger.info("Enviando mensajes de bienvenida a los IDs cargados:")
        for chat_id in chat_ids:
            logger.info(f"Enviando mensaje a ID: {chat_id}")  # Imprimir cada ID cargado
            bot.send_message(chat_id, welcome_message)
    else:
        logger.warning("No se encontraron IDs de usuario para enviar el mensaje de bienvenida.")
    
    while True:
        try:
            # Iniciar el polling del bot (escuchar mensajes continuamente)
            bot.polling(none_stop=True, interval=0, timeout=20)
                    
        except apihelper.ApiException as e:
            logger.error(f"Error de API de Telegram: {e}")
            time.sleep(5)  # Esperar 5 segundos antes de intentar reconectar
        except RequestException as e:
            logger.error(f"Error de conexión: {e}")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error inesperado: {e}", exc_info=True)
            time.sleep(5)
        
        logger.info("Intentando reconectar...")

# Función principal para iniciar el bot
def main():
    # Función para detener el bot de manera segura al recibir señales del sistema
    def stop_bot(signal_received, frame):
        logger.info("Deteniendo el bot...")
        bot.stop_polling()  # Detener el polling del bot
        sys.exit(0)  # Salir del programa

    # Asignar señales SIGINT (Ctrl+C) y SIGTERM para detener el bot
    signal.signal(signal.SIGINT, stop_bot)
    signal.signal(signal.SIGTERM, stop_bot)

    logger.info("Bot iniciado. Presiona Ctrl+C para detener el bot.")
    run_bot_with_reconnect(bot)  # Ejecutar el bot con reconexiones automáticas

# Punto de entrada del script
if __name__ == "__main__":
    main()
