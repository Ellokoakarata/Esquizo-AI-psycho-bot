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
            user_name = message.from_user.first_name or "Unknown User"
            user_username = message.from_user.username or "No username"
            
            logger.info(f"Message received from {user_name} (ID: {user_id}): {message.text}")
            
            # Load user history
            history = ConversationHistory(user_id)
            history.add_message("user", message.text, user_username)
            history.save_history()
            logger.info(f"History updated for user {user_id}")

            # Summarize recent context
            recent_messages = history.get_recent_messages(3)  # Only get the last 3 messages
            summarized_context = summarize_messages(recent_messages)
            logger.info(f"Summarized context: {len(recent_messages)} messages")

            # Determine if we should use the meta_prompt
            use_meta_prompt = history.history.get('use_meta_prompt', False)

            if not use_meta_prompt:
                open_keywords = ["reason", "structure", "use your meta_prompt"]
                if any(keyword in message.text.lower() for keyword in open_keywords):
                    history.history['use_meta_prompt'] = True
                    history.save_history()
                    logger.info("Meta_prompt activated")
            else:
                close_keywords = ["stop using meta_prompt"]
                if any(keyword in message.text.lower() for keyword in close_keywords):
                    history.history['use_meta_prompt'] = False
                    history.save_history()
                    logger.info("Meta_prompt deactivated")

            # Define which prompts to load based on current state
            system_message_path = 'prompts/system.txt'  # Always include the system prompt
            template_path = 'prompts/prompt_template.txt'
            meta_prompt_path = 'prompts/meta_prompt_caotico_visceral (1).md' if history.history.get('use_meta_prompt') else None
            rebel_path = 'prompts/rebel.json' if "rebel" in message.text.lower() else None
            rebel2_path = 'prompts/rebel_v2.json' if "rebel" in message.text.lower() else None

            # Create the prompt dynamically, loading only required files
            prompt_builder = PromptBuilder(
                meta_prompt_path=meta_prompt_path,
                system_message_path=system_message_path,
                template_path=template_path,
                rebel_path=rebel_path,
                rebel2_path=rebel2_path
            )

            # Build the internal prompt using both system and internal context
            internal_prompt = prompt_builder.build_prompt(
                summarized_context=summarized_context,
                user_name=user_name,
                user_username=user_username,
                user_message=message.text
            )
            logger.info("Internal prompt constructed")

            # Combine system_prompt and internal_prompt
            full_prompt = f"{open(system_message_path).read()}\n{internal_prompt}"

            # Select the model
            selected_model = history.history.get('model', 'groq')
            logger.info(f"Selected model: {selected_model}")

            # Generate response based on selected model
            if selected_model == 'groq' and GROQ_API_KEY:
                logger.info("Generating response with Groq")
                reply_content = generate_groq_response(full_prompt, history)
            elif selected_model == 'google' and GOOGLE_API_KEY:
                logger.info("Generating response with Google")
                reply_content = generate_google_response(full_prompt, history)
            else:
                logger.warning("No available model to generate a response")
                reply_content = "No model available to generate a response."

            # Send the response
            if reply_content:
                success = send_message_with_retries(bot, message.chat.id, reply_content)
                if success:
                    history.add_message("assistant", reply_content)
                    history.save_history()
                    logger.info(f"Response generated and saved: {reply_content[:50]}...")
                else:
                    logger.error("Failed to send message to the user after multiple attempts.")
            else:
                logger.warning("Unable to generate a clear response")
                send_message_with_retries(bot, message.chat.id, "No clear response. Chaos is odd today.")

            logger.info("Message processing completed")

        except Exception as e:
            logger.error(f"Error processing the message: {e}", exc_info=True)
            send_message_with_retries(bot, message.chat.id, "Sorry, I am experiencing some technical difficulties. Please try again later.")

    def send_message_with_retries(bot, chat_id, text, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:
                bot.send_message(chat_id, text)
                return True  # Message successfully sent
            except (ConnectionError, ReadTimeout, ProtocolError, RemoteDisconnected, apihelper.ApiException) as e:
                retries += 1
                wait_time = 2 ** retries  # Exponential backoff
                logger.warning(f"Error sending message: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            except Exception as e:
                logger.error(f"Unknown error sending message: {e}", exc_info=True)
                break
        logger.error("Failed to send the message after several attempts.")
        return False

