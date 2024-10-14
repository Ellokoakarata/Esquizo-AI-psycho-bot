# handlers/messages.py
import logging
import time
import os
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

# Registrar los manejadores de mensajes del bot
def register_message_handlers(bot: TeleBot):
    @handle_error(bot)
    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        try:
            # Obtener la información del usuario
            user_id = str(message.chat.id)
            user_name = message.from_user.first_name or "Usuario desconocido"
            user_username = message.from_user.username or "Sin username"
            
            logger.info(f"Mensaje recibido de {user_name} (ID: {user_id}): {message.text}")
            
            # Guardar el ID de usuario si no está ya en el archivo
            file_path = 'user_chat_ids.txt'
            
            # Leer el archivo para verificar si el ID ya existe
            if not os.path.exists(file_path):
                open(file_path, 'w').close()  # Crear el archivo si no existe

            # Leer los IDs existentes en el archivo
            with open(file_path, 'r') as file:
                existing_ids = file.read().splitlines()

            # Solo agregar el ID si no está en el archivo
            if user_id not in existing_ids:
                with open(file_path, 'a') as file:
                    file.write(user_id + '\n')
                logger.info(f"El ID de usuario {user_id} ha sido guardado.")
            else:
                logger.info(f"El ID de usuario {user_id} ya existe, no se guardará de nuevo.")

            # Cargar el historial de usuario
            history = ConversationHistory(user_id)
            # Agregar el mensaje del usuario al historial
            history.add_message("user", message.text, user_username, chat_id=message.chat.id)
            history.save_history()
            logger.info(f"Historial actualizado para el usuario {user_id}")

            # Resumir el contexto reciente (últimos 3 mensajes)
            recent_messages = history.get_recent_messages(3)
            summarized_context = summarize_messages(recent_messages)
            logger.info(f"Contexto resumido: {len(recent_messages)} mensajes")

            # Determinar si se debe usar el meta_prompt
            use_meta_prompt = history.history.get('use_meta_prompt', False)

            if not use_meta_prompt:
                # Activar el uso del meta_prompt si se encuentran las palabras clave
                open_keywords = ["reason", "structure", "use your meta_prompt"]
                if any(keyword in message.text.lower() for keyword in open_keywords):
                    history.history['use_meta_prompt'] = True
                    history.save_history()
                    logger.info("Meta_prompt activado")
            else:
                # Desactivar el uso del meta_prompt si se encuentran las palabras clave
                close_keywords = ["stop using meta_prompt"]
                if any(keyword in message.text.lower() for keyword in close_keywords):
                    history.history['use_meta_prompt'] = False
                    history.save_history()
                    logger.info("Meta_prompt desactivado")

            # Definir qué prompts cargar según el estado actual
            system_message_path = 'prompts/system.txt'  # Incluir siempre el system prompt
            template_path = 'prompts/prompt_template.txt'
            meta_prompt_path = 'prompts/meta_prompt_caotico_visceral (1).md' if history.history.get('use_meta_prompt') else None
            rebel_path = 'prompts/rebel.json' if "rebel" in message.text.lower() else None
            rebel2_path = 'prompts/rebel_v2.json' if "rebel" in message.text.lower() else None

            # Crear el prompt de forma dinámica, cargando solo los archivos necesarios
            prompt_builder = PromptBuilder(
                meta_prompt_path=meta_prompt_path,
                system_message_path=system_message_path,
                template_path=template_path,
                rebel_path=rebel_path,
                rebel2_path=rebel2_path
            )

            # Construir el prompt interno usando el contexto resumido y los datos del usuario
            internal_prompt = prompt_builder.build_prompt(
                summarized_context=summarized_context,
                user_name=user_name,
                user_username=user_username,
                user_message=message.text
            )
            logger.info("Prompt interno construido")

            # Combinar el system_prompt y el internal_prompt
            full_prompt = f"{open(system_message_path).read()}\n{internal_prompt}"

            # Seleccionar el modelo
            selected_model = history.history.get('model', 'groq')
            logger.info(f"Modelo seleccionado: {selected_model}")

            # Generar la respuesta basada en el modelo seleccionado
            if selected_model == 'groq' and GROQ_API_KEY:
                logger.info("Generando respuesta con Groq")
                reply_content = generate_groq_response(full_prompt, history)
            elif selected_model == 'google' and GOOGLE_API_KEY:
                logger.info("Generando respuesta con Google")
                reply_content = generate_google_response(full_prompt, history)
            else:
                logger.warning("No hay un modelo disponible para generar una respuesta")
                reply_content = "No hay un modelo disponible para generar una respuesta."

            # Enviar la respuesta
            if reply_content:
                success = send_message_with_retries(bot, message.chat.id, reply_content)
                if success:
                    # Guardar la respuesta en el historial
                    history.add_message("assistant", reply_content)
                    history.save_history()
                    logger.info(f"Respuesta generada y guardada: {reply_content[:50]}...")
                else:
                    logger.error("No se pudo enviar el mensaje al usuario después de varios intentos.")
            else:
                logger.warning("No se pudo generar una respuesta clara")
                send_message_with_retries(bot, message.chat.id, "No tengo una respuesta clara. Hoy el caos es extraño.")

            logger.info("Procesamiento del mensaje completado")

        except Exception as e:
            logger.error(f"Error al procesar el mensaje: {e}", exc_info=True)
            send_message_with_retries(bot, message.chat.id, "Lo siento, estoy experimentando dificultades técnicas. Por favor, intenta de nuevo más tarde.")

    # Función para enviar el mensaje con reintentos en caso de error
    def send_message_with_retries(bot, chat_id, text, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:
                bot.send_message(chat_id, text)
                return True  # Mensaje enviado con éxito
            except (ConnectionError, ReadTimeout, ProtocolError, RemoteDisconnected, apihelper.ApiException) as e:
                retries += 1
                wait_time = 2 ** retries  # Backoff exponencial
                logger.warning(f"Error al enviar mensaje: {e}. Reintentando en {wait_time} segundos...")
                time.sleep(wait_time)
            except Exception as e:
                logger.error(f"Error desconocido al enviar el mensaje: {e}", exc_info=True)
                break
        logger.error("No se pudo enviar el mensaje después de varios intentos.")
        return False