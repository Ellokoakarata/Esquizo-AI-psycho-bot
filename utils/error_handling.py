# utils/error_handling.py
import logging
import traceback
import random
import re
from config import ADMIN_CHAT_ID
from functools import wraps

# Obtener el logger
logger = logging.getLogger(__name__)

def sanitize_error_message(error_message, sensitive_data):
    """Sanitiza el mensaje de error eliminando datos sensibles."""
    sanitized_message = error_message
    for data in sensitive_data:
        sanitized_message = sanitized_message.replace(data, '[DATO_SENSIBLE]')
    return sanitized_message

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
            logger.error(f"No se pudo enviar el mensaje de error al administrador: {e}", exc_info=True)

def handle_error(bot):
    """Decorador para manejar errores en los handlers del bot."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Registrar el error sin incluir información sensible
                logger.error(f"Error en {func.__name__}", exc_info=True)
                chat_id = args[0].chat.id if args and hasattr(args[0], 'chat') else None
                if chat_id:
                    bot.send_message(chat_id, "Oops, algo salió mal. Estoy trabajando para solucionarlo. Por favor, intenta de nuevo más tarde.")
                # Preparar y enviar el mensaje de error al administrador
                error_message = f"Error en {func.__name__}: {type(e).__name__}"
                # Sanitizar el mensaje de error si es necesario
                sensitive_data = [bot.token]  # Añade otros datos sensibles si es necesario
                sanitized_message = sanitize_error_message(error_message, sensitive_data)
                send_error_to_admin(bot, sanitized_message)
        return wrapper
    return decorator
