# bot.py
import sys
import os
import logging
import time
from telebot.apihelper import ApiException
from requests.exceptions import RequestException

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Añade el directorio raíz, utils y handlers al sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'utils'))
sys.path.insert(0, os.path.join(project_root, 'handlers'))

from telebot import TeleBot
from config import TELEGRAM_TOKEN
from handlers.commands import register_command_handlers
from handlers.messages import register_message_handlers
import signal

bot = TeleBot(TELEGRAM_TOKEN)

# Registrar manejadores
register_command_handlers(bot)
register_message_handlers(bot)

def run_bot_with_reconnect(bot):
    while True:
        try:
            logger.info("Iniciando el bot...")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except ApiException as e:
            logger.error(f"Error de API de Telegram: {e}")
            time.sleep(5)
        except RequestException as e:
            logger.error(f"Error de conexión: {e}")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
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
