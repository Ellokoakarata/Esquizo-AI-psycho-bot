# handlers/messages.py
import logging
from telebot import TeleBot
from utils.error_handling import handle_error
from utils.history import ConversationHistory
from utils.prompts import PromptBuilder
from utils.voice import text_to_voice
from utils import summarize_messages
from models.groq_model import generate_groq_response
from models.google_model import generate_google_response
from config import GOOGLE_API_KEY, GROQ_API_KEY
import os

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
            logger.info(f"Contexto resumido: {len(summarized_context)} mensajes")

            # Construir el prompt
            prompt_builder = PromptBuilder(
                meta_prompt_path='prompts/meta_prompt_caotico_visceral (1).md',
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
                reply_content = generate_groq_response(internal_prompt)
            elif modelo_seleccionado == 'google' and GOOGLE_API_KEY:
                logger.info("Generando respuesta con Google")
                reply_content = generate_google_response(internal_prompt, history)
            else:
                logger.warning("No hay un modelo disponible para generar una respuesta")
                reply_content = "No hay un modelo disponible para generar una respuesta."

            if reply_content:
                history.add_message("assistant", reply_content)
                history.save_history()
                logger.info(f"Respuesta generada y guardada: {reply_content[:50]}...")
                bot.reply_to(message, reply_content)
            else:
                logger.warning("No se pudo generar una respuesta clara")
                bot.reply_to(message, "No tengo una respuesta clara. El caos es extraño hoy.")

            logger.info("Procesamiento del mensaje completado")

        except Exception as e:
            logger.error(f"Error al procesar el mensaje: {e}")
            bot.reply_to(message, "Lo siento, estoy experimentando algunas dificultades técnicas. Estoy trabajando para resolverlas. Por favor, intenta de nuevo más tarde.")
            
        finally:
            logger.info("Procesamiento del mensaje completado")
