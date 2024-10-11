# handlers/messages.py
import logging
import time
from telebot import TeleBot, apihelper
from utils.error_handling import handle_error
from utils.history import ConversationHistory
from utils.prompts import PromptBuilder
from utils.voice import text_to_voice
from utils import summarize_messages
from models.groq_model import generate_groq_response
from models.google_model import generate_google_response
from config import GOOGLE_API_KEY, GROQ_API_KEY
from requests.exceptions import ConnectionError, ReadTimeout
from urllib3.exceptions import ProtocolError
from http.client import RemoteDisconnected  # Importación corregida

# Configurar logging
logger = logging.getLogger(__name__)

# Registrar mensaje del bot
def register_message_handlers(bot: TeleBot):
    @handle_error(bot)
    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        try:
            user_id = str(message.chat.id)
            user_name = message.from_user.first_name or "Usuario desconocido"
            user_username = message.from_user.username or "Sin username"

            logger.info(f"Mensaje recibido de {user_name} (ID: {user_id}): {message.text}")

            history = ConversationHistory(user_id)
            history.add_message("user", message.text, user_username)
            history.save_history()
            logger.info(f"Historial actualizado para el usuario {user_id}")

            # Resumir el contexto
            relevant_messages = history.history['messages'][-5:]
            summarized_context = summarize_messages(relevant_messages)
            logger.info(f"Contexto resumido: {len(relevant_messages)} mensajes")

            # Palabras clave para abrir o cerrar el archivo
            open_keywords = ["razón", "razonar", "estructura", "utiliza tu meta_prompt_caotico_visceral"]
            close_keywords = ["deja de usar el meta_prompt_caotico_visceral"]

            # Chequeo dinámico para abrir el archivo
            should_use_meta_prompt = False
            if any(keyword in message.text.lower() for keyword in open_keywords):
                history.history['use_meta_prompt'] = True  # Marcar que se debe usar el meta prompt
                logger.info("Se activó el uso de meta_prompt_caotico_visceral (1).md")

            # Chequeo dinámico para cerrar el archivo
            if any(keyword in message.text.lower() for keyword in close_keywords):
                history.history['use_meta_prompt'] = False  # Marcar que se debe dejar de usar el meta prompt
                logger.info("Se desactivó el uso de meta_prompt_caotico_visceral (1).md")

            # Determinar si se debe usar el archivo meta_prompt_caotico_visceral (1).md
            use_meta_prompt = history.history.get('use_meta_prompt', False)
            meta_prompt_path = 'prompts/meta_prompt_caotico_visceral (1).md' if use_meta_prompt else None

            # Construir el prompt
            prompt_builder = PromptBuilder(
                meta_prompt_path=meta_prompt_path,  # Solo se carga si se necesita
                system_message_path='prompts/system.txt',
                template_path='prompts/prompt_template.txt',
                rebel_path='prompts/rebel.json',
                rebel2_path='prompts/rebel_v2.json'
            )

            internal_prompt = prompt_builder.build_prompt(
                summarized_context=summarized_context,
                user_name=user_name,
                user_username=user_username,
                user_message=message.text
            )
            logger.info("Prompt interno construido")

            modelo_seleccionado = history.history.get('model', 'groq')
            logger.info(f"Modelo seleccionado: {modelo_seleccionado}")

            if modelo_seleccionado == 'groq' and GROQ_API_KEY:
                logger.info("Generando respuesta con Groq")
                reply_content = generate_groq_response(internal_prompt, history)
            elif modelo_seleccionado == 'google' and GOOGLE_API_KEY:
                logger.info("Generando respuesta con Google")
                reply_content = generate_google_response(internal_prompt, history)
            else:
                logger.warning("No hay un modelo disponible para generar una respuesta")
                reply_content = "No hay un modelo disponible para generar una respuesta."

            if reply_content:
                success = send_message_with_retries(bot, message.chat.id, reply_content)
                if success:
                    history.add_message("assistant", reply_content)
                    history.save_history()
                    logger.info(f"Respuesta generada y guardada: {reply_content[:50]}...")
                else:
                    logger.error("No se pudo enviar el mensaje al usuario después de varios intentos.")
            else:
                logger.warning("No se pudo generar una respuesta clara")
                send_message_with_retries(bot, message.chat.id, "No tengo una respuesta clara. El caos es extraño hoy.")

            logger.info("Procesamiento del mensaje completado")

        except Exception as e:
            logger.error(f"Error al procesar el mensaje: {e}", exc_info=True)
            send_message_with_retries(bot, message.chat.id, "Lo siento, estoy experimentando algunas dificultades técnicas. Por favor, intenta de nuevo más tarde.")

    def send_message_with_retries(bot, chat_id, text, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:
                bot.send_message(chat_id, text)
                return True  # Mensaje enviado con éxito
            except (ConnectionError, ReadTimeout, ProtocolError, RemoteDisconnected, apihelper.ApiException) as e:
                retries += 1
                wait_time = 2 ** retries  # Exponencial backoff
                logger.warning(f"Error al enviar mensaje: {e}. Reintentando en {wait_time} segundos...")
                time.sleep(wait_time)
            except Exception as e:
                logger.error(f"Error desconocido al enviar mensaje: {e}", exc_info=True)
                break
        logger.error("No se pudo enviar el mensaje después de varios intentos.")
        return False
