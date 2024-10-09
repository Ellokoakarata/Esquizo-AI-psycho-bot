# utils/error_handling.py
import logging
import traceback
import random
from config import ADMIN_CHAT_ID
from functools import wraps

# Configurar el logging
logging.basicConfig(filename='bot_errors.log', level=logging.ERROR)

def send_error_to_admin(bot, error_message):
    """Envía un mensaje de error al administrador."""
    error_prefixes = [
        "¡Ups! Parece que mi cerebro cibernético tuvo un cortocircuito:",
        "Error en la matriz neuronal:",
        "Glitch en el sistema caótico:",
        "Fragmentación inesperada en el flujo de datos:",
        "Delirio detectado en el núcleo de procesamiento:"
    ]
    safe_error_message = f"{random.choice(error_prefixes)}\n{error_message}"
    if ADMIN_CHAT_ID:
        try:
            bot.send_message(ADMIN_CHAT_ID, safe_error_message)
        except Exception as e:
            print(f"No se pudo enviar el mensaje de error al administrador: {e}")

def handle_error(bot):
    """Decorador para manejar errores en los handlers del bot."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error en {func.__name__}: {e}")
                chat_id = args[0].chat.id if args and hasattr(args[0], 'chat') else None
                if chat_id:
                    bot.send_message(chat_id, "Oops, algo salió mal. Estoy trabajando para solucionarlo. Por favor, intenta de nuevo más tarde.")
        return wrapper
    return decorator
